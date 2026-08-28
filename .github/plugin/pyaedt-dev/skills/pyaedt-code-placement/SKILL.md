---
name: pyaedt-code-placement
description: Use when adding new classes, methods, functions, or static assets to the PyAEDT source tree, or when deciding which module or package a change belongs in. Triggers on requests to implement a new PyAEDT feature, add a utility, add a geometry operation, add a configuration schema, or wrap a native AEDT API call.
---

# PyAEDT code placement skill

New code must land in the package that matches its function and must match the existing structure of
`src/ansys/aedt/core`. Never reorganize the repository layout unless the user explicitly asks for it.

## Rule 0: reuse before you create

Creating new code is the last resort. Before writing anything:

1. Search for an existing implementation. Prefer symbol and code search over guessing.

   ```bash
   grep -rn "def <candidate_name>" src/ansys/aedt/core
   grep -rn "<domain keyword>" src/ansys/aedt/core --include=*.py
   ```

2. If a function does most of what is needed, extend it (new optional keyword argument with a
   backward-compatible default) instead of writing a near-duplicate.
3. If two candidate helpers already exist, use the one in the most general package and do not add a
   third.
4. Only if nothing suitable exists, add new code, in the smallest possible unit, in the package
   chosen with the map below.

If reuse requires changing existing code, follow the `pyaedt-refactor` skill: propose the change and
get user approval first.

## Placement map

| Location | What belongs there |
|---|---|
| `src/ansys/aedt/core/application` | Application setup, settings, design and solution workflow. Anything that configures an AEDT application object or drives the solve process. |
| `src/ansys/aedt/core/generic` | General-purpose utilities with no AEDT-specific behavior: file system helpers, math and number utilities, data handlers, settings and logging infrastructure. |
| `src/ansys/aedt/core/misc` | Static data only: JSON schemas, general configuration files, and other static settings consumed by PyAEDT. No business logic. |
| `src/ansys/aedt/core/internal` | Low-level functions that simplify the interface to the native AEDT API, plus internal checks and guards. Thin wrappers, not user-facing workflows. |
| `src/ansys/aedt/core/modeler` | Geometric operations and any command that modifies or manipulates the geometry of an AEDT model. |
| `src/ansys/aedt/core/modeler/cad` | Classes and methods for geometric operations: primitives, objects, components, coordinate systems. |
| `src/ansys/aedt/core/modeler/advanced_cad` | Advanced, application-specific geometry creation, such as twisted-pair cables or other geometrically complex model builders. |

Other existing packages, listed so that you use them instead of inventing new locations:

| Location | What belongs there |
|---|---|
| `src/ansys/aedt/core/cli` | The `pyaedt` command-line interface. |
| `src/ansys/aedt/core/modules` | Solution setups, boundaries, materials, mesh, and post-processing modules. |
| `src/ansys/aedt/core/visualization` | Plotting, reports, and post-processing visualization. |
| `src/ansys/aedt/core/extensions` | AEDT toolkit extensions and their installers. |
| `src/ansys/aedt/core/emit_core` | EMIT-specific logic. |
| `src/ansys/aedt/core/filtersolutions_core` | Filter Solutions logic. |
| `src/ansys/aedt/core/rpc` | Remote procedure call server and client. |
| `src/ansys/aedt/core/examples` | Example downloaders and sample data helpers. |
| `src/ansys/aedt/core/syslib` | Shipped binary/system libraries. Do not add Python logic here. |

## Decision procedure

Ask these questions in order and stop at the first match:

1. Is it static data (schema, JSON, configuration file)? → `misc`
2. Is it a thin wrapper over a native AEDT API call? → `internal`
3. Does it create or modify model geometry?
   - Complex, application-specific builder → `modeler/advanced_cad`
   - General geometric operation or CAD entity → `modeler/cad`
   - Other modeler-level operation → `modeler`
4. Does it configure the application, its settings, or the solution process? → `application`
5. Is it solution setup, boundary, material, mesh, or post-processing data? → `modules`
6. Is it plotting or reporting? → `visualization`
7. Is it AEDT-agnostic? → `generic`

If none of these fit, ask the user rather than creating a new top-level package.

## Pre-write checklist

Before adding code, confirm all of the following:

- [ ] An equivalent helper does not already exist (Rule 0 search was run).
- [ ] The owning package was selected with the decision procedure above.
- [ ] The target module already groups related behavior; a new module is created only when no
      existing module is a reasonable home.
- [ ] Public API surface is intentional: if the symbol is meant to be public, it is exported from
      the appropriate `__init__.py` and documented under `doc/source/API`.
- [ ] Imports follow the repository isort configuration (see the `pyaedt-docstrings` skill).
- [ ] The new behavior is documented and tested (see `pyaedt-docstrings` and `pyaedt-testing`).

## Anti-patterns

- Adding a `utils.py`, `helpers.py`, or `common.py` module next to the caller instead of using
  `generic`.
- Putting AEDT-specific logic in `generic`, or AEDT-agnostic math in `application`.
- Putting Python logic in `misc`, which is reserved for static data.
- Duplicating a modeler operation in an application class because the modeler API was not searched.
- Moving or renaming existing modules to "clean things up" without an explicit user request.
