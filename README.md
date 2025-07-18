# 🐾 purrgr3ss

[![🐱 Open Taskboard](https://img.shields.io/badge/🐱_Open_Taskboard-ff69b4?style=flat-square)](/docs/purrboard.md)
[![🌈 View Tags](https://img.shields.io/badge/View_Tags-ffb347?style=flat-square)](/docs/purrboard.md)
[![🏷️ Badge List](https://img.shields.io/badge/Badge_List-87ceeb?style=flat-square)](/docs/purrboard.md)

Lightweight markdown task boards / todo list + Python CLI automation.

🐈‍⬛ **purrgr3ss** is text‑first. Use git. Archive often. Pet cat. Repeat.

**CLI command:** `purrgress`

## What It Does

* Maintain a markdown task board (`docs/purrboard.md`) with visual badges + tags.
* Auto‑inject rolling dates (today / ISO week / month) into placeholders and anchored comment blocks.
* Sweep completed tasks into an archive file (`docs/archived.md`), grouped by month.
* Preview all changes before writing.

Minimal. Text‑based. Git‑friendly.

## Install

From the repo root:

```bash
pip install -e .
```

This installs the console script **`purrgress`** into your environment.

Run:

```bash
purrgress --help
purrgress purrdate --write # initialize date tags
```

## Subcommands

### `purrgress purrdate`

Update date placeholders and/or anchored date blocks in a markdown file.

**Default target:** `docs/purrboard.md`

**Tokens supported** (from `purrgress.utils.date.date_vars()`):

* `{{DATE_TODAY}}`
* `{{DATE_WEEK}}`
* `{{DATE_WEEK_RANGE}}`
* `{{DATE_MONTH}}`
* `{{LAST_UPDATED}}`

**Anchors:** HTML comments followed by a `<sub>` line are rewritten, e.g.

```markdown
<!--DATE-TODAY-->
<sub><em>{{DATE_TODAY}}</em></sub>
```

**Flags:**

```bash
purrgress purrdate -f docs/purrboard.md --preview   # show diff only
purrgress purrdate -f docs/purrboard.md --write     # apply
purrgress purrdate --tags-only                      # update {{...}} only
purrgress purrdate --anchors-only                   # update anchors only
```

> If neither `--write` nor `--preview` is given, a preview is shown (no write).

### `purrgress archive`

Move completed tasks from the **ACTIVE** block in a board into a month bucket in an archive file.

**Defaults:**

* Source board: `docs/purrboard.md`
* Destination archive: `docs/archived.md`
* Removes archived tasks from source.

**Preview first:**

```bash
purrgress archive --preview
```

**Apply:**

```bash
purrgress archive
```

**Console output:**

```txt
📤 Archived N items to docs/archived.md
🧹 Removed N items from docs/purrboard.md
```

#### ACTIVE & ARCHIVE Markers

`archive` looks for these comment markers:

```markdown
<!-- ============= ACTIVE START ============= -->
... active task sections ...
<!-- ============= ACTIVE END ============= -->

<!-- ============= ARCHIVE START ============= -->
... archived content will be inserted above END ...
<!-- ============= ARCHIVE END ============= -->
```

Archived items are grouped under headers like:

```markdown
## ✅ Done (2025-07)
* [x] Example task <span class="tag tag-primary">#proj.demo</span>
```

Duplicate completed lines (same first line) are skipped.

## Board Markup Basics

A task line:

```markdown
* [ ] ![todo][todo] Write docs <span class="tag tag-primary">#proj.docs</span>
```

Completed:

```markdown
* [x] ![done][done] Write docs <span class="tag tag-primary">#proj.docs</span>
```

Optional continuation (timestamp, notes) — in the line *directly after* the bullet:

```markdown
(2025-07-17T13:00:00+00:00)
```

(Indented continuation lines are moved with the task when archived.)

## Badge / Tag Quick Reference

Sample status badges (generated via [shields.io](https://shields.io)):

![todo](https://img.shields.io/badge/status-QUEUE-blue?style=plastic&logo=github)
![wip](https://img.shields.io/badge/status-WIP-orange?style=flat-square)
![done](https://img.shields.io/badge/status-DONE-brightgreen?style=flat-square)

See:

* [`docs/badges.md`](docs/badges.md)
* [`docs/tags.md`](docs/tags.md)

## Dev Notes

* Works best with VS Code + Markdown Preview Enhanced (or similar markdown render).
* Apply custom CSS under `docs/assets/css/purrgress.css` to markdown render.
* All paths resolved relative to repo root; CLI accepts forward‑slash paths.
* Editable install means code changes are picked up without reinstall, unless you change dependencies.