---
name: 7_excitations_ports
description: >
  Step 7 of the PyAEDT workflow: excitations (ports).
  Comes after boundary conditions (Step 6) and before solution setup (Step 8).
---

# Step 7 — Excitations (Ports)

Most rule-governed step — port violations cause incorrect or non-converging simulations.

## 7.1 Wave Port

```python
app.create_wave_port(
    assignment=face_id,
    name="Port1",
    num_modes=1,
    renormalization_impedance=50,
    deembed=False,
)
```

- Must lie on the solution region boundary **or** be backed by a PEC object of the same size when internal.
- Integration line recommended for Driven Modal (ground → signal) to define voltage path.
- Sizing: microstrip → 8–10× trace width, 4–6× substrate height; waveguide → exact cross-section.

## 7.2 Lumped Port

```python
app.create_lumped_port(
    assignment=sheet_or_face,
    name="LumpedPort1",
    impedance=50,
    integration_line=[[x1, y1, z1], [x2, y2, z2]],
    renormalization=True,
)
```

- Must be **internal** — bridges two conductors (or conductor to ground).
- Must not be inside or completely covered by a conductor.
- Integration line required for Driven Modal (ground → signal direction).

## 7.3 Incident Wave

```python
app.assign_incident_wave_excitation(
    wave_type="Plane Wave",
    vector_E=[1, 0, 0],
    propagation_vector=[0, 0, -1],
    name="PlaneWave1",
)
```

## 7.4 Floquet Port

Requires master/slave boundary pair on opposing unit cell faces first.

```python
app.assign_floquet_port(
    assignment=top_face, name="FloquetPort1", num_modes=2, phase_delay="Scan"
)
```

## 7.5 Driven Modal vs Driven Terminal

| Aspect | Modal | Terminal |
|---|---|---|
| S-param basis | Waveguide modes | Conductor terminals |
| Integration line | Recommended on wave ports | Not applicable |
| Terminals | Not used | Required — auto-created per conductor |
| Best for | Waveguides, single-mode feeds | Differential pairs, circuit co-sim |

## 7.6 De-embedding (Wave Ports Only)

Removes electrical length between port face and reference plane. The line must be uniform over the de-embed distance.

```python
app.create_wave_port(
    assignment=face_id,
    name="Port1",
    num_modes=1,
    renormalization_impedance=50,
    deembed=True,
    deembed_distance="5mm",
)
```

## 7.7 Renormalization

Always renormalize to 50 ohm (default for most RF systems) unless raw modal impedance is specifically needed. Set via `renormalization_impedance=50` at port creation.
