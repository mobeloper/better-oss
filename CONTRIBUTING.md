# Contributing to better-oss

Thanks for helping. better-oss is a small project with one maintainer, so the
most useful contributions are focused ones: one problem, one change, with
evidence that it works.

By taking part you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). Security
problems go through [SECURITY.md](SECURITY.md), not a public issue. Questions
are welcome; see [SUPPORT.md](SUPPORT.md).

## Ways to contribute

- **Report a bug.** Use the bug form. Say what you ran, what you expected, and
  paste the output. A skill that graded a real issue or PR wrongly is a *rubric*
  report; use the rubric-change form instead (below).
- **Tune a rubric.** The rubrics (`skills/*/rubric.md`) are the judgment in this
  project. A change here changes what the tools decide, so it has a higher bar
  (see "Changing a rubric").
- **Improve a default or an example.** `defaults/` are the example files users
  copy and rewrite; `examples/` is a real worked run. A second worked example
  from a different repo or language is very welcome.
- **Fix a script or the installer.** `core/` (Python, standard library only) and
  `cli/` (the `better-oss-cli` npm package; Node 18+, no dependencies).
- **Add a skill.** Open an issue first so we can agree it belongs in the pipeline.
- **Improve the docs.**

Issues labelled `good first issue` and `help wanted` are good places to start.

## Development setup

The scripts need Python 3.9+ and the standard library only; the installer needs
Node 18+. Install the checks once:

```sh
python3 -m pip install --upgrade pip ruff pytest pre-commit
pre-commit install          # run the hooks on every commit
pre-commit run --all-files  # or check the whole tree now
```

The hooks run `ruff`, the personal-data and symlink check, and `pytest`.

## What must not go in a contribution

Everything you add here is public and permanent, and the people who install
better-oss read and run it. So keep these out of every file you contribute
(code, docs, rubrics, defaults, examples, tests, and pull request text):

- **Personally identifiable information.** Your real name, email address, phone
  number, home address, employer, or private account details; tokens and keys;
  anything private about another person; and local paths, because a
  home-directory path spells out your username. Credit comes through your git
  author line, not through text in the files. What is fine: the URL of a public
  issue or pull request you really worked on, and the public handles shown there.
- **Your personal open-source contribution preferences.** Your fit profile (your
  languages, organizations, time budget, operating system), your search strategy
  (your queries and repository lists), your voice guide, your playbook, and your
  ship manifests describe *you*. They belong in your own folder
  (`~/.claude/better-oss/`, or your clone for per-repo files, kept out of git
  with `.git/info/exclude`). Do not add them to `defaults/`, a skill, or
  `examples/`.

What that means for the shared files:

- **`defaults/`** are the example files users copy and rewrite, and each opens
  with an `EXAMPLE:` comment. Improve them for everyone; do not replace them with
  your own, and keep the comment.
- **`examples/`** show a real run. Use public artifacts only, and strip anything
  personal from your drafts before you copy them in.
- **Rubrics** carry shared judgment, not taste. A rubric change must be justified
  by a case the tool decided wrongly (see "Changing a rubric"), not by how you
  like to work. If a change only reflects a preference, it belongs in your fit
  profile, which ranks issues without changing any verdict.

Before you push, look at your own diff:

```text
git diff main --stat
git ls-files -s | awk '$1==120000'                  # no symlinks (prints nothing)
grep -rIn '/[U]sers/\|/[h]ome/' . --exclude-dir=.git --exclude-dir=node_modules
```

## Set up

