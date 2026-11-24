# Roadmap

Where better-oss is, and where to help. Every item is a GitHub issue; the numbers
link to them, and the milestones group them.

## Where we are

- **v0.1.0 is released**: `better-oss-cli@0.1.0` on npm and a GitHub release,
  published by the automated release workflow (npm trusted publishing, approved by
  a maintainer). The first public build, `0.0.1`, stays on npm; npm never lets a
  version number be reused.
- CI is green on `main`, with tests that need no model, an evaluation suite
  (`evals/`, 18 frozen cases), and a set of required checks.
- The first outside contributions are in: the Python 3.9 CI fix, the installer's
  dry-run fix, the leak-check fix, and tests for the installer, the guards and the
  monitor. The v0.1.0 milestone is closed.

## Next: v0.2.0, quality gates and trust

The theme: stop relying on the maintainer to notice problems. Enforce the
contribution rules and the evals in CI, test the hooks and monitor completely,
and make the release verify itself.

**Gate contributions**

| Issue | What | Size |
|---|---|---|
| [#15](https://github.com/mobeloper/better-oss/issues/15) | Tests for `check_pr.py`, `eval_scope.py` and the evals harness | medium |
| [#17](https://github.com/mobeloper/better-oss/issues/17) | Write `evals/README.md` | small |
| [#16](https://github.com/mobeloper/better-oss/issues/16) | Evals as a required merge check (needs a model key, see the issue) | medium to large |

**Make CI catch more**

| Issue | What | Size |
|---|---|---|
| [#42](https://github.com/mobeloper/better-oss/issues/42) | Validate the plugin manifest and skills with `claude plugin validate` | small to medium |
| [#19](https://github.com/mobeloper/better-oss/issues/19) | Lint the workflows with actionlint | small |
| [#23](https://github.com/mobeloper/better-oss/issues/23) | CodeQL code scanning | small |
| [#24](https://github.com/mobeloper/better-oss/issues/24) | Dependency review, and the failing Dependabot Actions updates | small |
| [#43](https://github.com/mobeloper/better-oss/issues/43) | Smoke-test the published package and plugin install after each release | medium |

**Make the hooks dependable**

| Issue | What | Size |
|---|---|---|
| [#45](https://github.com/mobeloper/better-oss/issues/45) | `cd dir && gh ... --body-file x` is wrongly stopped | small |
| [#44](https://github.com/mobeloper/better-oss/issues/44) | A clear message and an explicit override when the model is unavailable | medium |
| [#9](https://github.com/mobeloper/better-oss/issues/9) | Hooks leave a child process behind when killed | medium |
| [#10](https://github.com/mobeloper/better-oss/issues/10) | voice-guard misses comments posted through `gh api` | medium |

**Behavior and docs**

| Issue | What | Size |
|---|---|---|
| [#7](https://github.com/mobeloper/better-oss/issues/7) | `shipped-recently` passed while quoting 122 days | small |
| [#21](https://github.com/mobeloper/better-oss/issues/21) | pr-monitor fixture tests for every PR state | medium |
| [#25](https://github.com/mobeloper/better-oss/issues/25) | Troubleshooting and FAQ | small to medium |

### Suggested order

`[#45](https://github.com/mobeloper/better-oss/issues/45)`, `[#19](https://github.com/mobeloper/better-oss/issues/19)`, `[#42](https://github.com/mobeloper/better-oss/issues/42)` and `[#15](https://github.com/mobeloper/better-oss/issues/15)` are independent and small: start there. Then
`[#14](https://github.com/mobeloper/better-oss/issues/14)` and `[#17](https://github.com/mobeloper/better-oss/issues/17)`, then `[#16](https://github.com/mobeloper/better-oss/issues/16)` (it needs `[#15](https://github.com/mobeloper/better-oss/issues/15)`). The hook items can run in
parallel with all of it.

## After that: v0.3.0, reach

Windows support for the hooks ([#4](https://github.com/mobeloper/better-oss/issues/4), the biggest limit on who can use this),
search-strategy examples for other languages ([#5](https://github.com/mobeloper/better-oss/issues/5)), a second worked example
([#6](https://github.com/mobeloper/better-oss/issues/6)), a `doctor` command ([#8](https://github.com/mobeloper/better-oss/issues/8)), a plugin icon and marketplace description
([#29](https://github.com/mobeloper/better-oss/issues/29)), and a README demo ([#33](https://github.com/mobeloper/better-oss/issues/33)).

## Later

- Evals: a negative case for every required check ([#32](https://github.com/mobeloper/better-oss/issues/32)), cases for
  `issue-scout` ([#31](https://github.com/mobeloper/better-oss/issues/31)), and repeat runs, a flakiness report and a cost estimate
  ([#11](https://github.com/mobeloper/better-oss/issues/11)).
- Tooling and docs: labeler and stale workflows ([#26](https://github.com/mobeloper/better-oss/issues/26)), a threat model
  ([#27](https://github.com/mobeloper/better-oss/issues/27)), a pre-commit config ([#28](https://github.com/mobeloper/better-oss/issues/28)), a cleaner `repro-check` rubric
  ([#30](https://github.com/mobeloper/better-oss/issues/30)), and pinning GitHub Actions to commit SHAs ([#46](https://github.com/mobeloper/better-oss/issues/46)).
- Direction: a standalone CLI that runs the skills outside Claude Code
  ([#34](https://github.com/mobeloper/better-oss/issues/34), a design discussion first).

## How to pick something up

1. Filter issues by [`good first issue`](https://github.com/mobeloper/better-oss/labels/good%20first%20issue)
   or [`help wanted`](https://github.com/mobeloper/better-oss/labels/help%20wanted),
   and by milestone. `priority:p1` comes before `priority:p2`.
2. Comment that you are taking it, so two people do not do the same work.
3. Read [CONTRIBUTING.md](../CONTRIBUTING.md) (setup, branch names, what CI checks).
4. You do not need model credits for most of this. Lint, the tests and the eval
   `--dry-run` need none, and the guards' decision paths are tested with a fake
   `claude`. Only running the evals or a skill needs a logged-in `claude`.
