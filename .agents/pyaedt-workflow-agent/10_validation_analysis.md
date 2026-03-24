---
name: 10_validation_analysis
description: >
  Step 10 of the PyAEDT workflow: validate the design and run the simulation.
  Comes after frequency sweep (Step 9) and before post-processing (Step 11).
---

# Step 10 — Validation & Analysis

## 10.1 Validate and Solve

```python
# Always validate before solving
validation = app.validate_simple()

# Run a specific setup
app.analyze_setup("Setup1")

# OR all setups / with HPC cores
app.analyze_all()
app.analyze_setup("Setup1", num_cores=8)
```

## 10.2 Post-Solve Convergence Check

```python
convergence = app.get_setup("Setup1").get_convergence_data()
```

If the solver hit `MaximumPasses` without converging, increase passes or add mesh seeding on critical features.
