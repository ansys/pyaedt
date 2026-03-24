---
name: 11_post_processing
description: >
  Step 11 of the PyAEDT workflow: post-processing reports.
  Comes after validation & analysis (Step 10). Final step.
---

# Step 11 — Post-Processing & Reports

## 11.1 `create_report` API

```python
app.post.create_report(
    expressions="dB(S(1,1))",  # str or list of expressions
    setup_sweep_name=None,  # "Setup1 : Sweep1" — defaults to first
    domain="Sweep",  # "Sweep" | "Time" | "DCIR"
    variations=None,  # e.g. {"Freq": ["All"], "Theta": ["All"]}
    primary_sweep_variable="Freq",
    secondary_sweep_variable=None,  # for 3D plots
    report_category=None,  # "Modal S Parameter", "Far Fields", "Fields", etc.
    plot_type="Rectangular Plot",  # "Smith Chart", "Radiation Pattern", "3D Polar Plot", etc.
    context=None,  # infinite sphere name (far-field) | "3D" | polyline name
    plot_name=None,
)
```

## 11.2 Common Expressions

| Expression | Description |
|---|---|
| `dB(S(1,1))` | Return loss (dB) |
| `dB(S(2,1))` | Insertion loss (dB) |
| `ang_deg(S(2,1))` | Phase (degrees) |
| `S(1,1)` | Complex (for Smith Chart) |
| `re(Zin(Port1,Port1))`, `im(Zin(Port1,Port1))` | Input impedance |
| `VSWR(Port1)` | VSWR |
| `GainTotal` | Far-field gain |
| `Peak Realized Gain` | Peak gain vs frequency |
| `GroupDelay(Port1,Port2)` | Group delay |
| `re(Zo(Port1))` | Characteristic impedance |
| `Mag_E`, `Mag_H`, `Mag_Jsurf` | Field quantities (for field plots) |

Port references use the assigned port name or index shorthand: `S(1,1)`, `S(Port1,Port1)`.

## 11.3 Far-Field Reports

Requires `save_rad_fields=True` in the sweep.

```python
# Create infinite sphere cut
app.insert_infinite_sphere(
    definition="Elevation Over Azimuth",
    x_start=-180,
    x_stop=180,
    x_step=1,
    y_start=0,
    y_stop=0,
    plot_name="EPlane",
)

# 2D radiation pattern
app.post.create_report(
    expressions=["GainTotal"],
    primary_sweep_variable="Theta",
    report_category="Far Fields",
    plot_type="Radiation Pattern",
    context="EPlane",
    plot_name="FarField_EPlane",
)

# 3D polar plot
variations = app.available_variations.nominal_values
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
variations["Freq"] = ["2.4GHz"]
app.post.create_report(
    expressions=["GainTotal"],
    setup_sweep_name=app.nominal_adaptive,
    variations=variations,
    primary_sweep_variable="Phi",
    secondary_sweep_variable="Theta",
    report_category="Far Fields",
    plot_type="3D Polar Plot",
    context="3D",
    plot_name="FarField_3D",
)
```

## 11.4 Field Plots

```python
app.post.create_fieldplot_surface(
    assignment=["patch"],
    quantity="Mag_E",
    intrinsics={"Freq": "10GHz"},
    plot_name="EField",
)

app.post.create_fieldplot_cutplane(
    quantity="Mag_H",
    cut_plane="XY",
    offset=0,
    intrinsics={"Freq": "10GHz"},
    plot_name="HField_XY",
)
```

## 11.5 Report Selection by Problem Type

| Design type | Reports |
|---|---|
| Antenna | S11, Zin, VSWR, Smith Chart, 2D E/H-plane, 3D far-field, Peak Gain vs freq |
| Filter | S11, S21 (insertion loss), S22, group delay, S21 phase |
| Transmission line | Z0, propagation constant, S11, S21 |
| Resonant cavity | Eigenfrequencies, Q-factor |
| RCS | Monostatic RCS vs freq, bistatic pattern |
