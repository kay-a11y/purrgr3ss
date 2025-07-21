# 🐾 purrgr3ss

[![🐱 Open Taskboard](https://img.shields.io/badge/🐱_Open_Taskboard-ff69b4?style=flat-square)](/docs/purrboard.md)
[![Archive](https://img.shields.io/badge/😽_Open_Archive-86FAA1?style=flat-square)](/docs/archived.md)
[![🌈 View Tags](https://img.shields.io/badge/View_Tags-ffb347?style=flat-square)](/docs/tags.md)
[![🏷️ Badge List](https://img.shields.io/badge/Badge_List-87ceeb?style=flat-square)](/docs/badges.md)

*Markdown task-boards  / todo list* **(`purg`)** + *Life-log / study tracker* **(`plog`)**, generating the latest **heat-map**, all version-controlled with git.

![plog demo](/assets/img/plog-demo.gif)

![Heat-map Preview](/purrgress/visuals/2025/06_heatmap_viridis.png)

<details>
<summary>🌑 Click to preview the dark mode</summary>
<p align="center">
  <img src="/purrgress/visuals/2025/06_heatmap_viridis_dark.png" alt="theme" width="100%" style="filter: brightness(100%)">
</p>
</details>

## Quick Start

```bash
pip install -e .

# board workflow:
purrgress purrdate --write # initialize date tags
# add and finish tasks in `/docs/purrboard.md`
purg archive               # sweep completed tasks

# life-log workflow:
plog start "write docs" -t write.doc
plog stop
plog day                   # clipboard summary
plog heatmap --theme viridis # generate visuals/2025/07_heatmap_magma.png
```

## Feature

| | **purg** - task board | **plog** - life log |
|---|---|---|
| Core file(s) | `docs/purrboard.md` | `purrgress/data/<year>/<month>.yaml` |
| Key commands | `add`, `archive`, `purrdate`, `clean` | `start/stop`, `wake/sleep`, `status`, `day`, `month`, `heatmap`, `tidy` |
| Tags & badges | `/docs/tags.md` & `/docs/badges.md`  | `plog/config.yaml` (can be shared) |
| Output | Pretty markdown with shield badges | YAML + PNG heat-maps |
| Automation hooks | Pre-commit board tidy | Auto-tidy YAML on every write |

**purg**:

* Maintain a markdown task board (`docs/purrboard.md`) with visual badges + tags.
* Auto-inject rolling dates (today / ISO week / month) into placeholders and anchored comment blocks.
* Sweep completed tasks into an archive file (`docs/archived.md`), grouped by month.
* Preview all changes before writing.

Minimal. Text-based. Git-friendly.

---

**plog**:

* **One-keystroke life-logging** - `plog start/stop` captures every study/work span; prompts with an arrow-key checklist if you omit tags or moods.
* **Wake / sleep tracking** - `plog wake` & `plog sleep` stamp your daily rhythm for later analysis.
* **Instant summaries** - `plog status`, `plog day`, `plog month` echo totals.
* **Heat-map generator** - `plog heatmap --theme magma --dark` turns any month into a colourful hour-by-day PNG (saved under `purrgress/visuals/`).
* **Cross-midnight smartness** - spans that roll past 00 : 00 are bucketed into the proper days on your charts.
* **Auto-tidy YAML** - every write dedupes, sorts, merges sessions, and keeps long task lines un-wrapped. One-shot `plog tidy` retro-cleans old months.
* **Shared config** - moods, tag codes, and badge URLs live in `plog/config.yaml`.
* **Dark-mode plotting** - add `--dark` to heat-maps for a charcoal canvas that pops at 3 AM.
* **Fully tested** - pytest fixtures sandbox all logs, so `pytest -q` runs green without touching your real data.

CLI-first. YAML-backed. Git-versioned.

## Install

This installs two console scripts:

* **`purg`** - board automation (`purrgress = "purrgress.cli:cli"`)
* **`plog`** - life-log tool (`plog   = "purrgress.plog_cli:cli"`)

## CLI cheat-sheets

Learn more details in [wiki](https://github.com/kay-a11y/purrgr3ss/wiki).

### purg

```bash
purg purrdate        # update {{DATE_*}} placeholders
purg archive         # move completed tasks → archive
purg clean           # unicode-punct normalize
```

### plog

```bash
plog start <task> [-t TAG] [-m MOOD]    # prompts if omitted
plog stop                               # close session
plog wake HH:MM                         # log wake time
plog sleep HH:MM                        # log sleep
plog status                             # open session + today total
plog day                                # day total
plog month                              # month total
plog heatmap [--theme viridis] [--dark] # make PNG
plog tidy                               # sort/dedupe YAML
```

## Dev

```bash
pip install -e .[dev]
pytest -q     # 100% green
```
