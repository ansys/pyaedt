---
name: pyaedt-branch-naming
description: Use whenever a Git branch is about to be created, renamed, or pushed in the PyAEDT repository. Triggers on requests to create a new branch, start work on an issue or feature, check out a new branch, rename a branch, or choose a branch name. Enforces the PyAnsys branch naming ruleset.
---

# PyAEDT branch naming skill

The PyAEDT repository enforces the PyAnsys
[branch naming ruleset](https://dev.docs.pyansys.com/_downloads/7510e6c963aea4a6bc7ca8a9798cb721/branch_naming.json)
as an **active** GitHub repository rule with no bypass actors. A push to a non-conforming branch is
rejected by the server, so the name must be correct at creation time.

A copy of the ruleset is stored next to this skill in `branch_naming.json` for reference.

## Hard rule

**Never create a branch without a valid prefix.** Before running `git branch`, `git checkout -b`,
`git switch -c`, or `gh pr create` on a new branch, the name must match:

```text
^(feat|fix|chore|docs|style|refactor|test|testing|perf|ci|no-ci|build|dependabot|release|maint|junk)/.*
```

That is: an allowed prefix, a single forward slash, then a non-empty descriptive name.

If the user asks for a branch and does not supply a conforming name, do **not** invent an arbitrary
name and do not fall back to the plain issue number. Derive the prefix from the nature of the work
using the table below, propose the full name, and use it.

## Allowed prefixes

| Prefix | Use for |
|---|---|
| `feat` | New user-facing functionality. |
| `fix` | Bug fixes. |
| `chore` | Routine repository upkeep that is not a feature or a fix. |
| `docs` | Documentation only, including docstrings and `doc/`. |
| `style` | Formatting and cosmetic changes with no behavior change. |
| `refactor` | Restructuring existing code without changing behavior. |
| `test` / `testing` | Adding or updating tests. |
| `perf` | Performance improvements. |
| `ci` | Continuous integration and workflow changes. |
| `no-ci` | Changes that must not trigger continuous integration. |
| `build` | Build system, packaging, or `pyproject.toml` changes. |
| `dependabot` | Automated dependency updates. |
| `release` | Release preparation branches. |
| `maint` | Maintenance work. |
| `junk` | Throwaway experiments that will never be merged. |

Pick the prefix that matches the dominant purpose of the change, and keep it consistent with the
conventional-commit type used for the pull request title (see the `pyaedt-contribution` skill):
a `feat/...` branch carries `FEAT:` commits, a `fix/...` branch carries `FIX:` commits.

## Naming the rest of the branch

After the slash, use a short, lowercase, hyphen-separated description. Include the issue number
first when one exists.

```text
feat/8034-twisted-pair-cable-creation
fix/7988-box-unit-handling
docs/8034-pyaedt-dev-plugin
test/7991-extend-general-methods-coverage
ci/pin-ruff-version
```

Guidance:

- Keep it under roughly 60 characters.
- Use hyphens, not underscores or spaces.
- Use lowercase; do not uppercase the prefix (`FEAT/...` does not match the pattern).
- Describe the change, not the author or the date.

## Excluded and protected branches

These refs are exempt from the pattern and must never be created, force-pushed, or deleted by you:

- `main`
- `gh-pages`
- `pre-commit-ci-update-config`

The ruleset also blocks branch **deletion** and **non-fast-forward** pushes. Never run
`git push --force`, `git push --force-with-lease`, or `git push --delete` against the remote unless
the user explicitly asks and understands the rule will reject it.

## Procedure

1. Determine the purpose of the work and map it to a prefix from the table.
2. Look up the related issue or pull request number, if any.
3. Compose `"<prefix>/<number>-<short-description>"`.
4. Validate it before using it:

   ```bash
   python -c "import re, sys; pattern = r'^(feat|fix|chore|docs|style|refactor|test|testing|perf|ci|no-ci|build|dependabot|release|maint|junk)/.+$'; print('OK' if re.match(pattern, sys.argv[1]) else 'INVALID')" feat/8034-my-change
   ```

5. Create the branch from an up-to-date `main`:

   ```bash
   git switch main
   git pull --ff-only
   git switch -c feat/8034-twisted-pair-cable-creation
   ```

6. If a branch with a non-conforming name already exists locally and has not been pushed, rename it
   rather than pushing it:

   ```bash
   git branch -m feat/8034-twisted-pair-cable-creation
   ```

## Anti-patterns

- `8034-twisted-pair-cable` — no prefix; rejected.
- `feature/twisted-pair` — `feature` is not an allowed prefix; use `feat`.
- `FEAT/twisted-pair` — the pattern is case sensitive.
- `feat-twisted-pair` — the separator must be a forward slash.
- `feat/` — the description after the slash must not be empty.
- `/my-change` — the ruleset regex contains an empty alternative that technically permits a leading
  slash. Never use it; it defeats the purpose of the convention.
