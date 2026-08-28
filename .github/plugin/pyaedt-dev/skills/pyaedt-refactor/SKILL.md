---
name: pyaedt-refactor
description: Use when modifying, cleaning up, deprecating, or removing existing PyAEDT code. Triggers on requests to refactor a PyAEDT module, improve poorly written or undocumented code, rename or change a public API, fix a bug in existing code, or review a change for backward compatibility.
---

# PyAEDT refactoring skill

PyAEDT is a widely used public API. Changes to existing code must be surgical, backward compatible,
and approved when they go beyond the user's request.

## Approval gate for opportunistic cleanup

Poorly written or poorly documented code **should** be improved, but you must get explicit user
approval before making the change. When you spot such code:

1. Stop before editing.
2. Report: the file and symbol, what is wrong (missing docstring, dead code, duplicated logic,
   unsafe error handling, and so on), the proposed fix, and the blast radius (callers, public API,
   tests affected).
3. Ask the user whether to proceed, and wait for the answer.
4. Only then apply the change.

Never bundle unapproved cleanup into a functional change. Fixes that are *directly caused by* or
*tightly coupled to* the requested change do not need a separate approval, but say so in the summary.

## Surgical diff rules

- Change only what the task requires. No drive-by reformatting of untouched lines.
- Do not reorder imports, rewrap strings, or restyle code that you are not otherwise editing;
  `ruff format` handles formatting on the lines you touch.
- Do not move modules, rename files, or restructure packages without an explicit user request.
- Keep the diff readable: prefer extending an existing function over replacing it wholesale.
- Preserve existing behavior for every currently documented input.

## Public API compatibility

Anything importable from `ansys.aedt.core` is public. When changing it:

- **Do not** rename or remove a public function, method, property, or keyword argument outright.
- Add new behavior through new optional keyword arguments with defaults that preserve today's
  results.
- Use the existing deprecation helpers instead of hand-rolled warnings:

  ```python
  from ansys.aedt.core.generic.general_methods import deprecate_argument
  from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


  # pyaedt_function_handler maps a deprecated keyword to its replacement
  @pyaedt_function_handler(old_name="new_name")
  @deprecate_argument("legacy_arg", version="1.0")
  def do_something(self, new_name=None, legacy_arg=None): ...
  ```

- Guard version-dependent behavior with `min_aedt_version` from
  `ansys.aedt.core.internal.checks`.
- Document deprecations in the docstring, with the deprecation note placed before the extended
  summary (numpydoc check `GL09`).
- Raise the PyAEDT error types from `ansys.aedt.core.internal.errors` (for example
  `AEDTRuntimeError`) rather than bare `Exception`.

## Reuse while refactoring

If the refactor reveals duplicated logic, consolidate into the correct package per the
`pyaedt-code-placement` skill (usually `generic` for AEDT-agnostic helpers, `internal` for native API
wrappers). Consolidation that changes call sites needs the approval gate above.

## Verification loop

After every set of edits:

```bash
ruff format .
ruff check .
ty check
pytest <the smallest selector covering the change> -q
```

Also confirm:

- [ ] Existing tests that cover the changed code still pass, and were **updated rather than
      duplicated** when behavior legitimately changed.
- [ ] Docstrings for the changed symbols still describe reality, including `Parameters`, `Returns`,
      and `Raises`.
- [ ] No public symbol was removed or renamed without a deprecation path.
- [ ] `doc/source/API` still matches the public surface.
- [ ] A changelog fragment was added (see the `pyaedt-contribution` skill).
