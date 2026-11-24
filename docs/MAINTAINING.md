# Maintaining better-oss

For the maintainer (and anyone who becomes one). Contributors: see
[CONTRIBUTING.md](../CONTRIBUTING.md).

## One-time repository setup

Do these by hand in the GitHub UI or with `gh`; none of it can live in the repo.

**Settings (Settings tab)**

- General: enable **Discussions** (the issue form and `SUPPORT.md` link to it;
  or `gh repo edit --enable-discussions`).
- Code security: enable **Private vulnerability reporting** (`SECURITY.md` and
  the Code of Conduct send reports there), **Dependabot alerts** and
  **Dependabot security updates**.
- Branches: add a rule for `main` that requires a pull request before merging, and
  (after CI has run once) requires its checks; the names are listed under "CI". Pick one merge style and keep
  it (the history so far uses merge commits).

**Labels.** `bug`, `enhancement`, `question`, `documentation`, `good first
issue` and `help wanted` already exist on a new repo. Create the rest:

```text
gh label create rubric    --color 5319e7 --description "A rubric, procedure or evidence-guide change"
gh label create hooks     --color d93f0b --description "voice-guard or ship-gate"
gh label create installer --color 0e8a16 --description "npx better-oss-cli init"
gh label create monitor   --color 1d76db --description "pr-monitor"
gh label create needs-repro --color fbca04 --description "Waiting for steps to reproduce"
for s in issue-scout issue-select repro-check plan-check pr-precheck; do
  gh label create "skill:$s" --color c5def5 --description "The $s skill"
done
```

**Description and topics**

```text
gh repo edit --description "Skills and guardrail hooks for making robust, reliable open source contributions (a Claude Code plugin)"
gh repo edit --add-topic claude-code --add-topic claude-code-plugin --add-topic agents \
             --add-topic open-source --add-topic automation
```

## Triage

1. Reproduce it, or ask for the missing piece and add `needs-repro`.
2. Label it: its type (`bug`, `enhancement`, `question`, `documentation`), its
   area (`rubric`, `hooks`, `installer`, `monitor`, or `skill:<name>`), and
   `good first issue` or `help wanted` when it fits.
3. Close duplicates with a link. Close "a skill graded my issue wrongly"
   reports that have no case and no verdicts, asking for the rubric-change form.
4. Answer questions in Discussions, and turn a repeated question into docs.

## Reviewing a pull request

Always: the PR template is filled in, the checks in `AGENTS.md` pass, the diff
is one change, and this holds:

```text
git ls-files -s | awk '$1==120000'      # no symlinks (must print nothing)
grep -rIn '/[U]sers/\|/[h]ome/' . --exclude-dir=.git --exclude-dir=node_modules
```

By area:

- **Rubrics, procedures, evidence guides.** The PR must show the case, the
  verdict before and after, and a case that was already right and still is. Re-run
  at least the failing case yourself with `claude --plugin-dir .`. Check names,
  weights and the verdict rule must change only on purpose, because the
  evidence guides and the ship-gate refer to them by name. Look for a wording
  change that fixes the one case by making the check easier to pass in general.
- **Hooks (`core/voice_guard`, `core/ship_gate`).** Every new path that can raise
  must end in exit 2. Pipe a few commands into the script (see `AGENTS.md`). A
  hook must never print a pass for something it could not read.
- **pr-monitor.** The `READONLY_GH` allowlist must not grow. A new `gh` call needs
  an issue first.
- **Installer.** It must not write `settings.json`, and must not overwrite a file
  without `--force`. `cd cli && npm test` covers both.
- **`defaults/`.** Still prefilled, still carrying the `EXAMPLE:` banner, and
  still generic wording (no personal paths or names beyond the author fields).
- **Skills.** `SKILL.md` frontmatter intact; the `pr-precheck` layout in
  `skills/pr-precheck/CONTRACT.md` unchanged.

## Releasing

A release is a tag. The `Release` workflow does the rest, and the npm step waits
for your approval.

1. Decide the version (`X.Y.Z`). Set it in **both** `.claude-plugin/plugin.json`
   and `cli/package.json`; they must match. Move the `Unreleased` entries in
   `CHANGELOG.md` under a new dated `## [X.Y.Z] - YYYY-MM-DD` heading.
