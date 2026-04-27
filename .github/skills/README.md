# PyAEDT skills marketplace

Skills are organized as plugins under `.github/plugin/`. Each plugin has its own directory with a README and a `skills/` subfolder containing SKILL.md files.

The marketplace manifest lives at `.github/plugin/marketplace.json`.

## GitHub Copilot CLI

Add the marketplace:

```bash
copilot plugin marketplace add ansys/pyaedt
```

Install the current plugin:

```bash
copilot plugin install pyaedt-cli@pyaedt-skills
```

## Claude Code

Claude uses `.claude-plugin/marketplace.json`, which is a symlink to `../.github/plugin/marketplace.json`.

## Maintenance

When you add or update a skill, place it under `.github/plugin/<plugin-name>/skills/`. Update `.github/plugin/marketplace.json` accordingly. The symlinked `.claude-plugin/marketplace.json` will pick up changes automatically.