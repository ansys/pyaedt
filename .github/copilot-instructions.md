# PyAEDT Copilot Instructions

## Agent Selection Guide

Two agents are available. Always load the correct one **before** responding.

| Agent | Skill file                                | Purpose |
|---|-------------------------------------------|---|
| `pyaedt-cli-agent` | `.agents\pyaedt-cli-agent\README.md`      | Interact with AEDT via the `pyaedt` CLI |
| `pyaedt-script-agent` | `.agents\pyaedt-workflow-agent\README.md` | Write or edit PyAEDT Python scripts |

---

## Agent 1 — pyaedt-cli-agent (MANDATORY)

**Load when the user wants to interact with AEDT:**

- Launch, connect to, or stop AEDT
- Open / save / list projects or designs
- Execute a script or inline code inside AEDT

```
Skill file: .agents\pyaedt-cli-agent\README.md
```

---

## Agent 2 — pyaedt-workflow-agent (MANDATORY)

**Load when the user wants to write or modify a PyAEDT Python script:**

- Create a full automation script from scratch
- Add or modify a specific step in an existing script
- Ask how to use the PyAEDT API

```
Skill file: .agents\pyaedt-script-agent\README.md
```
