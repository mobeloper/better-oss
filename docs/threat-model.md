# Threat model

better-oss runs on your machine and reads text written by other people. This
page states where the trust boundaries are and what each part does **not**
protect against. It is grounded in the code; the cited files are the source of
truth when this page and the code disagree.

## What runs where

| Part | Runs | Reads | Can change |
| --- | --- | --- | --- |
| Hooks (`hooks/hooks.json`) | `python3 core/voice_guard/check_voice.py` and `core/ship_gate/check_gate.py`, before every Bash command Claude Code is about to run | The command, the hook's JSON on stdin, files named by `--body-file`, and the repo (git status, the manifest) | Exit code: 2 blocks the command, anything else lets it through |
| Ship manifest (`ship-manifest.md`) | The commands in its table, from `check_gate.py` | Your repository | Whatever those commands do; they are your commands |
| Monitor (`core/pr_monitor/monitor.py`) | On request | The PR through the read-only `gh` allowlist (`READONLY_GH`) | Nothing on GitHub |
| Installer (`cli/bin/better-oss.js`, `core/init.py`) | `npx better-oss-cli init` | Your home folder and the installed plugin | Copies example files; calls `claude plugin install`; never edits `settings.json` |

## Trust boundaries

1. **Model text is untrusted.** The guards and skills put issue and PR text into
   a prompt. A prompt injection can at worst change a **verdict** — for example
   make a bad draft pass the voice check. It cannot post, push or comment: the
   hooks only return an exit code, and the monitor only reads.
2. **The command line is untrusted input to the hooks.** `check_voice.py` and
   `check_gate.py` parse the command, not a summary of it. They stop what they
   cannot read (`--web`, `--fill`, a missing body file) rather than guess.
3. **The manifest is trusted code.** `ship-manifest.md` runs shell commands
   from your repository. Read it before you run a contribution's manifest, the
   same way you would read a `Makefile` or a CI config.
4. **GitHub is read-only for the monitor.** Every `gh` call goes through
   `READONLY_GH`; anything else is reported as a bug, not executed.
5. **Your local files are yours.** `init` does not overwrite an existing file
   without `--force`, and the installer never edits Claude Code's
   `settings.json`.

## What the guards do not protect against

- **Posting through the browser.** `gh pr create --web` and the GitHub web UI
  bypass the hooks; that is why the hooks stop `--web` and ask for
  `--body-file`.
- **`gh api` writes.** The voice guard checks comments posted through
  `gh issue comment` / `gh pr comment` / `create`. A `gh api` call that writes
  is outside that check today (tracked separately).
- **A malicious manifest.** The ship-gate runs the commands in the manifest;
  it does not sandbox them.
- **A compromised local tool.** A trojaned `gh`, `git` or `claude` is outside
  this project's control; the guards call the programs you have installed.
- **A wrong grade.** A rubric decision is a judgment, not a security boundary.
  A prompt injection can make a check too lenient; it cannot make it publish.

## Recommended practice

- Read `ship-manifest.md` before running a contribution from someone else.
- Keep the guards fail-closed: do not add an override that silently passes when
  the model is unavailable.
- Report a bypass privately (see [SECURITY.md](../SECURITY.md)), not in a
  public issue.
