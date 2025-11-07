# Claude Skills Collection

A curated collection of custom skills that extend Claude Code's capabilities with specialized knowledge, workflows, and tool integrations.

## What are Skills?

Skills are modular packages that provide Claude with domain-specific expertise. They contain:
- **Specialized workflows** - Multi-step procedures for specific tasks
- **Tool integrations** - Instructions for working with file formats, APIs, and tools
- **Domain knowledge** - Framework-specific patterns, best practices, and reference material
- **Bundled resources** - Scripts, templates, and reference documentation

## Skills by Category

### 📄 Document Processing
Professional document manipulation and analysis tools.

| Skill | Description | License |
|-------|-------------|---------|
| **[pdf](pdf/)** | Extract text/tables, create PDFs, merge/split documents, handle forms | Proprietary |
| **[docx](docx/)** | Create/edit Word documents with tracked changes, comments, formatting | Proprietary |
| **[pptx](pptx/)** | Create/edit PowerPoint presentations with layouts and speaker notes | Proprietary |
| **[xlsx](xlsx/)** | Spreadsheet creation, formulas, data analysis, and visualization | Proprietary |

### 🛠️ Development Tools
Tools for building applications and managing workflows.

| Skill | Description | License |
|-------|-------------|---------|
| **[claude-agent-ts-sdk](claude-agent-ts-sdk/)** | Build Claude agents using TypeScript - tools, streaming, patterns | MIT |
| **[svelte-5-runes](svelte-5-runes/)** | Complete guide for Svelte 5 reactive state management | MIT |
| **[webapp-testing](webapp-testing/)** | Test local web applications using Playwright | Apache-2.0 |

### 🌐 APIs & Integrations
Domain-specific API integration and data access.

| Skill | Description | License |
|-------|-------------|---------|
| **[worldcat-api](worldcat-api/)** | Search WorldCat for bibliographic data, ISBNs, library holdings | MIT |
| **[omeka-s](omeka-s/)** | Expert Omeka S development - themes, modules, Docker configuration | MIT |

### 🔧 Meta
Tools for working with skills themselves.

| Skill | Description | License |
|-------|-------------|---------|
| **[skill-creator](skill-creator/)** | Guide and tooling for creating effective skills | Apache-2.0 |

## Quick Start

### Installation

1. Copy skill directories to your Claude Code skills directory:
   ```bash
   cp -r <skill-name> ~/.claude/skills/
   ```

2. Skills are automatically loaded by Claude Code on startup.

### Usage

Skills activate automatically when relevant to your task. For example:
- Mention "PDF" or work with `.pdf` files → `pdf` skill activates
- Ask about Svelte 5 or use `$state` → `svelte-5-runes` skill activates
- Request to build an agent → `claude-agent-ts-sdk` skill activates

## Creating Your Own Skills

Use the **skill-creator** skill to learn how to create custom skills:

1. Study existing skills in this collection
2. Use `skill-creator/scripts/init_skill.py` to scaffold a new skill
3. Follow the progressive disclosure pattern (SKILL.md → references → assets)
4. Package with `skill-creator/scripts/package_skill.py`

See [skill-creator/SKILL.md](skill-creator/SKILL.md) for detailed guidance.

## License

This collection contains skills under different licenses:
- **MIT**: claude-agent-ts-sdk, omeka-s, worldcat-api, svelte-5-runes
- **Apache-2.0**: skill-creator, webapp-testing
- **Proprietary**: docx, pdf, pptx, xlsx (see individual LICENSE.txt files)

See each skill's LICENSE.txt file for complete terms.

## Contributing

Contributions are welcome! When adding skills:
1. Follow the skill structure guidelines in skill-creator
2. Include complete YAML frontmatter (name, description, license)
3. Add appropriate LICENSE.txt file
4. Update this README with your skill in the appropriate category