2. Run the checks locally (`ruff check .`, `python3 -m pytest`,
   `python3 scripts/leak_check.py`, `cd cli && npm test`) and
   `cd cli && npm pack --dry-run` (the `prepack` step copies `defaults/` into the
   package; the list should show it).
3. Test a clean install against an empty config, from the working tree:

   ```text
   export CLAUDE_CONFIG_DIR=$(mktemp -d)
   node cli/bin/better-oss.js init --home $(mktemp -d) --marketplace "$PWD"
   claude plugin list
   ```

4. Merge to `main`, then tag the merge commit and push the tag:

   ```text
   git tag vX.Y.Z && git push origin vX.Y.Z
   ```

5. Watch the workflow (Actions tab):
   - **verify** checks that the tag, `plugin.json`, `cli/package.json` and the
     changelog heading agree (`python3 scripts/release_tools.py check vX.Y.Z`),
     then runs the tests.
   - **release** creates the GitHub release with notes from the changelog (marked
     a pre-release while the version is `0.x`).
   - **publish** runs `npm publish --provenance` once you approve the
     `npm-publish` environment.
6. Check `npx better-oss-cli@latest --version`. Users get the plugin update with
   `claude plugin update better-oss`.

### One-time setup for the automated publish

- **Environment.** Settings > Environments > New environment, named exactly
  `npm-publish`, with yourself as a required reviewer. Do this *before* the first
  tag: GitHub creates a missing environment with no protection, and then the
  publish job would not wait for anyone.
- **npm trusted publishing.** npm can accept a publish from this workflow with no
  stored token. A package must already exist to configure it, so the very first
  version is published by hand (`cd cli && npm publish --access public`, which
  asks for your npm login and second factor). Then on npmjs.com open the
  package's Settings, add a Trusted Publisher for GitHub Actions with repository
  `mobeloper/better-oss`, workflow `release.yml` and environment `npm-publish`.
  The workflow uses Node 24 because trusted publishing needs a recent npm. Check
  npm's current documentation when you set it up, as this feature is new.
- **If the publish job fails with `E403 ... OIDC permission denied`.** The
  workflow got its token and npm refused it, which means the Trusted Publisher
  entry does not match. Nothing was published. Compare the entry on the package's
  Settings page with what this workflow presents: owner `mobeloper`, repository
  `better-oss`, workflow `release.yml` (the file name only, not the path),
  environment `npm-publish`. A wrong environment name, a path in the workflow
  field, or an entry saved on another package are the usual causes. After fixing
  it, open the failed run, choose *Re-run failed jobs*, and approve the
  `npm-publish` deployment again; no new tag or version is needed.
- **Manual fallback.** If the workflow's publish step is not set up, publish by
  hand from `cli/` after the tag exists; the rest of the release is unchanged.

## CI

Workflows pin every action to a full commit SHA with the tag in a trailing
comment, for example `uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0`.
A tag can move; the SHA cannot, and `release.yml` publishes to npm with an
OIDC token. Dependabot still proposes updates for the `github-actions` ecosystem:
when you take one, update the SHA and the comment together.

`ci.yml` runs on every push to `main` and every pull request: `ruff` and `pytest`
on Python 3.9 and 3.13, the installer tests on Node 18 and 22, and the leak
check. After it has run once, require these checks in the `main` branch rule:
`Python 3.9`, `Python 3.13`, `Personal data and symlinks`, `Installer (Node 18)`
and `Installer (Node 22)`.

**Project-private terms.** The leak check built into the repo only knows
universal rules (home paths, emails, tokens, symlinks). If there are words that
must never appear in the repository, add them as repository secrets so they are
never committed:

- `LEAK_EXTRA_PATTERNS`: a case-insensitive regex of those terms (for example
  `term one|term two`).
- `LEAK_ALLOW_FILES`: comma-separated repo paths exempt from those extra terms,
  such as a file that carries an author credit.

Run it the same way locally:
`LEAK_EXTRA_PATTERNS='term one|term two' python3 scripts/leak_check.py`.
Pull requests from forks do not receive secrets, so only the universal rules run
for them; recheck those PRs yourself before merging.

## Dependabot

Dependabot opens weekly pull requests for the installer's npm dependencies
(there are none today) and for GitHub Actions once workflows exist. Treat them
like any other pull request: the tests must pass.
