# Light panels design

## Problem

`pyaedt panels add` currently installs the full PyAEDT panel set, and the Console entry is only available inside the grouped "PyAEDT Utilities" button. We need a light install mode that registers a smaller set of panels and makes the Console appear as a standalone item.

## Goals

- Add a `--light` option to `pyaedt panels add`.
- Route the feature through `add_pyaedt_to_aedt` with a new `light` parameter.
- In light mode, install only:
  - Console
  - Extension Manager
  - Version Manager by default
- Keep `--skip-version-manager` working in light mode so Version Manager can still be omitted.
- Register Console as a standalone panel item in light mode instead of placing it inside the utilities button group.

## Non-goals

- Changing the default/full install layout.
- Refactoring the installer into a generic preset system.
- Changing reset, path validation, or existing failure handling beyond what is required for the new flag.

## Current behavior

- `src\ansys\aedt\core\cli\panels.py` exposes `pyaedt panels add`.
- The CLI forwards installation to `add_pyaedt_to_aedt(personal_lib=..., skip_version_manager=...)`.
- `src\ansys\aedt\core\extensions\installer\pyaedt_installer.py` builds the installed entries.
- The Console is currently added through `_install_utilities_group()`, which creates the grouped "PyAEDT Utilities" section containing Console, CLI, and Jupyter.

## Proposed design

### CLI changes

- Add a new boolean Typer option: `--light`.
- Pass `light=light` to `add_pyaedt_to_aedt(...)`.
- Keep `--skip-version-manager` independent so it applies in both full and light modes.
- Derive the success output in the CLI from the same input flags that define the requested install set:
  - full mode: grouped utilities, Run Script, Extension Manager, and optionally Version Manager
  - light mode: Console, Extension Manager, and optionally Version Manager
- Do not require the installer to return a richer payload for this feature; the existing boolean success contract remains unchanged.

### Installer changes

- Extend `add_pyaedt_to_aedt` with `light: bool = False`.
- Centralize mode selection inside the installer so the CLI remains a thin wrapper.

#### Full mode

- Preserve the existing behavior:
  - Install the grouped utilities entry containing Console, CLI, and Jupyter.
  - Install Run Script.
  - Install Extension Manager.
  - Install Version Manager unless `skip_version_manager=True`.

#### Light mode

- Do not call `_install_utilities_group()`.
- Register Console directly with `customize_automation_tab.add_script_to_menu(...)` as a standalone item.
- Do not pass `group_name` or `group_icon` when registering Console in light mode.
- Install Extension Manager.
- Install Version Manager unless `skip_version_manager=True`.
- Do not install CLI, Jupyter, or Run Script.

### Registration logic

- Reuse the existing catalog-driven metadata from `extensions_catalog.toml`.
- Keep all item resolution inside `add_pyaedt_to_aedt` so the list of installed entries and their layout are decided in one place.
- Prefer a small branch between full and light modes over a broader generalized preset abstraction because only one new preset is required.

## User-facing behavior

### Full install

- No behavior change.
- Success output continues to list the full set and only omits Version Manager when skipped.

### Light install

- The command installs only Console, Extension Manager, and Version Manager by default.
- If `--skip-version-manager` is also passed, the command installs only Console and Extension Manager.
- The success output reflects the actual installed set.

## Error handling

- Preserve all current validation and exception handling in the CLI:
  - missing or invalid `personal_lib`
  - nonexistent path
  - non-directory path
  - reset deletion failures
  - installer import failures
  - installer returning `False`
  - unexpected exceptions
- No silent fallback between light and full modes. If the requested install mode fails, the command fails.
- Treat registration as an all-or-fail operation at the command level:
  - if any required `add_script_to_menu(...)` call raises or the installer returns `False`, `pyaedt panels add` exits with failure
  - this feature does not introduce rollback or cleanup of entries that may have been written before the failure
  - the behavior stays aligned with the current installer contract rather than adding transactional semantics

## Testing

- Extend CLI tests in `tests\unit\test_cli.py` to cover:
  - `pyaedt panels add --light`
  - `pyaedt panels add --light --skip-version-manager`
  - updated success output for light mode
  - the new `light` argument being passed to `add_pyaedt_to_aedt`
- Preserve existing coverage for full mode and skip-version-manager behavior.
- Add installer-level tests for `add_pyaedt_to_aedt(..., light=True)` to verify:
  - Console is registered directly without a utilities group
  - Extension Manager is registered
  - Version Manager is registered unless skipped
  - CLI, Jupyter, and Run Script are not registered in light mode
  - full mode continues to use the grouped utilities path unchanged

## Approach rationale

### Recommended approach

Add `--light` at the CLI layer and `light` inside `add_pyaedt_to_aedt`, with the installer owning both the reduced panel set and the standalone Console layout.

### Alternatives considered

1. Handle all light branching in the CLI.
   - Rejected because it duplicates installer decisions and splits registration logic across layers.
2. Introduce a generic installer preset or arbitrary include-list API.
   - Rejected because it adds abstraction beyond the immediate need and increases surface area without a current requirement.

## Implementation boundaries

- Touch only the panels CLI, the PyAEDT installer helper, and directly related tests or user-facing documentation if needed.
- Keep unrelated panel registration behavior unchanged.
