---
name: pyaedt-docstrings
description: Use when writing, reviewing, or fixing docstrings, type hints, imports, or formatting in the PyAEDT source tree. Triggers on requests to document a PyAEDT function or class, follow the PyAnsys documentation style, satisfy numpydoc validation, fix ruff or pydocstyle findings, or add a new public API entry to the documentation.
---

# PyAEDT documentation and style skill

All PyAEDT code must be documented with numpydoc docstrings that follow the
[PyAnsys documentation style reference](https://dev.docs.pyansys.com/doc-style/index.html), and must
satisfy PEP 8 as enforced by ruff. The style is consistent with NumPy, SciPy, and pandas.

Everything below reflects the configuration that already exists in `pyproject.toml` and
`.pre-commit-config.yaml`. Do not invent additional style rules.

## Docstring rules

Write a docstring for every public module, class, method, function, and property you add or change.

Required shape:

- One-line summary, starting with a capital letter, ending with a period, written in the
  **infinitive** ("Return the...", not "Returns the...").
- Blank line, then an optional extended summary.
- `Parameters`, `Returns`, `Raises`, `References`, `Examples` sections, in that order, only when
  they apply.
- Every parameter documented with `name : type` (space before the colon) and, for optional
  arguments, `, optional` plus the default stated in the description as ``` ``value`` ```.
- Return descriptions start with a capital letter and end with a period.
- Cross-reference AEDT API calls in a `References` section when the method wraps one.

Template:

```python
@pyaedt_function_handler()
def create_box(self, origin, sizes, name=None, material="vacuum"):
    """Create a box.

    Parameters
    ----------
    origin : list of float
        Anchor point of the box in ``[x, y, z]`` coordinates.
    sizes : list of float
        Length of the box edges in ``[dx, dy, dz]``.
    name : str, optional
        Name of the box. The default is ``None``, in which case a
        name is automatically assigned.
    material : str, optional
        Material to assign to the box. The default is ``"vacuum"``.

    Returns
    -------
    :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`
        3D object.

    Raises
    ------
    AEDTRuntimeError
        If the box cannot be created.

    References
    ----------
    >>> oEditor.CreateBox

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss()
    >>> box = hfss.modeler.create_box([0, 0, 0], [10, 10, 5], name="my_box")
    """
```

## numpydoc validation checks that are enforced

`[tool.numpydoc_validation]` in `pyproject.toml` enables these checks. Satisfy all of them:

| Check | Requirement |
|---|---|
| `GL06` | No unknown sections. |
| `GL07` | Sections in the canonical order. |
| `GL08` | The object has a docstring. |
| `GL09` | Deprecation warning precedes the extended summary. |
| `GL10` | reST directives are followed by two colons. |
| `RT04` | Return description starts with a capital letter. |
| `RT05` | Return description ends with a period. |
| `SS01` | A summary is present. |
| `SS02` | Summary starts with a capital letter. |
| `SS03` | Summary ends with a period. |
| `SS04` | Summary has no leading whitespace. |
| `SS05` | Summary starts with an infinitive verb, not third person. |
| `PR10` | A space precedes the colon between parameter name and type. |

## Coding style

Enforced by ruff (`ruff check`, `ruff format`):

- Line length: **120**.
- Quote style: **double**. Indentation: spaces. Docstring code is formatted.
- Selected rule sets: `D` (pydocstyle, numpy convention), `E`/`W` (pycodestyle), `F` (pyflakes),
  `I` (isort), `N` (pep8-naming), `PTH` (use `pathlib`), `TD` (todos), and `UP006`, `UP007`, `UP045`.
- Prefer `pathlib.Path` over the `os.path` functions that are not in the ignore list; new code
  should use `pathlib` throughout.
- Use modern typing: `list[str]` instead of `List[str]`, `str | None` instead of `Optional[str]`.
  Add `from __future__ import annotations` at the top of new modules that use these forms on
  Python 3.10.
- Naming: `snake_case` for functions and variables, `PascalCase` for classes, leading underscore for
  private helpers.
- Do not leave `print` or debug statements; the `debug-statements` pre-commit hook fails on them.
- `TODO` comments must include an author and a link, otherwise `TD002`/`TD003` fail.

## Import ordering

isort is configured with `force-sort-within-sections = true` and `force-single-line = true`, with
first-party packages `doc`, `src/ansys/aedt/core`, and `tests`. One import per line, alphabetically
sorted within each section:

```python
from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError
```

Never write `from module import a, b`. Never reorder imports by hand; run `ruff format` and
`ruff check --fix`.

## License header

Every new `.py` file under `src`, `tests`, `doc`, or `examples` needs the MIT header applied by the
`add-license-headers` pre-commit hook (start year 2021). Run the hook rather than typing the header
manually:

```bash
prek run add-license-headers --all-files
```

## Documenting the public API

If you add a public class, method, or function, also update the reStructuredText files under
`doc/source/API` so the symbol appears in the rendered documentation. If you add user-facing
behavior, check whether `doc/source/User_guide` needs an update too.

## Verification

Run before declaring the work done:

```bash
ruff format .
ruff check .
ty check
```
