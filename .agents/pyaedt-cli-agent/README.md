---
name: pyaedt-cli-agent
description: Use when interacting with ANSYS AEDT through the PyAEDT CLI. Triggers on requests to launch, connect, create designs, run simulations, export results, or manage AEDT projects via command line.
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
pyaedt --json <group> <command> [options]
```

## Golden Rule: Always Use --json

**Every command MUST use `--json` for structured, parseable output:**

JSON output returns: `{"status": "ok", "data": {...}}` or `{"status": "error", "error": "message"}`

Always parse the `status` field before using `data`. Never rely on human-readable output.

## Session Model

The CLI uses a persistent session file (`~/.pyaedt/session.json`). You connect once, run many commands, then disconnect.

```
[write script] -> session connect -> script run -> session disconnect
```

> **Important:** Always write or generate the script **before** calling `session connect`. Connect only once per workflow — never call `session connect` a second time.

Session info (port, machine, version) is saved automatically on `session connect` or `process start`. All subsequent commands reuse this session.

### Targeting a Specific Instance with `--port`

When multiple AEDT instances are running simultaneously, every session-scoped command accepts `--port PORT` to target a specific instance **without changing the saved session**. This lets you operate on several desktops in the same script:

```bash
# Two instances running on ports 50051 and 50052
pyaedt --json session status --port 50051
pyaedt --json project list --port 50052
```

If `--port` is omitted, the port from `~/.pyaedt/session.json` is used.

## Command Structure

Commands are organized into groups:

```
pyaedt [--json] <group> <command> [options]
```

Available groups: `session`, `process`, `project`, `script`, `file`, `export`, `utility`, `config`, `panels`, `doc`

Top-level commands (no group): `version`, `aedt-versions`

## Command Reference

### Top-Level Commands

| Command | Description | Requires Session |
|---|---|---|
| `pyaedt --json version` | Display PyAEDT version | No |
| `pyaedt --json aedt-versions` | List installed AEDT versions on this machine | No |

### Session Management (`pyaedt session`)

| Command | Description | Requires Session |
|---|---|---|
| `pyaedt --json session connect --port 50051 [--machine localhost] [--version 2026.1]` | Connect to running AEDT | No (creates session) |
| `pyaedt --json session disconnect [--port PORT] [--close-projects]` | Disconnect and clear session | No |
| `pyaedt --json session status [--port PORT]` | Show AEDT status, projects, version | Yes |

### Process Management (`pyaedt process`)

| Command | Description | Requires Session |
|---|---|---|
| `pyaedt --json process list` | List running AEDT processes | No |
| `pyaedt --json process start --version 2026.1 [--non-graphical] [--port 50051]` | Launch new AEDT instance | No (creates session) |
| `pyaedt --json process stop --all` | Stop all AEDT processes | No |
| `pyaedt --json process stop --pid 12345` | Stop process by PID | No |
| `pyaedt --json process stop --port 50051` | Stop process by port | No |
| `pyaedt process attach [--pid PID]` | Attach interactive console to AEDT | No |

### Project & Design Management (`pyaedt project`)

| Command | Description |
|---|---|
| `pyaedt --json project list [--port PORT]` | List all open projects |
| `pyaedt --json project list-designs [--project NAME] [--port PORT]` | List designs in a project |
| `pyaedt --json project open "C:/path/to/file.aedt" [--design NAME] [--port PORT]` | Open a project file |
| `pyaedt --json project save [--project NAME] [--save-as PATH] [--port PORT]` | Save project |
| `pyaedt --json project create-design <AppType> [--name NAME] [--solution-type TYPE] [--port PORT]` | Create a new design |
| `pyaedt --json project analyze [--setup NAME] [--design NAME] [--cores N] [--port PORT]` | Run simulation |

**AppType values:** `Hfss`, `Maxwell2d`, `Maxwell3d`, `Q3d`, `Q2d`, `Icepak`, `Circuit`, `TwinBuilder`, `Mechanical`, `Emit`, `Rmxprt`, `Hfss3dLayout`, `MaxwellCircuit`

### Script Execution (`pyaedt script`)

| Command | Description |
|---|---|
| `pyaedt --json script run "path/to/script.py" [--port PORT]` | Execute a Python script inside AEDT |
| `pyaedt --json script code "python_code_here" [--port PORT]` | Execute inline Python code |

`script code` provides `desktop` (PyAEDT Desktop), `odesktop` (native COM), and `result` variable. Set `result` to return a value:

```bash
pyaedt --json script code "hfss = desktop.active_app(); result = hfss.design_name"
```

**When to use `script code` vs `script run`:**

| Use `script code` (inline) | Use `script run` (file) |
|---|---|
| Simple, single-step operations (create a box, get a value, assign a material) | Multi-step workflows with many operations |
| Quick queries or one-off tasks | Scripts meant to be saved, reused, or shared |
| No need to persist the code | Complex logic, loops, or error handling |

> **Rule:** Do **not** create a script file for simple tasks. Prefer `script code` unless the task genuinely requires a multi-step script.

### File Management (`pyaedt file`)

| Command | Description |
|---|---|
| `pyaedt --json file list [--dir PATH] [--pattern "*.aedt"]` | List files in directory |
| `pyaedt --json file upload "local_file.step" [--to "C:/aedt_work/"]` | Copy file to AEDT working dir |
| `pyaedt --json file download "C:/aedt_work/results.csv" [--to "./local/"]` | Copy file from AEDT working dir |

### Export (`pyaedt export`)

| Command | Description |
|---|---|
| `pyaedt --json export screenshot [--output "preview.jpg"] [--design NAME] [--port PORT]` | Capture design view screenshot |
| `pyaedt --json export touchstone "out.s2p" [--setup NAME] [--sweep NAME] [--port PORT]` | Export S-parameters |
| `pyaedt --json export 3d "model.step" [--format step/iges/sat/stl] [--port PORT]` | Export 3D geometry |

### Utility (`pyaedt utility`)

| Command | Description |
|---|---|
| `pyaedt --json utility clear [--close-projects/--no-close-projects] [--port PORT]` | Close all projects, clear messages |
| `pyaedt --json utility model-info [--design NAME] [--port PORT]` | Get design name, type, project path |

### Configuration (`pyaedt config`)

| Command | Description |
|---|---|
| `pyaedt config test --show` | Show current test configuration |
| `pyaedt config test desktop-version 2026.1` | Set AEDT version for tests |
| `pyaedt config test non-graphical true` | Set non-graphical mode |

### Documentation (`pyaedt doc`)

| Command | Description |
|---|---|
| `pyaedt doc` | Open PyAEDT documentation home |
| `pyaedt doc examples` | Open examples page |
| `pyaedt doc search <keywords>` | Search documentation |

### Panels (`pyaedt panels`)

| Command | Description |
|---|---|
| `pyaedt panels add --personal-lib PATH` | Install PyAEDT panels in AEDT |

## Common Workflows

### Workflow 1: Connect and Explore

```bash
# Use the venv-local binary if pyaedt is not on PATH
.venv\Scripts\pyaedt --json process list      # Windows
# .venv/bin/pyaedt --json process list        # Linux/macOS

