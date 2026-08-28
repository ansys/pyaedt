# PyAEDT Copilot Instructions

## Skill Selection Guide

Skills are organized as plugins under `.github/plugin/`. Always **read the skill file** (using the file-reading tool) **before** responding.

| Skill | Skill file | Purpose |
|---|---|---|
| `pyaedt-cli` | `.github/plugin/pyaedt-cli/skills/SKILL.md` | Interact with AEDT via the `pyaedt` CLI |
| `pyaedt-code-placement` | `.github/plugin/pyaedt-dev/skills/pyaedt-code-placement/SKILL.md` | Decide where new PyAEDT code belongs and reuse existing code |
| `pyaedt-docstrings` | `.github/plugin/pyaedt-dev/skills/pyaedt-docstrings/SKILL.md` | Write PyAnsys-style numpydoc docstrings and PEP 8 compliant code |
| `pyaedt-testing` | `.github/plugin/pyaedt-dev/skills/pyaedt-testing/SKILL.md` | Add or update tests for PyAEDT code |
| `pyaedt-refactor` | `.github/plugin/pyaedt-dev/skills/pyaedt-refactor/SKILL.md` | Modify, clean up, or deprecate existing PyAEDT code |
| `pyaedt-branch-naming` | `.github/plugin/pyaedt-dev/skills/pyaedt-branch-naming/SKILL.md` | Name and create Git branches per the PyAnsys ruleset |
| `pyaedt-contribution` | `.github/plugin/pyaedt-dev/skills/pyaedt-contribution/SKILL.md` | Run quality checks, write changelog fragments, and open pull requests |

---

## Branch naming (MANDATORY, always applies)

**Whenever you are asked to create, rename, or check out a new branch, the branch name MUST match
the PyAnsys [branch naming ruleset](https://dev.docs.pyansys.com/_downloads/7510e6c963aea4a6bc7ca8a9798cb721/branch_naming.json),
which is enforced as an active repository rule with no bypass actors.**

```text
^(feat|fix|chore|docs|style|refactor|test|testing|perf|ci|no-ci|build|dependabot|release|maint|junk)/.+
```

Allowed prefixes: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`, `testing`, `perf`,
`ci`, `no-ci`, `build`, `dependabot`, `release`, `maint`, `junk`.

Rules:

- Always prefix the branch, then a single `/`, then a lowercase hyphen-separated description,
  prefixed by the issue number when one exists, for example `feat/8034-twisted-pair-cable`.
- Never create an unprefixed branch such as `8034-my-fix`, and never use `feature/`, `FEAT/`, or
  `feat-`.
- If the user does not give a conforming name, derive the prefix from the nature of the change,
  state the name you chose, and use it. Do not silently invent a non-conforming name.
- Never create, force-push, or delete `main`, `gh-pages`, or `pre-commit-ci-update-config`. The
  ruleset also blocks deletions and non-fast-forward pushes on all other branches.

Read `.github/plugin/pyaedt-dev/skills/pyaedt-branch-naming/SKILL.md` for prefix selection guidance,
validation commands, and examples.

---

## pyaedt-dev (MANDATORY)

**Read the relevant skill files whenever you write or modify PyAEDT Python code:**

- Adding a new class, method, function, or static asset → `pyaedt-code-placement`
- Writing or fixing docstrings, type hints, imports, or formatting → `pyaedt-docstrings`
- Adding or updating tests → `pyaedt-testing`
- Changing, cleaning up, or deprecating existing code → `pyaedt-refactor`
- Creating, renaming, or checking out a branch → `pyaedt-branch-naming`
- Committing, opening a pull request, or running quality checks → `pyaedt-contribution`

Core rules enforced by these skills:

- Prefer reusing existing code over writing new code.
- Place code in the package matching its function; never restructure the repository unless the user
  explicitly asks.
- Document everything following the
  [PyAnsys documentation style reference](https://dev.docs.pyansys.com/doc-style/index.html).
- Cover new functionality with a test, preferring updates to existing tests.
- Improving poorly written or poorly documented code requires explicit user approval first.

---

## pyaedt-cli (MANDATORY)

**Read this skill file when the user wants to interact with AEDT:**

- Launch, connect to, or stop AEDT
- Open / save / list projects or designs
- Execute a script or inline code inside AEDT

```
Read skill file: .github/plugin/pyaedt-cli/skills/SKILL.md
```
