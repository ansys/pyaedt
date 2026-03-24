---
name: 8_solution_setup
description: >
  Step 8 of the PyAEDT workflow: adaptive solution setup and mesh refinement.
  Comes after excitations (Step 7) and before frequency sweep (Step 9).
---

# Step 8 — Solution Setup

## 8.1 Creating the Setup

```python
setup = app.create_setup(name="Setup1")
setup.props["Frequency"] = "2.4GHz"  # adaptive frequency
setup.props["MaximumPasses"] = 15
setup.props["MinimumPasses"] = 2
setup.props["MinimumConvergedPasses"] = 2
setup.props["PercentRefinement"] = 30
setup.props["BasisOrder"] = -1  # -1=mixed, 1=1st order, 2=2nd order
setup.props["DeltaS"] = 0.02  # S-param convergence criterion
setup.update()
```

**Adaptive frequency:** use resonant freq for narrowband, center of band for broadband, highest freq for transmission lines / waveguides.

## 8.2 Multi-Frequency Adaptive (Wideband >40% BW)

```python
setup.props["MultipleAdaptiveFreqsSetup"] = {
    "1GHz": [0.02],  # [DeltaS] at low end
    "2.4GHz": [0.02],  # center
    "4GHz": [0.02],  # high end
}
setup.update()
```

Include at minimum the lowest and highest operating frequencies. Expect more passes than single-frequency.

## 8.3 Mesh Refinement

Seed mesh on features smaller than λ/10 — the adaptive algorithm may not resolve them automatically.

```python
app.mesh.assign_length_mesh(
    assignment=["feed_gap_sheet"],
    inside_selection=True,
    max_length=0.3,
    name="FeedGapMesh",
)

app.mesh.assign_skin_depth_mesh(
    assignment=["patch", "ground"],
    skin_depth="0.0013mm",
    triangulation_max_length=0.5,
    name="SkinDepthMesh",
)
```
