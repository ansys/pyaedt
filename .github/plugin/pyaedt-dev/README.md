# PyAEDT Dev

Plugin that helps AI coding agents develop and maintain the PyAEDT Python codebase.

Use `pyaedt-cli` when you want to *drive* Ansys Electronics Desktop (AEDT). Use `pyaedt-dev` when
you want to *change the PyAEDT source code itself*.

## What it does

- **Code placement**: decides which package a new class, method, or asset belongs in, and enforces
  code reuse before new code is written
- **Documentation and style**: numpydoc docstrings following the
  [PyAnsys documentation style reference](https://dev.docs.pyansys.com/doc-style/index.html), plus
  the PEP 8 and ruff rules configured in `pyproject.toml`
- **Testing**: requires coverage for every new behavior and prefers extending existing tests
- **Refactoring**: improves poorly written or poorly documented code, but only with explicit user
  approval, and keeps the public API backward compatible
- **Branch naming**: enforces the PyAnsys branch naming ruleset on every new branch
- **Contribution workflow**: towncrier changelog fragments, conventional-commit pull request titles,
  and the pre-commit quality gate

## Skills

| Skill | Use when |
|---|---|
| `pyaedt-code-placement` | Deciding where new code, data, or assets belong in `src/ansys/aedt/core` |
| `pyaedt-docstrings` | Writing or reviewing docstrings, type hints, imports, or formatting |
| `pyaedt-testing` | Adding or updating tests for new or changed behavior |
| `pyaedt-refactor` | Modifying, cleaning up, or deprecating existing PyAEDT code |
| `pyaedt-branch-naming` | Creating, renaming, or checking out a Git branch |
| `pyaedt-contribution` | Committing, opening a pull request, or running quality checks |

## Requirements

Install the development dependency groups from the repository root:

```bash
uv sync --group dev
```

## Links

- [PyAEDT documentation](https://aedt.docs.pyansys.com/)
- [PyAnsys developer's guide](https://dev.docs.pyansys.com/)
- [PyAnsys documentation style reference](https://dev.docs.pyansys.com/doc-style/index.html)
- [GitHub repository](https://github.com/ansys/pyaedt)
