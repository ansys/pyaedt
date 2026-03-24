---
name: 9_frequency_sweep
description: >
  Step 9 of the PyAEDT workflow: frequency sweeps (HFSS, Maxwell, Q3D only).
  Comes after solution setup (Step 8) and before validation & analysis (Step 10).
---

# Step 9 — Frequency Sweep

Applies to **HFSS**, **Maxwell**, and **Q3D** only. Always add at least one sweep — the adaptive solve gives results only at the solution frequency.

## 9.1 Sweep Types

| Type | Use when |
|---|---|
| `"Interpolating"` | Default — best speed/accuracy for wideband S-params |
| `"Fast"` | Narrowband exploration; fine-sampled field data |
| `"Discrete"` | Sharp filter responses, time-domain conversion, exact at every point |

## 9.2 Creating Sweeps

```python
# By step size
sweep = setup.create_linear_step_sweep(
    unit="GHz",
    start_frequency=1.0,
    stop_frequency=4.0,
    step_size=0.01,
    name="Sweep1",
    sweep_type="Interpolating",
    save_fields=False,
    save_rad_fields=True,
)

# By number of points
sweep = setup.create_frequency_sweep(
    unit="GHz",
    start_frequency=1.0,
    stop_frequency=4.0,
    num_of_freq_points=301,
    name="Sweep1",
    sweep_type="Interpolating",
    save_fields=False,
    save_rad_fields=True,
)

# Single point
sweep = setup.create_single_point_sweep(
    unit="GHz", freq=2.4, name="SinglePt", save_fields=True, save_rad_fields=True
)
```

## 9.3 Field Storage

- **`save_rad_fields=True`** — required for far-field reports (gain, directivity, EIRP, axial ratio). Always enable for antenna designs.
- **`save_fields=True`** — stores full E/H at every frequency. Large files — enable only when field plots / SAR at swept frequencies are needed.
