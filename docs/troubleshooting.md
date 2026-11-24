# Troubleshooting

Each entry quotes the message you see and the fix. If a problem is not here, run
`python3 core/init.py --check` first: it reports whether `git`, `gh`, `claude`
and your `gh` login are in place.

## The hooks run twice

**Symptom:** every Bash command is checked twice, or a guard's log has two
entries for one command.

**Cause:** the plugin's hooks and a copy in your own Claude Code
`settings.json` are both registered.

**Fix:** keep one. Remove the `hooks` entry from your `settings.json` if you
installed the plugin (or remove the plugin if you wired the hooks by hand), then
restart Claude Code.

## "shipped EXAMPLE" notices

**Messages:**

```text
NOTE: this check used the shipped EXAMPLE voice guide, not yours. Copy
defaults/voice-guide.md to ~/.claude/better-oss/voice-guide.md
(/better-oss:init does this), rewrite it, and delete its EXAMPLE comment.
```

```text
ship-manifest.md still has the shipped EXAMPLE comment, so it is the example
for a fictional repo, not yours. Rewrite its title and both tables for this
repo, then delete the EXAMPLE comment at the top (the comment explains how).
```

The monitor prints a similar note when it drafts from the example playbook.

**Fix:** run `/better-oss:init` (or `python3 core/init.py`) to copy the example
files, rewrite them for your repository, and delete the `EXAMPLE` comment at the
top. The notice disappears once the file is yours.

## `gh` or `claude` is missing, or not logged in

**Symptom:** `git failed`, `gh` exits with an auth error, or the model checks say
they cannot run.

**Fix:** install both CLIs and sign in:

```sh
gh auth status        # then: gh auth login
claude --version      # install Claude Code if this fails
```

The guards fail closed on purpose when the model cannot run. They do not pass a
check just because the CLI is broken.

## "not inside a git clone"

**Message:** `<dir> is not inside a git clone. Run the ship-gate from the clone
of the repository your contribution lives in, on your branch.`

**Fix:** `cd` into the clone (not a parent folder or a worktree copy) and run the
command on the branch whose pull request you are opening.

## The ship-gate asks for a fresh pass after 30 minutes

A pass run by hand carries to the hook for 30 minutes. After that the hook asks
again, so an old pass cannot approve a different PR.

**Fix:** run the check again, then open the pull request within the window.

## The plugin does not load after an update

**Fix:** inside Claude Code run `/reload-plugins`; if that is not enough, restart
Claude Code. `/plugin list` should show `better-oss` with the new version.

## `npx better-oss-cli` fails

**Symptom:** a network error, a proxy error, or `EACCES` while `npx` downloads
the package.

**Fix:** check `npm config get registry` and your proxy settings, then retry. If
the cache is corrupt, `npm cache clean --force` and run the command again. A
permission error usually means a global prefix you cannot write; `npx` needs no
global install, so remove any half-installed global copy.
