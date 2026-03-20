---
name: pyaedt-cli-agent
description: Use when interacting with ANSYS AEDT through the PyAEDT CLI. Triggers on requests to launch, connect, create designs, run simulations, export results, or manage AEDT projects via command line.
---

# PyAEDT CLI Agent Skill

You have access to the `pyaedt` CLI to interact with ANSYS Electronics Desktop (AEDT). This skill teaches you how to use it effectively.

## Golden Rule: Always Use --json

**Every command MUST use `--json` for structured, parseable output:**

```bash
pyaedt --json <group> <command> [options]
```

JSON output returns: `{"status": "ok", "data": {...}}` or `{"status": "error", "error": "message"}`

Always parse the `status` field before using `data`. Never rely on human-readable output.

## Session Model

The CLI uses a persistent session file (`~/.pyaedt/session.json`). You connect once, run many commands, then disconnect.

```
session connect -> [commands...] -> session disconnect
```

Session info (port, machine, version) is saved automatically on `session connect` or `process start`. All subsequent commands reuse this session.

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
| `pyaedt --json session disconnect [--close-projects]` | Disconnect and clear session | No |
| `pyaedt --json session status` | Show AEDT status, projects, version | Yes |

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
| `pyaedt --json project list` | List all open projects |
| `pyaedt --json project list-designs [--project NAME]` | List designs in a project |
| `pyaedt --json project open "C:/path/to/file.aedt" [--design NAME]` | Open a project file |
| `pyaedt --json project save [--project NAME] [--save-as PATH]` | Save project |
| `pyaedt --json project create-design <AppType> [--name NAME] [--solution-type TYPE]` | Create a new design |
| `pyaedt --json project analyze [--setup NAME] [--design NAME] [--cores N]` | Run simulation |

**AppType values:** `Hfss`, `Maxwell2d`, `Maxwell3d`, `Q3d`, `Q2d`, `Icepak`, `Circuit`, `TwinBuilder`, `Mechanical`, `Emit`, `Rmxprt`, `Hfss3dLayout`, `MaxwellCircuit`

### Script Execution (`pyaedt script`)

| Command | Description |
|---|---|
| `pyaedt --json script run "path/to/script.py"` | Execute a Python script inside AEDT |
| `pyaedt --json script code "python_code_here"` | Execute inline Python code |

`script code` provides `desktop` (PyAEDT Desktop), `odesktop` (native COM), and `result` variable. Set `result` to return a value:

```bash
pyaedt --json script code "hfss = desktop.active_app(); result = hfss.design_name"
```

### File Management (`pyaedt file`)

| Command | Description |
|---|---|
| `pyaedt --json file list [--dir PATH] [--pattern "*.aedt"]` | List files in directory |
| `pyaedt --json file upload "local_file.step" [--to "C:/aedt_work/"]` | Copy file to AEDT working dir |
| `pyaedt --json file download "C:/aedt_work/results.csv" [--to "./local/"]` | Copy file from AEDT working dir |

### Export (`pyaedt export`)

| Command | Description |
|---|---|
| `pyaedt --json export screenshot [--output "preview.jpg"] [--design NAME]` | Capture design view screenshot |
| `pyaedt --json export touchstone "out.s2p" [--setup NAME] [--sweep NAME]` | Export S-parameters |
| `pyaedt --json export 3d "model.step" [--format step/iges/sat/stl]` | Export 3D geometry |

### Utility (`pyaedt utility`)

| Command | Description |
|---|---|
| `pyaedt --json utility clear [--close-projects/--no-close-projects]` | Close all projects, clear messages |
| `pyaedt --json utility model-info [--design NAME]` | Get design name, type, project path |

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
# Check what's available
pyaedt --json session check-installed
pyaedt --json process list

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

## Error Handling

Always check the `status` field:

```python
import json, subprocess

result = subprocess.run(
    ["pyaedt", "--json", "session", "status"], capture_output=True, text=True
)
response = json.loads(result.stdout)

if response["status"] == "error":
    # Handle error - response["error"] has the message
    if "No active session" in response["error"]:
        # Need to connect first
        subprocess.run(["pyaedt", "--json", "session", "connect", "--port", "50051"])
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
