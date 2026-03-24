# PyAEDT Copilot Instructions

## Agent Selection Guide

Two agents are available. Always **read the skill file** (using the file-reading tool) **before** responding — do NOT use `run_subagent`, these are Markdown instruction files, not registered sub-agents.

| Agent | Skill file                                | Purpose |
|---|-------------------------------------------|---|
| `pyaedt-cli-agent` | `.agents\pyaedt-cli-agent\README.md`      | Interact with AEDT via the `pyaedt` CLI |
| `pyaedt-script-agent` | `.agents\pyaedt-workflow-agent\README.md` | Write or edit PyAEDT Python scripts |

---

## Agent 1 — pyaedt-cli-agent (MANDATORY)

**Read this skill file when the user wants to interact with AEDT:**

- Launch, connect to, or stop AEDT
- Open / save / list projects or designs
- Execute a script or inline code inside AEDT

```
Read skill file: .agents\pyaedt-cli-agent\README.md
```

---

## Agent 2 — pyaedt-workflow-agent (MANDATORY)

**Read this skill file when the user wants to write or modify a PyAEDT Python script:**

- Create a full automation script from scratch
- Add or modify a specific step in an existing script
- Ask how to use the PyAEDT API

```
Read skill file: .agents\pyaedt-workflow-agent\README.md
```
