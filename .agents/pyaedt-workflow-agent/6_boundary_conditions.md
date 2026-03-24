---
name: 6_boundary_conditions
description: >
  Step 6 of the PyAEDT workflow: assigning boundary conditions.
  Comes after material assignment (Step 5) and before excitations (Step 7).
---

# Step 6 — Boundary Conditions

Boundaries must be assigned **before** excitations (ports).

## 6.1 Free-Space Boundaries (Antennas / Open Structures)

Placed on the outer faces of the air/vacuum region. Mandatory for any radiating structure.

```python
# ABC (radiation boundary) — simplest, most common
app.assign_radiation_boundary_to_objects("rad_box")

# PML — better absorption at steep angles / near-field accuracy
app.create_open_region(frequency="1GHz", boundary="PML", apply_infinite_ground=False)

# FEBI — electrically large structures, convex/concave air volumes
app.assign_febi(assignment="rad_box", name="febi_region")

# create_open_region works for all three types:
app.create_open_region(
    frequency="1GHz", boundary="Radiation", apply_infinite_ground=False
)
app.create_open_region(frequency="1GHz", boundary="FEBI", apply_infinite_ground=False)
```

**Spacing rules:** ABC / PML faces ≥ λ/4 from nearest radiating surface; PML surface ≥ λ/6; FEBI must not touch any geometry objects. FEBI cannot be used with symmetry planes.

## 6.2 Finite Conductivity

For thin conductor sheets (PCB traces thinner than skin depth):

```python
app.assign_finite_conductivity(
    assignment="trace_sheet",
    material="copper",
    use_thickness=True,
    thickness="0.035mm",
    name="copper_bc",
)
# OR with explicit values
app.assign_finite_conductivity(
    assignment=face_ids, conductivity=5.8e7, permittivity=1, name="copper_bc"
)
```

Optional: `is_infinite_ground`, `is_two_side`, `roughness`, `use_huray`, `radius`, `ratio`.

## 6.3 Impedance Boundary

```python
app.assign_impedance_to_faces(
    face_list, resistance=0.1, reactance=0.0, name="wall_impedance"
)
```

## 6.4 Perfect E (PEC)

```python
app.assign_perfect_e(assignment="ground_plane", name="pec_ground")
```

Not needed if the object is a 3D solid with PEC material — HFSS applies it automatically. For symmetry reduction use Section 6.5 instead.

## 6.5 Symmetry Planes

Halves the solution domain per plane. **Both geometry and fields must be symmetric.**

```python
app.assign_perfecte_to_faces(face_ids, name="PEC_Symmetry_YZ")  # E_t = 0
app.assign_perfecth_to_faces(face_ids, name="PMC_Symmetry_XZ")  # H_t = 0
```

| Symmetry | Condition | Use when |
|---|---|---|
| PEC | E_t = 0 | E-field ⊥ to symmetry plane |
| PMC | H_t = 0 | H-field ⊥ to symmetry plane |