# Connect to existing instance
pyaedt --json session connect --port 50051

# See what's open
pyaedt --json session status
pyaedt --json project list
pyaedt --json project list-designs
pyaedt --json utility model-info
```

### Workflow 2: Create and Simulate

```bash
# Connect
pyaedt --json session connect --port 50051

# Create design
pyaedt --json project create-design Hfss --name "PatchAntenna" --solution-type "DrivenModal"

# Run a setup script
pyaedt --json script run "./setup_antenna.py"

# Analyze
pyaedt --json project analyze --setup "Setup1" --cores 8

# Export results
pyaedt --json export touchstone "./antenna.s2p" --setup "Setup1"
pyaedt --json export screenshot --output "antenna_model.jpg"

# Save and disconnect
pyaedt --json project save
pyaedt --json session disconnect
```

### Workflow 3: Launch Fresh AEDT

```bash
# Launch non-graphical AEDT
pyaedt --json process start --version 2026.1 --non-graphical

# Open existing project
pyaedt --json project open "C:/projects/filter.aedt" --design "HFSSDesign1"

# Work with it...
pyaedt --json project analyze
pyaedt --json export touchstone "./filter.s2p"

# Close everything
pyaedt --json session disconnect --close-projects
```

### Workflow 4: Work with Multiple AEDT Instances

```bash
# Two instances already running on different ports
pyaedt --json session status --port 50051   # check instance A
pyaedt --json session status --port 50052   # check instance B

