#!/usr/bin/env python3
"""voice-guard: your voice pass, run before every post.

repro-check, plan-check and pr-precheck each read voice-guide.md and hold
your outgoing drafts against your own rules, quoting the rule a draft
breaks. This checker runs the SAME pass (one canonical guide, one
contract, the same quoted-rule output) as a Claude Code PreToolUse hook,
so it fires on every outgoing `gh issue comment` / `gh pr comment` /
`gh issue create` / `gh pr create` body by construction, instead of when
someone remembers to invoke a skill.

Two modes, one contract:

  hook mode (no arguments): invoked by Claude Code with the tool-call
    JSON on stdin (see hooks/hooks.json). Commands that carry no
    outgoing body pass through untouched and cost nothing. An
    outgoing command has its body checked against your voice guide: a
    clean draft posts; a draft that breaks a rule is stopped with the
    exact rule quoted (exit 2).

  manual mode (--draft FILE): the same check on a draft file, for
    comments you will post from the browser. Prints the verdict.
    Exit 0 on pass, 2 on stop.

Your voice guide is ~/.claude/better-oss/voice-guide.md (or under
$BETTER_OSS_HOME). If you have none yet, the shipped example guide is
used, and each pass says so until you make the guide your own.

Every check appends one dated line to guard-log.md in your better-oss
folder. That log is your guard transcript.

The guard checks voice rules only; it never judges the technical content
of what you post.

Honesty note: the guard checks commands it can read. Posting from a
bare terminal, or through a command form it does not parse (a raw
`gh api` POST), walks around it, exactly like not running a skill. It
is a check on your own words, not a security system; what it adds
is that inside Claude Code, where you work, the check always runs.
"""

import argparse
import datetime
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths  # noqa: E402

# Model pin: the rubrics and this pass were built and checked on Sonnet,
# so the pass bar only holds there. Do not add a model flag.
MODEL = "sonnet"

LOG_PATH = paths.DATA_DIR / "guard-log.md"

EXAMPLE_NOTE = ("NOTE: this check used the shipped EXAMPLE voice guide, not "
                "yours. Copy defaults/voice-guide.md to "
                "~/.claude/better-oss/voice-guide.md (/better-oss:init "
                "does this), rewrite it, and delete its EXAMPLE comment.")

PROMPT = """You are the voice guard: the same voice pass repro-check's voice check
runs, now checking every post before it goes up. Below are (1) the author's voice
guide, their own rules for how they write upstream, with wrong/right
pairs and a list of things they never post, and (2) a draft comment
about to be posted publicly under their name.

Hold the draft against each rule in the guide, and against the
never-post list. Voice rules only: do not judge technical content,
facts, or general etiquette; a rule that exists only as an unfilled
template slot binds nothing. If no written rule is broken, the draft
passes.

After a short line per rule checked, output a fenced JSON block,
last, in exactly one of these forms:

{"verdict": "pass"}
{"verdict": "stop", "rule": "<the exact rule text, quoted verbatim from the guide>", "where": "<the draft line that breaks it>"}

=== THE VOICE GUIDE ===
%s

=== THE DRAFT ===
%s
"""


def guide_is_filled(text: str) -> bool:
    """A guide with only template scaffolding binds nothing: strip
    comments, headings, and blanks, and require real content."""
    stripped = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = [ln.strip() for ln in stripped.splitlines()]
    substantive = [ln for ln in lines if ln and not ln.startswith("#")]
    return len(substantive) >= 3


_OUTGOING = {("issue", "comment"), ("pr", "comment"),
             ("issue", "create"), ("pr", "create")}


def find_comment_command(tokens: list[str]):
    """Return the index after an outgoing-body gh command
    ('gh issue|pr comment|create'), or None if the command line
    sends nothing out."""
    for j in range(len(tokens) - 2):
        if tokens[j] == "gh" and (tokens[j + 1], tokens[j + 2]) in _OUTGOING:
            return j + 3
    return None


def command_cwd(tokens: list[str], upto: int, cwd: str):
    """Return the folder a leading `cd DIR &&` (or `;`) changes to.

    Only a `cd` before the gh command counts; anything uncertain leaves the
    hook input's cwd in place, so a stop that should stay a stop still does.
    """
    base = Path(cwd or ".")
    i = 0
    while i + 1 < upto:
        if tokens[i] == "cd":
            target = tokens[i + 1]
            j = i + 2
            if j < upto and tokens[j] in ("&&", ";"):
                candidate = Path(target).expanduser()
                base = candidate if candidate.is_absolute() else base / candidate
                i = j + 1
                continue
        i += 1
    return base


def extract_body(tokens: list[str], start: int, cwd: str):
    """Return (body, problem). Exactly one is None."""
    i = start
    while i < len(tokens):
        t = tokens[i]
        if t in ("--web", "-w"):
            return None, ("browser posting skips the guard. Write the "
                          "draft to a file, run the manual check "
                          "(check_voice.py --draft FILE), then paste it "
                          "in the browser, or post it here with "
                          "--body-file.")
        if t in ("--body", "-b"):
            if i + 1 < len(tokens):
                return tokens[i + 1], None
            return None, "--body has no value the guard can read."
        if t.startswith("--body="):
            return t.split("=", 1)[1], None
        if t in ("--body-file", "-F"):
            if i + 1 < len(tokens):
                path = tokens[i + 1]
                if path == "-":
                    return None, ("--body-file - reads stdin, which the "
                                  "guard cannot see. Post from a real "
                                  "file.")
                base = Path(cwd or ".")
                try:
                    return (base / path).read_text(), None
                except OSError as e:
                    return None, (f"could not read the body file: {e} "
                                  f"(searched {base})")
            return None, "--body-file has no value the guard can read."
        if t.startswith("--body-file="):
            path = t.split("=", 1)[1]
            base = Path(cwd or ".")
            try:
                return (base / path).read_text(), None
            except OSError as e:
                return None, (f"could not read the body file: {e} "
                              f"(searched {base})")
        i += 1
    return None, ("no body the guard can read (interactive and --help "
                  "forms are stopped on purpose). Write "
                  "your draft to a file and post with --body-file, or "
                  "run the manual check first.")


