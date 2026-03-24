---
name: 2_session_init
description: >
  Step 2 of the PyAEDT workflow: session initialization and teardown for any PyAEDT application.
  Covers new project, attach to running session, open existing file, solution type selection,
  and safe cleanup. Comes after Step 1 (environment setup) and before Step 3 (design variables).
---

# Step 2 — Session Initialization

> **CLI first**: use `pyaedt-cli-agent` to launch or connect to AEDT before running a script.
> In that case, attach with `new_desktop=False` (Mode B below).

## 2.1 Application Classes

| App            | Class               |
|----------------|---------------------|
| HFSS           | `aedt.Hfss`         |
| Maxwell 3D     | `aedt.Maxwell3d`    |
| Maxwell 2D     | `aedt.Maxwell2d`    |
| Q3D Extractor  | `aedt.Q3d`          |
| Icepak         | `aedt.Icepak`       |
| Circuit        | `aedt.Circuit`      |
| HFSS 3D Layout | `aedt.Hfss3dLayout` |
| Mechanical     | `aedt.Mechanical`   |
| Emit           | `aedt.Emit`         |

All share the same constructor signature and teardown pattern below.

## 2.2 Initialization Modes

```python
# Mode A — new project (automation / CI)
app = aedt.Hfss(
    project=project_name,
    design=design_name,
    solution_type="Modal",
    version=aedt_version,
    non_graphical=non_graphical,
    new_desktop=True,
)

# Mode B — attach to running AEDT (after pyaedt-cli-agent launched it)
app = aedt.Hfss(project=project_name, design=design_name, new_desktop=False)

# Mode C — open existing .aedt file
app = aedt.Hfss(
    project=r"C:\path\to\project.aedt", design=design_name, new_desktop=True
)
```

Replace `aedt.Hfss` with the relevant class from Section 2.1. `solution_type` is app-dependent — omit it to use the app default.

## 2.3 Solution Types (HFSS)

| Type | Use when |
|---|---|
| `"Modal"` | Antennas, waveguides — default |
| `"Terminal"` | Multi-conductor / mixed feeds |
| `"Eigenmode"` | Resonant cavity Q-factor, no ports |
| `"Transient"` | Time-domain / pulse excitation |
| `"SBR+"` | Electrically large platforms |

## 2.4 Teardown — always required

Prefer the context manager; it releases the desktop automatically on exit or exception:

```python
with aedt.Hfss(
    project=project_name,
    design=design_name,
    solution_type="Modal",
    version=aedt_version,
    non_graphical=non_graphical,
    new_desktop=True,
) as app:
    # Steps 3–11 go here
    app.save_project()
# desktop released automatically — even on unhandled exceptions
```

If context manager is unavailable, use `try/finally`:

```python
app = None
try:
    app = aedt.Hfss(...)
    app.save_project()
finally:
    if app:
        app.release_desktop(close_projects=True, close_desktop=True)
```

- `close_projects=False, close_desktop=False` — keep GUI open for interactive inspection
- `close_projects=True, close_desktop=True` — clean shutdown for CI/automation
