---
name: pyaedt-workflow-agent
description: Use when the user wants to build, structure, or organize any PyAEDT automation script.
---

# PyAEDT Workflow Assistant

Orchestrates the structure and sequencing of PyAEDT automation scripts. Operates in two modes:

- **Mode A — Full Pipeline**: all 11 steps in order (user asks to build a complete project from scratch).
- **Mode B — Targeted Operation**: only the relevant step(s) (user asks to add/modify a specific aspect).

For each step, dispatch to the corresponding agent listed in Section 2.

---

## 1. Usage Modes

### Choosing the Mode
1. User provides an **existing script** and asks for a specific change → **Mode B** (dispatch only to relevant agent)
2. User asks to **create / build / generate** a complete simulation from scratch → **Mode A** (all 11 steps)
3. If ambiguous, ask the user.

**Key principle**: Ordering rules (Section 3) always apply to whichever steps are active, but unneeded steps are skipped entirely in Mode B.

---

## 2. Pipeline & Agent Dispatch

```
Step  | Description                          | Agent
------|--------------------------------------|--------------------------------------
  1   | Environment setup, settings          | 1_environment_setup
  2   | HFSS session initialization          | 2_session
  3   | Design variables                     | 3_design_variables
  4   | Geometry creation                    | 4_geometry_creation
  5   | Material assignment                  | 5_material_assignment
  6   | Boundary conditions                  | 6_boundary_conditions
  7   | Excitations (ports)                  | 7_excitations_ports
  8   | Solution setup                       | 8_solution_setup
  9   | Frequency sweep                      | 9_frequency_sweep
 10   | Validation & analysis                | 10_validation_analysis
 11   | Post-processing & reports            | 11_post_processing
```

---

## 3. Ordering Rules

These govern the **relative order** of whichever steps are active (both modes):

1. **Variables → Geometry** — Step 3 before Step 4
2. **Materials → Boundaries** — Step 5 before Step 6
3. **Boundaries → Ports** — Step 6 before Step 7
4. **Ports → Setup** — Step 7 before Step 8
5. **Setup → Sweep** — Step 8 before Step 9
6. **Sweep → Analysis** — Step 9 before Step 10
7. **Analysis → Reports** — Step 10 before Step 11
8. **Error handling wraps Steps 3–11** (try/finally or context manager from Step 2)

---

## 4. Configuration Export

PyAEDT can export a full design configuration (variables, setups, boundaries, materials, mesh, objects) to a JSON file that follows `config.schema.json`. Use this instead of manually serialising design state:

```python
# Export — produces a JSON file matching config.schema.json
config_path = hfss.configurations.export_config("my_design.json")

# Import into a new/existing design
hfss.configurations.import_config("my_design.json")
```

Fine-tune what gets exported via `hfss.configurations.options`:

```python
hfss.configurations.options.export_variables = True
hfss.configurations.options.export_setups = True
hfss.configurations.options.export_boundaries = True
hfss.configurations.options.export_mesh_operations = True
hfss.configurations.options.export_materials = True
hfss.configurations.options.export_object_properties = True
```

Use `export_config` whenever you need to snapshot a design state. Do **not** hand-craft YAML or JSON to represent design configuration.