# Operate on each independently without changing the saved session
pyaedt --json project list --port 50051
pyaedt --json project analyze --port 50051 --design "FilterA" --setup "Setup1"
pyaedt --json project analyze --port 50052 --design "FilterB" --setup "Setup1"

# Export from each
pyaedt --json export touchstone "filter_a.s2p" --port 50051
pyaedt --json export touchstone "filter_b.s2p" --port 50052
```

### Workflow 5: Auto-detect Running AEDT, Connect, and Launch a Script

Use this workflow whenever a script is generated and must be executed immediately against a running (or freshly started) AEDT instance.

```bash
# Step 1 — discover running AEDT processes
pyaedt --json process list
```

**Decision logic (agent must apply this):**

| `process list` result | Action |
|---|---|
| Empty list | Launch a new instance: `pyaedt --json process start --version 2026.1` |
| Exactly one process | Connect directly to its port |
| Two or more processes | **Ask the user** which port to use, then connect to the chosen one |

```bash
# Step 2a — one instance found on port 50051, connect to it
pyaedt --json session connect --port 50051

# Step 2b — multiple instances: show the full list to the user and ask
# "Multiple AEDT instances are running:
#   • port 50051 — version 2026.1 (PID 1234)
#   • port 50052 — version 2025.2 (PID 5678)
# Which port should the script use?"
# Then connect to the chosen port:
pyaedt --json session connect --port <chosen_port>

# Step 3 — immediately run the generated script in the SAME command chain (no pause, no user confirmation)
pyaedt --json script run "path/to/generated_script.py"
```

> **Mandatory execution pattern** — always chain connect + run in a single terminal call:
> ```bash
> pyaedt --json session connect --port 50051 && pyaedt --json script run "path/to/script.py"
> ```
> Never stop after `session connect` and wait. The script **must** be executed immediately after connecting.

**Rules:**
- Always run `process list` first — never assume an instance is or is not running.
- When multiple instances are found, present the full list (port, version, PID) before asking.
- **Write (or generate) the script BEFORE connecting.** Do not call `session connect` until the script is ready to run.
- **Connect only once.** Never call `session connect` more than once per workflow.
- **Always chain `session connect` and `script run` in the same command** (`&&`). Never connect without immediately running the script.
- After connecting, always use `script run` to launch the generated script automatically — do **not** ask the user to run it manually.
- The script must use `new_desktop=False` so it attaches to the already-connected session (see Step 2 of the workflow agent).

## Error Handling

Always check the `status` field:

```python
import json, subprocess, sys
from pathlib import Path

# Resolve pyaedt binary: prefer venv, fall back to PATH
venv = Path.cwd() / ".venv"
pyaedt_bin = str(venv / ("Scripts/pyaedt" if sys.platform == "win32" else "bin/pyaedt"))
if not Path(pyaedt_bin).exists():
    pyaedt_bin = "pyaedt"

result = subprocess.run(
    [pyaedt_bin, "--json", "session", "status"], capture_output=True, text=True
)
response = json.loads(result.stdout)

if response["status"] == "error":
    # Handle error - response["error"] has the message
    if "No active session" in response["error"]:
        # Need to connect first
        subprocess.run([pyaedt_bin, "--json", "session", "connect", "--port", "50051"])
```

## Performance Tips

- **Connect once**, run many commands. Don't reconnect per command.
- Use `--json` to avoid parsing decorative output.
- Use `script code` for quick queries instead of creating full scripts.
- Use `utility model-info` to quickly check the active design state.
- Prefer `project list` + `project list-designs` over `session status` for targeted queries.
- Use `--non-graphical` when launching AEDT for headless/agent workflows.

## Cleanup

Always disconnect when done:

```bash
pyaedt --json session disconnect --close-projects
```

If AEDT processes are stuck:

```bash
pyaedt --json process stop --all
```