def last_json_block(text: str):
    blocks = re.findall(r"```(?:json)?\s*\n(.*?)```", text, flags=re.DOTALL)
    if not blocks:
        raise ValueError("no fenced JSON block in checker output")
    return json.loads(blocks[-1])


def run_voice_pass(guide: str, draft: str) -> dict:
    """One small Sonnet call over the guide and the draft; the same
    contract the skills' voice check uses. Returns the parsed verdict
    object."""
    prompt = PROMPT % (guide, draft)
    last_err = None
    for _ in range(2):
        try:
            proc = subprocess.run(["claude", "-p", "--model", MODEL],
                                  input=prompt, capture_output=True,
                                  text=True, timeout=80)
        except FileNotFoundError:
            raise RuntimeError("the claude CLI is not on PATH")
        except subprocess.TimeoutExpired:
            last_err = "the check timed out"
            continue
        if proc.returncode != 0:
            last_err = f"claude exited {proc.returncode}"
            continue
        try:
            verdict = last_json_block(proc.stdout)
        except (ValueError, json.JSONDecodeError) as e:
            last_err = str(e)
            continue
        if verdict.get("verdict") in ("pass", "stop"):
            return verdict
        last_err = "checker output had no usable verdict"
    raise RuntimeError(last_err or "the check failed")


def log_line(mode: str, target: str, outcome: str):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- {stamp} [{mode}] {outcome} | target: {target}\n"
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a") as f:
            if f.tell() == 0:
                f.write("# voice-guard log (one line per check; this "
                        "file is your guard transcript)\n\n")
            f.write(entry)
    except OSError:
        pass


def stop(msg: str, mode: str, target: str, outcome: str) -> int:
    log_line(mode, target, outcome)
    print(f"voice-guard: STOP. {msg}", file=sys.stderr)
    return 2


def check_draft(draft: str, mode: str, target: str) -> int:
    guide_path = paths.user_file("voice-guide.md")
    try:
        guide = guide_path.read_text()
    except OSError:
        return stop(f"no voice guide at {guide_path}. Run "
                    "`/better-oss:init` to copy the shipped example, then make it "
                    "yours.", mode, target, "stop: no guide")
    if not guide_is_filled(guide):
        return stop("your voice guide has no rules filled in. No "
                    "rules, no guard: the rules are the part you "
                    "write, and the guard will not wave a draft "
                    "through on an empty guide.",
                    mode, target, "stop: guide unfilled")
    try:
        verdict = run_voice_pass(guide, draft)
    except RuntimeError as e:
        return stop(f"the check could not run ({e}). Fix that and try "
                    "again; nothing posts until the check can "
                    "read your draft.",
                    mode, target, f"stop: checker failed ({e})")
    note = f" {EXAMPLE_NOTE}" if paths.is_example(guide) else ""
    if verdict["verdict"] == "pass":
        log_line(mode, target, "pass")
        if mode == "hook":
            print(f"voice-guard: pass. Your rules hold; posting.{note}")
        else:
            print("voice-guard: pass. Your rules hold; you can post "
                  f"it.{note}")
        return 0
    rule = verdict.get("rule", "(rule not quoted)")
    where = verdict.get("where", "")
    detail = f' Draft line: "{where}"' if where else ""
    return stop(f'your own rule: "{rule}".{detail} Revise the draft '
                f"and post again.{note}",
                mode, target, f'stop: rule broken: "{rule}"')


def hook_main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    try:
        tokens = shlex.split(command)
    except ValueError:
        return 0
    start = find_comment_command(tokens)
    if start is None:
        return 0
    target = " ".join(tokens[start - 3:start + 2])
    base = command_cwd(tokens, start, payload.get("cwd", "."))
    body, problem = extract_body(tokens, start, str(base))
    if body is None:
        return stop(problem, "hook", target,
                    f"stop: {problem.split('.', 1)[0]}")
    return check_draft(body, "hook", target)


def manual_main(draft_path: str) -> int:
    try:
        draft = Path(draft_path).read_text()
    except OSError as e:
        print(f"voice-guard: cannot read {draft_path}: {e}",
              file=sys.stderr)
        return 2
    return check_draft(draft, "manual", draft_path)


def main() -> int:
    ap = argparse.ArgumentParser(description=(
        "voice-guard checker: hook mode (no args, stdin JSON) or "
        "manual mode (--draft FILE)."))
    ap.add_argument("--draft", metavar="FILE",
                    help="check a draft file (the manual check for "
                         "browser posts)")
    args = ap.parse_args()
    if args.draft:
        return manual_main(args.draft)
    return hook_main()


if __name__ == "__main__":
    sys.exit(main())
