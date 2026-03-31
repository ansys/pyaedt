---
name: pyaedt-cli-agent
description: Use when interacting with ANSYS AEDT through the current PyAEDT CLI. Triggers on requests to start or inspect AEDT sessions, manage projects, create designs, run scripts, export screenshots or configs or use the PyAEDT command line from the workspace virtual environment.
---

# PyAEDT CLI agent

You have access to the `pyaedt` CLI to interact with ANSYS Electronics Desktop (AEDT). This agent teaches you how to use it effectively.

## Pre-Flight Check (Run First)

Before any CLI command, verify `pyaedt` is installed:

```bash
pyaedt --json version
```

If the command fails, stop and tell the user to install it first:

```bash
pip install pyaedt[all]
```

---

## Invoking the CLI

The `pyaedt` executable may not be on the system PATH. It is always available inside the virtual environment of the current working directory. Prefer the venv-local binary:

```bash
.venv\Scripts\pyaedt --json <group> <command> [options]   # Windows
# .venv/bin/pyaedt --json <group> <command> [options]       # Linux/macOS
```

If the wrapper is already on PATH, `pyaedt --json ...` is also fine.

## Golden Rule: Prefer --json

Use `--json` for every non-interactive command so output stays structured and machine-parseable.

JSON output returns: `{"status": "ok", "data": {...}}` or `{"status": "error", "error": "message"}`

Always parse the `status` field before using `data`. Never rely on human-readable output.

Exceptions:

- `session attach` launches an interactive console, so human mode is acceptable.
- `doc` commands open browser pages and are not usually consumed as structured automation output.

## Current CLI Shape

Commands are organized as:

```bash
pyaedt [--json] <group> <command> [options]
```

Available groups in the current CLI:

- `session`
- `project`
- `script`
- `export`
- `test-config`
- `panels`
- `doc`

Top-level commands:

- `version`
- `aedt-versions`

Do not invent or call removed groups or commands such as:

- `session connect`
- `session disconnect`
- `session status`
- `process ...`
- `file ...`
- `utility ...`
- `config test ...`
- `project list-designs`
- `project create-design`
- `project analyze`
- `export touchstone`
- `export 3d`

## Port-Based Model

The current CLI is port-based, not session-file based.

- `session start` launches a new AEDT instance and returns its gRPC port.
- `session list` discovers running AEDT instances.
- Most operational commands require `--port` explicitly.
- There is no persisted `session connect` state to reuse later.

Practical implication:

```bash
# Discover or start AEDT
pyaedt --json session list
pyaedt --json session start --version 2026.1 --non-graphical

# Then pass --port to the command you want
pyaedt --json project list --port 50051
pyaedt --json script run my_script.py --port 50051
```

## Project And Design Resolution Rules

Design-scoped commands use one shared resolution rule set. This is important and should be applied consistently in guidance and examples.

Commands affected:

- `export screenshot`
- `export config`
- `session attach` when used with `--project` or `--design`

Resolution rules:

- If both `--project` and `--design` are provided, use them directly.
- If only `--project` is provided, that project must contain exactly one design.
- If only `--design` is provided, exactly one project must be open.
- If neither is provided, there must be exactly one open project and exactly one design in it.
- If the selection is ambiguous, the command fails and the missing selector must be provided.

When helping a user, do not describe this behavior as “active project” or “active design” fallback unless the command actually uses that behavior. The intended behavior is uniqueness-based resolution.

## Command Reference

### Top-Level Commands

| Command | Description |
|---|---|
| `pyaedt --json version` | Display the PyAEDT version |
| `pyaedt --json aedt-versions` | List installed AEDT versions on the machine |

### Session Management

| Command | Description |
|---|---|
| `pyaedt --json session start --version 2026.1 [--port 50051] [--non-graphical]` | Start a new AEDT instance |
| `pyaedt --json session list` | List running AEDT instances with PID, version, and port |
| `pyaedt --json session stop --port 50051` | Stop a specific AEDT instance by port |
| `pyaedt --json session stop --all` | Stop all AEDT instances. |
| `pyaedt session attach [--port 50051] [--project NAME] [--design NAME]` | Launch an interactive PyAEDT console attached to a running instance |

Notes:

- `session attach` can work interactively if `--port` is omitted and the user selects an instance.
- `--project` or `--design` with `session attach` only works for gRPC instances with a usable port.

### Project Commands

| Command | Description |
|---|---|
| `pyaedt --json project list --port 50051` | List all open projects and their designs |
| `pyaedt --json project open "C:/path/to/file.aedt" --port 50051 [--non-graphical]` | Open an AEDT project file |
| `pyaedt --json project save --port 50051 [--path "C:/new/file.aedt"]` | Save the active project, optionally as a new file |
| `pyaedt --json project create --name ProjectA --port 50051` | Create a project |
| `pyaedt --json project create --project ProjectA --design Design1 --type Hfss --port 50051` | Create a design inside an existing project |
| `pyaedt --json project close --port 50051 [--project ProjectA]` | Close a project, or the active project if omitted |

`project create` behavior:

- `--name` is for project creation.
- `--project` + `--design` + `--type` is for design creation.
- Do not mix `--name` with `--design` / `--type`.

Supported `--type` values:

- `Hfss`
- `Maxwell2d`
- `Maxwell3d`
- `Q3d`
- `Q2d`
- `Icepak`
- `Circuit`
- `TwinBuilder`
- `Mechanical`
- `Emit`
- `Rmxprt`
- `Hfss3dLayout`
- `MaxwellCircuit`

### Script Commands