You need Claude Code, Python 3.9+, git, `gh` (logged in), Node 18+ and
[ruff](https://docs.astral.sh/ruff/).

```text
git clone https://github.com/mobeloper/better-oss.git
cd better-oss
claude --plugin-dir .          # loads this checkout as the plugin
```

Edit, then run `/reload-plugins` in the session.

**Environment notes**

- **No virtual environment is required.** The Python code uses only the standard
  library. To run the checks, install the two dev tools:
  `python3 -m pip install ruff pytest` (a virtual environment is fine if you
  prefer one).
- **Check your setup** with `python3 core/init.py --check`. It reports whether
  `git`, `gh`, `claude` and your `gh` login are in place.
- **Login only matters for model runs.** Skill runs and the evals call the
  `claude` CLI, so it must be logged in (or have an API key configured). Lint and
  the tests make no model calls and need no login.

Two habits keep your own setup out of the way:

- Set `BETTER_OSS_HOME` to an empty folder when you run a hook or script
  directly, so your own voice guide and playbook are not read.
- Set `CLAUDE_CONFIG_DIR` to an empty folder when you test an install, so your
  real Claude config is untouched.

If you already have the voice-guard or ship-gate hook registered in your own
`settings.json`, each guard runs twice next to the plugin's. Remove your copy
while developing.

## Before you open a pull request

```text
ruff check .
python3 -m pytest
python3 scripts/leak_check.py
(cd cli && npm test)
claude plugin validate .
claude plugin validate skills
```

The same checks run in CI on every pull request (`ruff` and `pytest` on Python
3.9 and 3.13, the installer tests on Node 18 and 22). None of them calls a model.

Read your own diff for personal information and personal preferences (see "What
must not go in a contribution"). Then exercise the thing you changed for real: run the skill on a real issue or
branch, or pipe a hook command into the script (see [AGENTS.md](AGENTS.md)).

## Branches, commits and pull requests

- Branch from `main`, and name the branch `<type>/<issue-number>-<short-title>`:
  lowercase, words joined with hyphens, a short title (about 50 characters at
  most). The type says what kind of change it is: `fix`, `feature`, `docs`,
  `rubric`, `test` or `chore`. Examples: `fix/12-gate-windows-path`,
  `feature/31-installer-doctor`, `rubric/7-shipped-recently-arithmetic`,
  `docs/5-go-search-strategy`. With no issue, leave the number out:
  `docs/clarify-env-setup`. The branch type is separate from the commit prefix
  below.
- Commit messages start with `[add]`, `[update]` or `[fix]`.
- Please sign off your commits (`git commit -s`) to certify the
  [Developer Certificate of Origin](https://developercertificate.org/). This is
  requested and not yet enforced.
- Keep a pull request to one change. A maintainer asking you to split or merge
  work is right, as the tools themselves tell you about other people's repos.
- Fill in the pull request template. It asks how you tested and how AI was used.
- **What CI checks.** Branch names are a convention that keeps the history
  readable; CI does not check them. CI runs `ruff` and `pytest` (Python 3.9 and
  3.13), the personal-data and symlink check, `actionlint` over the workflows,
  and the installer tests (Node 18 and 22). Run the same commands from "Before you open a pull request" so your pull
  request is green the first time.

## Changing a rubric

The skills have an evaluation suite in [`evals/`](evals/): frozen cases, each a
real worked run with one deliberate flaw, and the check that must catch it. It
runs locally and is not yet a required CI check, so run it yourself:

```text
python3 evals/run_evals.py --dry-run                    # validates the cases; no model, no cost
python3 evals/run_evals.py --skill plan-check           # runs one skill's cases (one model call each)
```

A rubric pull request must show:

1. **The case:** the issue, PR or draft that was graded wrongly (a URL, or the
   text if it is private), and the check that got it wrong.
2. **Before:** the verdict and the check grade the current rubric gives.
3. **After:** the verdict and grade with your change, from a real run.
4. **No collateral damage:** the same run on at least one case that already
   graded correctly, with the grade unchanged. Running the skill's evals shows
   this for every case at once, and [`examples/`](examples/) has real inputs you
   can reuse. If your change is for a case the suite does not cover, add a case
   under `evals/cases/<skill>/`.

Change check names, pass conditions, weights or the verdict rule only on
purpose: other files (the evidence guides and the ship-gate) refer to them by
name. The rubrics were tuned on Sonnet; the project pins that model for a
reason, so a change that only works on a different model is not an improvement.

## Changing the hooks or scripts

The hooks run on every Bash command Claude runs, so they **fail closed**: Claude
Code only blocks on exit code 2, and a crash exits 1 and would let a post or a
pull request through unchecked. Any new code path in `voice_guard/` or
`ship_gate/` that can raise must end in a stop (exit 2), never a pass.

The pr-monitor never posts. Its `READONLY_GH` allowlist is a guarantee, not a
default; do not widen it.

## Review

This is a single-maintainer project, so reviews are best effort. If a week goes
by with no reply, one short comment on the pull request asking if it is still
wanted is fine. A pull request nobody has touched for a long time may be closed
with a note, and you are welcome to reopen it.

## AI-assisted contributions

They are welcome, with one ask: say how AI was used in the pull request
description, in your own words. You are responsible for every line you submit,
whoever or whatever wrote it.
