---
name: 4_geometry_creation
description: >
  Step 4 of the PyAEDT workflow: creating 3D geometry — primitives, Booleans, CAD import,
  coordinate systems. Comes after design variables (Step 3) and before material assignment (Step 5).
---

# Step 4 — Geometry Creation

## 4.1 Units

```python
app.modeler.model_units = "mm"  # set once before any geometry call
```

## 4.2 Primitives

Always use design variables (Step 3) for tunable dimensions — never hardcode numbers.

```python
box = app.modeler.create_box(
    origin=["-sub_len/2", "-sub_wid/2", "-sub_h"],
    sizes=["sub_len", "sub_wid", "sub_h"],
    name="substrate",
    material="FR4_epoxy",
)

cyl = app.modeler.create_cylinder(
    orientation="Z", origin=[0, 0, 0], radius="wire_dia/2", height="arm_len", name="arm"
)

rect = app.modeler.create_rectangle(
    orientation="XY",
    origin=["-patch_len/2", "-patch_wid/2", "0mm"],
    sizes=["patch_len", "patch_wid"],
    name="patch",
)

poly = app.modeler.create_polyline(
    points=[[0, 0, "-arm_len"], [0, 0, "arm_len"]],
    segment_type="Line",
    name="dipole_wire",
)
```

Other primitives: `create_sphere`, `create_cone`, `create_ellipse`, `create_helix` — same pattern.

## 4.3 Boolean Operations

```python
app.modeler.unite([obj1, obj2])  # merge — obj1 name survives
app.modeler.subtract(blank, [tool])  # tool consumed, blank modified in place
app.modeler.intersect([obj1, obj2])  # keep overlapping volume only
app.modeler.split(obj, "XY")  # split by plane
app.modeler.duplicate_mirror(obj, axis)
app.modeler.duplicate_along_line(obj, vector, count)
```

## 4.4 CAD Import

```python
app.modeler.import_3d_cad(
    r"C:\path\to\model.step", healing=True, import_materials=False
)
# Supported: .step, .iges, .sat, .x_t, .stl — assign materials manually after import
```

## 4.5 Coordinate Systems

```python
cs = app.modeler.create_coordinate_system(
    origin=[10, 0, 0], x_pointing=[1, 0, 0], y_pointing=[0, 1, 0], name="my_cs"
)

cs_child = app.modeler.create_coordinate_system(
    origin=[0, 1, 0],
    reference_cs=cs.name,
    name="child_cs",
    mode="zxz",
    psi=25,
    theta=40,
    phi=0,
)
```

## 4.6 Object Properties

```python
obj.color = (255, 0, 0)  # RGB
obj.transparency = 0.5  # 0 = opaque, 1 = fully transparent
app.modeler.create_group(assignment=["obj1", "obj2"], name="antenna_group")
```
