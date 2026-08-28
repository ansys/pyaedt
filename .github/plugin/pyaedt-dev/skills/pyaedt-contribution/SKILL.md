---
name: pyaedt-contribution
description: Use when preparing a PyAEDT change for review. Triggers on requests to commit, open or update a pull request, write a changelog fragment, name a branch or pull request, or run the PyAEDT quality checks and pre-commit hooks.
---

# PyAEDT contribution workflow skill

Follow the [PyAnsys contributing guide](https://dev.docs.pyansys.com/how-to/contributing.html) plus
the PyAEDT specifics below.

## 1. Quality gate

Run the full hook set before committing. The repository pins `prek` in the `quality` dependency
group; `pre-commit` works as a drop-in alternative.

```bash
prek run --all-files
```

Hooks that must pass:

| Hook | Purpose |
|---|---|
| `ruff-check` | Lint (`D`, `E`, `F`, `I`, `N`, `PTH`, `TD`, `W`, `UP006`, `UP007`, `UP045`). |
| `ruff-format` | Formatting, 120 columns, double quotes. |
| `codespell` | Spelling, using `doc/styles/config/vocabularies/ANSYS/accept.txt`. |
| `debug-statements` | No leftover debugger or debug statements. |
| `trailing-whitespace` | No trailing whitespace. |
| `check-github-workflows` | Workflow files validate against the schema. |
| `blacken-docs` | Code blocks in documentation are formatted. |
| `add-license-headers` | MIT header on `src`, `tests`, `doc`, `examples` Python files. |
| `ty` | Static type checking. |

Then run the targeted tests for the change (see the `pyaedt-testing` skill).

## 2. Changelog fragment

Every user-visible change needs a towncrier fragment in `doc/changelog.d`, named
`<pull-request-number>.<type>.md`, for example `7983.added.md`.

Valid types, from `[tool.towncrier]` in `pyproject.toml`:

`breaking`, `added`, `fixed`, `documentation`, `dependencies`, `maintenance`, `miscellaneous`, `test`

The file contains a single short sentence describing the change from the user's point of view:

```text
Add support for creating twisted-pair cables in the advanced CAD modeler.
```

If the pull request number is not known yet, tell the user to rename the fragment once the pull
request is opened.

## 3. Branch and commit

- Work on a feature branch; never commit to `main`.
- The branch name must satisfy the PyAnsys branch naming ruleset, which is enforced as an active
  repository rule: `<prefix>/<description>` where `<prefix>` is one of `feat`, `fix`, `chore`,
  `docs`, `style`, `refactor`, `test`, `testing`, `perf`, `ci`, `no-ci`, `build`, `dependabot`,
  `release`, `maint`, or `junk`. See the `pyaedt-branch-naming` skill for details.

  ```bash
  git switch main
  git pull --ff-only
  git switch -c feat/8034-twisted-pair-cable-creation
  ```

- Commit messages follow conventional commits with an **upper-case** type, matching the pull request
  title requirement and the branch prefix, for example:

  ```text
  FEAT: Add twisted-pair cable creation to advanced CAD
  FIX: Correct unit handling in Modeler.create_box
  DOCS: Clarify Hfss setup docstrings
  MAINT: Update ruff configuration
  TEST: Extend unit coverage for general methods
  ```

- Never commit secrets, AEDT project binaries, or generated artifacts.

## 4. Pull request

- Title uses the same conventional-commit format with an upper-case type. This is checked in CI.
- Fill in `.github/pull_request_template.md`.
- Describe what changed, why, and how it was verified.
- Confirm in the description that documentation and tests were added or updated.

## Pre-submit checklist

- [ ] Code is placed per the `pyaedt-code-placement` skill and reuses existing helpers.
- [ ] Docstrings follow the PyAnsys style and pass numpydoc validation.
- [ ] New or changed behavior is covered by tests, preferring updates to existing tests.
- [ ] `prek run --all-files` passes.
- [ ] Targeted `pytest` selector passes.
- [ ] A `doc/changelog.d/<pr>.<type>.md` fragment exists.
- [ ] The branch name matches the PyAnsys branch naming ruleset (`<prefix>/<description>`).
- [ ] Commit messages and the pull request title use the upper-case conventional-commit format.
