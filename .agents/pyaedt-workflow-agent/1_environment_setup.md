---
name: 1_environment_setup
description: >
  Step 1 of the PyAEDT workflow: imports, settings, and project/design names.
  Always the first step in any PyAEDT script.
---

# Step 1 — Environment Setup

```python
import ansys.aedt.core as aedt
from ansys.aedt.core import settings

# Project config
non_graphical = False  # True for CI/headless runs
version = "2026.1"  # must match installed version
project = "MyProject"
design = "MyDesign"

# Logging — enable all sinks
settings.enable_logger = True
settings.enable_screen_logs = True
settings.enable_file_logs = True
settings.enable_desktop_logs = True
settings.enable_global_log_file = True

# Safe disconnection on failure
settings.release_on_exception = (
    True  # always keep True; prevents orphaned AEDT processes
)
```

> **All `settings` must be set before any PyAEDT object is instantiated — they are read at session startup and have no effect afterwards.**

