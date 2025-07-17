# 🐾 purrgr3ss

A sleek all-in-one CLI + markdown task manager.  
Track and organize your to-do board with visual tags and scriptable workflows.

[![Open Taskboard](https://img.shields.io/badge/🐱_Open--Taskboard-ff5e98?style=for-the-badge)](/docs/purrboard.md)

## 💡 Feature

- A customizable markdown board (`purrboard.md`) with **badge-based visual tasks**
- A Python-powered CLI to inject dates, archive tasks, and organize markdown fast
- A beautiful badge + tag system to color-code and filter your work

## 🛠️ CLI Quickstart

Install locally:

```bash
pip install -e .
```

Run with:

```bash
purrgress purrdate --preview
```

Options:

* `--file` or `-f`: path to your markdown board (default: `docs/purrboard.md`)
* `--preview`: see the output before writing changes
* `--tags-only`: only inject date/tags without editing anchored blocks

## 📁 Folder Map

```
purrgr3ss/
├── docs/
│   ├── purrboard.md       ← Your main task board
│   ├── tags.md            ← Tag palette reference
│   └── badges.md          ← Badge style swatches
├── purrgress/
│   ├── cli.py             ← Command-line entry point
│   └── utils/             ← Logic for tag/date injection
├── archive/               ← [Optional] Auto-saved completed tasks
├── .crossnote/            ← MPE styling: custom CSS, HTML head, etc.
└── pyproject.toml         ← Install as CLI: `purrgress`
```

## 🏷️ Badges & Tags

Use Markdown checkboxes + styled tags to categorize tasks:

```markdown
* [ ] ![learn][learn] _Start DCT chapter_ <span class="tag tag-primary">#ml.course</span>
```

Explore:

* [Badges](/docs/badges.md)
* [Tags](/docs/tags.md)

## 🧹 Archiving Logic

When a task is marked `[x]`, run:

```bash
purrgress archive
```

☑ Completed entries will be **auto-moved** to `archive/`, with date stamps preserved.

## 🐱 Nerd Notes

* Styling powered by [Markdown Preview Enhanced](https://shd101wyy.github.io/markdown-preview-enhanced/)
* Custom `.less` styles live in `.crossnote/style.less`
* Taskboards are version-controllable, commit-friendly, and nerd-approved™

---

[![Last Sweep](https://img.shields.io/github/last-commit/kay-a11y/purrgr3ss?style=flat-square)](/docs/purrboard.md)