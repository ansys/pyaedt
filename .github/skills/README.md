# Overview of the PyAEDT skills marketplace

Skills are organized as plugins under `.github/plugin/`. Each plugin has its own directory with a README and a `skills/` subdirectory containing SKILL.md files.

The marketplace manifest lives at `.github/plugin/marketplace.json`.

**GitHub Copilot CLI**

Add the marketplace:

```bash
copilot plugin marketplace add ansys/pyaedt
```

Install the available plugins:

```bash
copilot plugin install pyaedt-cli@pyaedt-skills
copilot plugin install pyaedt-dev@pyaedt-skills
```

| Plugin | Purpose |
|---|---|
| `pyaedt-cli` | Drive Ansys Electronics Desktop through the `pyaedt` command-line interface. |
| `pyaedt-dev` | Develop and maintain the PyAEDT Python code base. |

**Claude Code**

Claude uses `.claude-plugin/marketplace.json`, whose content points to `../.github/plugin/marketplace.json`.

## Maintenance

When you add or update a skill, place it under `.github/plugin/<plugin-name>/skills/`. A plugin with a
single skill may keep it at `skills/SKILL.md`; a plugin with several skills uses one subdirectory per
skill, `skills/<skill-name>/SKILL.md`, and lists each path in the manifest. Update
`.github/plugin/marketplace.json` accordingly. The referenced `.claude-plugin/marketplace.json` picks
up changes automatically.