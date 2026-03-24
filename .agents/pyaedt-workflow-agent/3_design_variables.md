---
name: 3_design_variables
description: >
  Step 3 of the PyAEDT workflow: defining parametric design variables.
  Must come before geometry creation (Step 4).
---

# Step 3 — Design Variables

Variables must be defined **before** any geometry that references them.

```python
# Syntax: app["name"] = "value_with_unit"
app["freq"] = "2.4GHz"
app["lam"] = "c0 / freq * 1000"  # expression — c0 (m/s), result in mm
app["arm_len"] = "lam * 0.235"  # expressions can reference other variables
app["feed_gap"] = "1.0mm"
app["box_pad"] = "lam / 4"  # λ/4 padding for radiation box

# Read back
value = app["arm_len"]  # returns string e.g. "29.35mm"
```

**Rules:**
- Always use variables for geometry dimensions — required for parametric sweeps
- Units must be in the string: `mm`, `GHz`, `deg`, `ohm`, `mil`, `cm`
- Built-in constants in expressions: `c0`, `pi`, `eps0`, `mu0`
- Names: letters, digits, underscores only — no spaces or special characters