| Command | Description |
|---|---|
| `pyaedt --json script run "path/to/script.py" --port 50051` | Execute a Python script inside AEDT |
| `pyaedt --json script code "result = 42" --port 50051` | Execute inline Python code inside AEDT |

`script code` runs with:

- `desktop`: the PyAEDT Desktop object
- `odesktop`: the native AEDT desktop object
- `result`: set this to return a value

Example:

```bash
pyaedt --json script code "result = odesktop.GetProjectList()" --port 50051
```

Use `script code` for short, one-off operations. Use `script run` for reusable or multi-step workflows.

### Export Commands

| Command | Description |
|---|---|
| `pyaedt --json export screenshot --port 50051 [--path preview.jpg] [--project NAME] [--design NAME]` | Capture a screenshot for a resolved design |
| `pyaedt --json export config --port 50051 [--output config.json] [--project NAME] [--design NAME] [--overwrite]` | Export a design configuration JSON |

Both commands are design-scoped and therefore follow the shared project/design resolution rules above.

### Documentation

| Command | Description |
|---|---|
| `pyaedt doc` | Open the docs home page and print help |
| `pyaedt doc examples` | Open the examples section |
| `pyaedt doc github` | Open the GitHub repository |
| `pyaedt doc user-guide` | Open the user guide |
| `pyaedt doc getting-started` | Open getting started docs |
| `pyaedt doc installation` | Open installation docs |
| `pyaedt doc api` | Open API reference |
| `pyaedt doc changelog [VERSION]` | Open the changelog |
| `pyaedt doc issues` | Open the issues page |
| `pyaedt doc search <keywords>` | Search the online documentation |

## Common Workflows

### Workflow 1: Discover Or Start AEDT

```bash
# Check for running instances
pyaedt --json session list

# If none are running, start one
pyaedt --json session start --version 2026.1 --non-graphical
```

Decision rule:

- If `session list` returns no processes, start AEDT.
- If it returns one process, reuse that port.
- If it returns multiple processes, ask the user which port to use.

### Workflow 2: Inspect Projects On A Port

```bash
pyaedt --json project list --port 50051
```

Use this first when you need to understand which project and design selectors will be required.

### Workflow 3: Create A Project Or A Design

```bash
# Create a project
pyaedt --json project create --name "PatchAntenna" --port 50051

# Create a design in an existing project
pyaedt --json project create --project "PatchAntenna" --design "HFSSDesign1" --type Hfss --port 50051
```

### Workflow 4: Run Automation

```bash
pyaedt --json script run "./setup_antenna.py" --port 50051

# Or a small one-off command
pyaedt --json script code "result = odesktop.GetProjectList()" --port 50051
```

### Workflow 5: Export Design Data

```bash
# If the instance has exactly one project and one design, selectors can be omitted
pyaedt --json export screenshot --port 50051 --path "preview.jpg"
pyaedt --json export config --port 50051 --output "config.json" --overwrite

# If ambiguous, specify the missing selector(s)
pyaedt --json export screenshot --port 50051 --project "PatchAntenna" --design "HFSSDesign1" --path "preview.jpg"
```

### Workflow 6: Generated Script Execution

Use this workflow whenever a script has been generated and must be run automatically.

```bash
# Step 1: discover instances
pyaedt --json session list

# Step 2: if needed, start one
pyaedt --json session start --version 2026.1 --non-graphical

# Step 3: run the script on the chosen port
pyaedt --json script run "path/to/generated_script.py" --port 50051
```

Rules:

- Always determine the target port first.
- If multiple instances are running, present the full list and ask which port to use.
- Do not tell the user to run the generated script manually if the workflow requires automatic execution.
- Generated scripts intended for an existing AEDT instance should use `new_desktop=False`.

## Error Handling

Always parse the `status` field in JSON output.

```python
import json
import subprocess
import sys
from pathlib import Path

venv = Path.cwd() / ".venv"
pyaedt_bin = str(venv / ("Scripts/pyaedt" if sys.platform == "win32" else "bin/pyaedt"))
if not Path(pyaedt_bin).exists():
    pyaedt_bin = "pyaedt"

result = subprocess.run(
    [pyaedt_bin, "--json", "session", "list"], capture_output=True, text=True
)
response = json.loads(result.stdout)

if response["status"] == "error":
    raise RuntimeError(response["error"])

processes = response["data"]["processes"]
```

## Guidance Rules For This Agent

- Prefer the venv-local `pyaedt` executable when giving commands.
- Prefer `--json` for non-interactive operations.
- Do not reference removed commands or groups.
- When a command is design-scoped, apply the shared project/design resolution rules explicitly.
- When the available project/design selection is ambiguous, ask for the missing selector instead of guessing.
- Use `project list --port ...` to inspect the AEDT state before choosing selectors.
- Use `script code` for small one-off actions and `script run` for real scripts.
- Use `session attach` only when the user explicitly wants an interactive console.
- When multiple instances are found, present the full list with port, version, and PID before asking.
- When a generated script must be executed automatically, determine the target port first and then run `script run --port ...`.
- Generated scripts intended to reuse an existing AEDT instance should use `new_desktop=False`.

## Performance Tips

- Use `session list` before starting AEDT so you do not launch unnecessary instances.
- Use `project list --port ...` to inspect available projects and designs before attempting a design-scoped export.
- Use `script code` for quick queries instead of creating full scripts.
- Use `--non-graphical` when launching AEDT for headless or agent workflows.

## Cleanup

When the workflow requires shutting down AEDT, use:

```bash
pyaedt --json session stop --port 50051
```

If all AEDT instances must be terminated:

```bash
pyaedt --json session stop --all
```
