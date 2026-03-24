---
name: 5_material_assignment
description: >
  Step 5 of the PyAEDT workflow: assigning materials to geometry objects.
  Comes after geometry creation (Step 4) and before boundary conditions (Step 6).
---

# Step 5 — Material Assignment

Every object must have the correct material **before** defining boundaries or ports.

## 5.1 Library Materials

```python
obj.material_name = "copper"
app.modeler["my_box"].material_name = "Rogers RO4003C (tm)"
```

Common names: `"copper"`, `"aluminum"`, `"gold"`, `"pec"`, `"FR4_epoxy"`, `"Rogers RO4003C (tm)"`, `"Rogers RT5880 (tm)"`, `"Teflon (tm)"`, `"air"`, `"vacuum"`

## 5.2 Custom Materials

```python
mat = app.materials.add_material("my_substrate")
mat.permittivity = 3.55  # ε_r
mat.dielectric_loss_tangent = 0.0027  # tan δ
mat.permeability = 1.0  # μ_r
mat.conductivity = 0  # S/m — 0 for dielectrics
```

Frequency-dependent properties — pass `[freq_Hz, value]` pairs:

```python
mat.permittivity = [[1e9, 4.4], [5e9, 4.3], [10e9, 4.2]]
```

## 5.3 Searching the Library

When the user gives an informal name (e.g. "plastic", "glass"):

```python
matches = [m for m in app.materials.mat_names_aedt if "plastic" in m.lower()]
```

If no match, create a custom material with representative properties and tell the user the assumed values.

## 5.4 Verification

```python
for name in app.modeler.object_names:
    print(f"{name}: {app.modeler[name].material_name}")
```
