---
name: pyaedt-cli
description: Use when interacting with ANSYS AEDT through the current PyAEDT CLI. Triggers on requests to start or inspect AEDT sessions, manage projects, create designs, run scripts, export screenshots or configs or use the PyAEDT command line from the workspace virtual environment.
---

# PyAEDT CLI skill

You have access to the `pyaedt` CLI to interact with ANSYS Electronics Desktop (AEDT). This skill teaches you how to use it effectively.

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

Before running any command, resolve the `pyaedt` binary once:

1. Try `pyaedt` directly — if it is on the system PATH, use it as-is.
2. If not found, fall back to the venv-local binary in the current working directory:
   - Windows: `.venv\Scripts\pyaedt`
   - Linux/macOS: `.venv/bin/pyaedt`

All examples use `pyaedt` for brevity. Replace it with the resolved path if needed.

## Working Directory For Generated Artifacts

Use temporary directories for all exports and generated files unless the user specifies otherwise.

**Rules:**
- Create a task-specific subfolder under the OS temp directory
- Use `tempfile.mkdtemp(prefix="pyaedt-skill-")` (Python), `$env:TEMP` (Windows), or `${TMPDIR:-/tmp}` (Linux/macOS)
- Do not write to the repository or arbitrary folders unless explicitly requested
- Move artifacts from temp only after successful export if the user wants to keep them

**Quick reference:**
```python
import tempfile

temp_dir = tempfile.mkdtemp(prefix="pyaedt-skill-")
```

Pass this path to `--path` or `--output` in export commands.

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

Do not invent other command groups or commands that do not exist in the current CLI.
If a required operation is not supported by the CLI, report that to the user instead of trying to work around it.

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
pyaedt --json run my_script.py --port 50051
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

| Command | Description                                                         |
|---|---------------------------------------------------------------------|
| `pyaedt --json session start --version 2026.1 [--port 50051] [--non-graphical]` | Start a new AEDT instance                                           |
| `pyaedt --json session list` | List running AEDT instances with PID, version, and port             |
| `pyaedt --json session stop --port 50051` | Stop a specific AEDT instance by port                               |
| `pyaedt --json session stop --all` | Close all AEDT instances.                                           |
| `pyaedt session attach [--port 50051] [--project NAME] [--design NAME]` | Launch an interactive PyAEDT console attached to a running instance |

Notes:

- `session attach` can work interactively if `--port` is omitted and the user selects an instance.
- `--project` or `--design` with `session attach` only works for gRPC instances with a usable port.

### Project Commands

Port is required for all project commands to specify which AEDT instance to target.

| Command | Description |
|---|---|
| `pyaedt --json project list --port 50051` | List all open projects and their designs |
| `pyaedt --json project open "C:/path/to/file.aedt" --port 50051 [--non-graphical]` | Open an AEDT project file |
| `pyaedt --json project save --port 50051 [--path "C:/new/file.aedt"]` | Save the active project, optionally as a new file |
| `pyaedt --json project create --name ProjectA --port 50051` | Create a **project** — use `--name` |
| `pyaedt --json project create --project ProjectA --design Design1 --type Hfss --port 50051` | Create a **design** inside an existing project — use `--project` + `--design` + `--type` |
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
| `pyaedt --json run "path/to/script.py" --port 50051` | Execute a Python script inside AEDT |


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
# Create a project — use --name ONLY (do NOT add --design or --type)
pyaedt --json project create --name "PatchAntenna" --port 50051

# Create a design in an existing project — use --project + --design + --type ONLY (do NOT add --name)
pyaedt --json project create --project "PatchAntenna" --design "HFSSDesign1" --type Hfss --port 50051
```

### Workflow 4: Interactive Exploration With session attach

Use `session attach` as the **first choice** when the user wants to explore, debug, or iterate on a design interactively.
It opens an iPython console that is already connected to the target AEDT session — `desktop` is pre-injected, so PyAEDT commands can be issued one by one without writing a full script.

```bash
# Attach to a running instance (port optional — prompts if omitted)
pyaedt session attach --port 50051

# Inside the iPython console — the session is already live:
# >>> import ansys.aedt.core as aedt
# >>> hfss = aedt.Hfss(new_desktop=False, port=50051)
# >>> box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10], name="MyBox")
# >>> hfss.modeler["MyBox"].color = (255, 0, 0)
```

#### Sending Multi-Line Code to the iPython Console

When the agent sends code to the iPython console that spans **more than one line** (loops, conditionals, function definitions, etc.), pasting it directly causes an `IndentationError` or `SyntaxError` because the console treats each line as a separate input.

**Always wrap multi-line blocks in `exec()`**, encoding all newlines as `\n` inside a single string:

```python
# Fails — the console breaks on the loop body
for i in range(3):
    print(i)

