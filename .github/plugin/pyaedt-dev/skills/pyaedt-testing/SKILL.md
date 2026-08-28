---
name: pyaedt-testing
description: Use when adding or updating tests for PyAEDT code. Triggers on requests to test new PyAEDT functionality, choose between a unit, integration, or system test, pick a pytest marker, mock an AEDT session, or run a targeted subset of the PyAEDT test suite.
---

# PyAEDT testing skill

Every new or changed behavior must be covered by a test. **Prefer modifying an applicable existing
test over creating a new one.** A new test module is justified only when no existing module covers
the area.

## Where tests live

| Path | Scope |
|---|---|
| `tests/unit` | Pure Python tests. No AEDT installation, no live desktop session. |
| `tests/unit/extensions` | Unit tests for AEDT toolkit extensions. |
| `tests/integration` | Tests that cross component boundaries but still avoid a full solve. |
| `tests/system/general` | System tests against a live AEDT session, general features. |
| `tests/system/layout` | Layout and 3D Layout / EDB-oriented system tests. |
| `tests/system/solvers` | Solver-driven system tests, including `tests/system/solvers/sequential`. |
| `tests/system/icepak` | Icepak system tests. |
| `tests/system/visualization` | Plotting, reports, and post-processing system tests. |
| `tests/system/extensions` | Extension system tests. |
| `tests/system/emit` | EMIT system tests. |
| `tests/system/filter_solutions` | Filter Solutions system tests. |

Test data files belong in the `example_models` (or `resources`) folder of the owning test package.
Do not add binary models to `tests/unit`.

## Choosing the right level

1. Can the behavior be exercised with plain Python objects or mocks? → **unit test**. This is the
   default and the fastest feedback loop.
2. Does it need several PyAEDT components wired together but no AEDT process? → **integration test**.
3. Does it genuinely require a running AEDT session or a solve? → **system test**, in the
   subdirectory matching the product area.

Unit tests must never launch AEDT. Use `unittest.mock` / the `mock` package (already a test
dependency) to patch the desktop, the modeler, or the native API objects.

```python
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.internal.errors import AEDTRuntimeError

TARGET = "ansys.aedt.core.modeler.cad.primitives_3d.Primitives3D.oeditor"


@patch(TARGET, new_callable=MagicMock)
def test_create_box_invalid_sizes_raises(mock_editor, modeler):
    with pytest.raises(AEDTRuntimeError):
        modeler.create_box([0, 0, 0], [0, 0, 0])
```

## Markers

Only these markers are registered in `pyproject.toml`. Using an unregistered marker fails the
configuration:

`unit`, `integration`, `system`, `solvers`, `general`, `visualization`, `extensions`,
`filter_solutions`, `emit`, `avoid_ansys_load`

Apply the level marker plus, where relevant, the area marker:

```python
pytestmark = [pytest.mark.unit, pytest.mark.general]
```

## What to cover

For each new public function, class, or method:

- The nominal path, asserting the returned value or the resulting state.
- Each documented `Raises` entry.
- Each meaningful branch introduced by a new optional argument.
- Boundary conditions for numeric or geometric inputs.

For a bug fix, add or extend a test that fails before the fix and passes after it.

## Running tests

Run the smallest command that covers the change:

```bash
# One file
pytest tests/unit/test_general_methods.py -q

# One test
pytest tests/unit/test_general_methods.py::test_deprecate_argument -q

# All unit tests
pytest tests/unit -m unit -q
```

Do not run the system test suites unless a live AEDT installation is available and the user asked
for it; they are slow and require licensing.

## Checklist

- [ ] An existing test module was checked first and extended if applicable.
- [ ] The test level (unit / integration / system) matches the dependency on AEDT.
- [ ] Only registered markers are used.
- [ ] Unit tests pass without AEDT installed.
- [ ] The targeted pytest command was actually run and passes.