# Correct — send as a single exec() call
exec("for i in range(3):\n    print(i)")
```

Rules:

- Use `exec()` for **any** block that contains indented code (loops, `if`, `with`, function or class definitions).
- Single-statement lines (imports, assignments, function calls) do **not** need `exec()`.
- Escape all inner double-quotes as `\"` if the outer delimiter is `"`, or use concatenated string literals as shown above.
- Keep `exec()` calls as short as possible; if the block grows beyond ~10 lines prefer saving a temp script and using `run` instead.

**When to prefer `session attach` over `run`:**

| Situation | Preferred approach |
|---|---|
| Exploring design state, unknown goal | `session attach` |
| Debugging a failing step interactively | `session attach` |
| One-off geometry / parameter tweaks | `session attach` |
| Iterating quickly on a few commands | `session attach` |
| Defined, repeatable, multi-step workflow | `run` |
| CI / headless / automated pipeline | `run` |
| Workflow has more than ~5 steps | `run` |
| Traceability and logging required | `run` |

Prefer `session attach` first. Graduate to `run` only once the workflow is known and needs to be repeatable or automated.

#### Working With Multiple Designs Simultaneously

When the user needs to work on **more than one design at the same time**, open a **separate iPython console for each design** instead of switching designs inside a single console.
This keeps every design live and editable without closing or releasing any of them.

```bash
# Terminal 1 — console for Design A
pyaedt session attach --port 50051 --project "ProjectA" --design "DesignA"

# Terminal 2 — console for Design B (same or different project)
pyaedt session attach --port 50051 --project "ProjectA" --design "DesignB"

# Terminal 3 — console for a design in a different project
pyaedt session attach --port 50051 --project "ProjectB" --design "DesignC"
```

Rules:

- Each console holds its own PyAEDT object bound to a specific design — closing one console does **not** close the others.
- All consoles share the same AEDT instance (same `--port`), so changes made in one are visible in AEDT immediately.
- Do **not** call `desktop.release_desktop()` or `aedt_app.release_desktop()` inside any of these consoles unless you intentionally want to shut down AEDT for all open consoles.
- If the designs live in different AEDT instances, use the matching `--port` for each console.


### Workflow 5: Run Automation

```bash
pyaedt --json run "<temp-dir>/setup_antenna.py" --port 50051
```

### Workflow 6: Generated Script Execution

Use this workflow whenever a script has been generated and must be run automatically.

```bash
# Step 1: discover instances
pyaedt --json session list

# Step 2: if needed, start one
pyaedt --json session start --version 2026.1 --non-graphical

# Step 3: run the script on the chosen port
pyaedt --json run "<temp-dir>/generated_script.py" --port 50051
```

Rules:

- Always determine the target port first.
- If multiple instances are running, present the full list and ask which port to use.
- Do not tell the user to run the generated script manually if the workflow requires automatic execution.
- Generated scripts intended for an existing AEDT instance should use `new_desktop=False`.

### Workflow 7: Export Design Data

```bash
# If the instance has exactly one project and one design, selectors can be omitted
pyaedt --json export screenshot --port 50051 --path "<temp-dir>/preview.jpg"
pyaedt --json export config --port 50051 --output "<temp-dir>/config.json" --overwrite

# If ambiguous, specify the missing selector(s)
pyaedt --json export screenshot --port 50051 --project "PatchAntenna" --design "HFSSDesign1" --path "<temp-dir>/preview.jpg"
```

## Error Handling

Always parse the `status` field in JSON output before using `data`:

```json
{"status": "ok", "data": {...}}
{"status": "error", "error": "message"}
```

If `status` is `"error"`, report the `error` message to the user and stop. Do not attempt to use `data`.

## Guidance Rules For This Skill

- Resolve the `pyaedt` binary once at the start (PATH first, then venv fallback) and use `pyaedt` for all subsequent commands.
- Prefer `--json` for non-interactive operations.
- Do not reference removed commands or groups.
- For `project create`: use `--name` + `--port` to create a project; use `--project` + `--design` + `--type` + `--port` to create a design. Never combine `--name` with `--project`, `--design`, or `--type`.
- When a command is design-scoped, apply the shared project/design resolution rules explicitly.
- When the available project/design selection is ambiguous, ask for the missing selector instead of guessing.
- Use `project list --port ...` to inspect the AEDT state before choosing selectors.
- Use `run` for real scripts.
- Use `session attach` as the first choice for interactive, exploratory, or debugging workflows; fall back to `run` only when the workflow is defined, repeatable, or automated.
- When sending multi-line code (loops, conditionals, function definitions) to a `session attach` iPython console, always wrap the entire block in a single `exec("line1\nline2\n...")` call. Never paste raw indented blocks directly — they cause `IndentationError` or `SyntaxError`.
- When the user needs to work on **multiple designs simultaneously**, instruct them to open one `session attach` console per design (one terminal per design). Never switch designs inside a single console to handle multiple designs at once.
- When multiple instances are found, present the full list with port, version, and PID before asking.
- When a generated script must be executed automatically, determine the target port first and then run `run --port ...`.
- Generated scripts intended to reuse an existing AEDT instance should use `new_desktop=False`.
- Unless the user explicitly asks for another destination, create and use a task-specific temporary folder for exports, generated scripts, screenshots, configs, and other intermediate files.

## Performance Tips

- Use `session list` before starting AEDT so you do not launch unnecessary instances.
- Use `project list --port ...` to inspect available projects and designs before attempting a design-scoped export.
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
