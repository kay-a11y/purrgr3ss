from __future__ import annotations

import click
import re
from datetime import datetime
from purrgress.utils import read_lines, write_lines
from purrgress.utils.markdown import diff_preview
from typing import List, Tuple

# ------------------------------------------------------------------
# Marker constants (customize if you change markup in your docs)
# ------------------------------------------------------------------
ACTIVE_START = "<!-- ============= ACTIVE START ============= -->"
ACTIVE_END   = "<!-- ============= ACTIVE END ============= -->"

ARCHIVE_START = "<!-- ============= ARCHIVE START ============= -->"
ARCHIVE_END   = "<!-- ============= ARCHIVE END ============= -->"

DONE_BULLET_RE = re.compile(r'^\s*[-*]\s*\[[xX]\]\s')

def _is_continuation_line(line: str) -> bool:
    stripped = line.strip()
    if stripped == "":
        return False
    if stripped.startswith("* [") or stripped.startswith("- ["):
        return False
    if stripped.startswith("#"):
        return False
    if stripped.startswith("<!-- ============="):
        return False
    return True

def _find_block(lines: List[str], start_marker: str, end_marker: str) -> Tuple[int, int]:
    start_idx = None
    end_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == start_marker:
            start_idx = i + 1
        elif ln.strip() == end_marker and start_idx is not None and end_idx is None:
            end_idx = i 
            break
    if start_idx is None or end_idx is None or end_idx < start_idx:
        return 0, len(lines)
    return start_idx, end_idx

def _extract_completed_tasks(block_lines: List[str]) -> Tuple[List[str], List[List[str]]]:
    remaining: List[str] = []
    archived_blocks: List[List[str]] = []

    i = 0
    n = len(block_lines)
    while i < n:
        ln = block_lines[i]
        if DONE_BULLET_RE.match(ln):
            task_block = [ln]
            i += 1
            while i < n and _is_continuation_line(block_lines[i]):
                task_block.append(block_lines[i])
                i += 1
            archived_blocks.append(task_block)
            continue
        else:
            remaining.append(ln)
            i += 1

    return remaining, archived_blocks

def _ensure_archive_skeleton(dst_lines: List[str]) -> List[str]:
    if any(ln.strip() == ARCHIVE_START for ln in dst_lines) and any(ln.strip() == ARCHIVE_END for ln in dst_lines):
        return dst_lines 

    skeleton = [
        "# Archive\n\n",
        '<div class="purrboard">\n\n',
        f"{ARCHIVE_START}\n\n",
        f"{ARCHIVE_END}\n\n",
        "</div>\n",
    ]
    return skeleton

def _find_month_section(dst_lines: List[str], ym: str) -> Tuple[int, int]:
    insert_idx = len(dst_lines)
    end_idx = None
    for i, ln in enumerate(dst_lines):
        if ln.strip() == ARCHIVE_END:
            insert_idx = i
            break
    pattern = f"## ✅ Done ({ym})"
    for i, ln in enumerate(dst_lines):
        if ln.strip().startswith("## ") and pattern in ln:
            return insert_idx, i
    return insert_idx, -1

def _gather_existing_archive_keys(dst_lines: List[str]) -> set[str]:
    keys = set()
    for ln in dst_lines:
        if DONE_BULLET_RE.match(ln):
            key = " ".join(ln.strip().split())
            keys.add(key)
    return keys

def _flatten_blocks(blocks: List[List[str]]) -> List[str]:
    flat: List[str] = []
    for blk in blocks:
        flat.extend(blk)
        if not blk[-1].endswith("\n"):
            flat.append("\n")
    return flat


@click.command(name="archive")
@click.option("--src", default="docs/purrboard.md", show_default=True,
              help="Active purrboard markdown file to sweep.")
@click.option("--dst", default="docs/archived.md", show_default=True,
              help="Archive destination file.")
@click.option("--preview", is_flag=True,
              help="Preview diff; do not modify files.")
def archive(src: str, dst: str, preview: bool) -> None:
    src_lines = read_lines(src)
    start, end = _find_block(src_lines, ACTIVE_START, ACTIVE_END)
    active_block = src_lines[start:end]
    remain_block, archived_blocks = _extract_completed_tasks(active_block)

    archived_count = sum(1 for _ in archived_blocks)

    if archived_count == 0:
        click.echo("😺 Nothing to archive. All clean!")
        return

    new_src_lines = src_lines[:start] + remain_block + src_lines[end:]

    dst_lines = read_lines(dst)
    dst_lines = _ensure_archive_skeleton(dst_lines)

    ym = datetime.now().strftime("%Y-%m")
    insert_idx, existing_idx = _find_month_section(dst_lines, ym)
    existing_keys = _gather_existing_archive_keys(dst_lines)

    new_blocks_filtered: List[List[str]] = []
    for blk in archived_blocks:
        key = " ".join(blk[0].strip().split())
        if key in existing_keys:
            continue
        new_blocks_filtered.append(blk)

    new_dst_lines = dst_lines[:]
    if existing_idx == -1:
        header = f"## ✅ Done ({ym})\n\n"
        new_dst_lines[insert_idx:insert_idx] = [header]
        insert_idx += 2 

    flat_archived_lines = _flatten_blocks(new_blocks_filtered)
    if flat_archived_lines:
        new_dst_lines[insert_idx:insert_idx] = flat_archived_lines

    if preview:
        click.echo("\n🐾 PREVIEW: SOURCE CHANGES\n" + "-"*32)
        click.echo(
            diff_preview(src_lines, new_src_lines,
                        fromfile=f"{src} (orig)", tofile=f"{src} (new)")
        )

        click.echo("\n🐾 PREVIEW: ARCHIVE CHANGES\n" + "-"*32)
        click.echo(
            diff_preview(dst_lines, new_dst_lines,
                        fromfile=f"{dst} (orig)", tofile=f"{dst} (new)")
        )
        click.echo("\n💡 Use without --preview to apply.\n")
        return

    write_lines(src, new_src_lines)
    write_lines(dst, new_dst_lines)

    archived_added = len(new_blocks_filtered)
    click.echo(f"📤 Archived {archived_added} items to {dst}")
    click.echo(f"🧹 Removed {archived_count} items from {src}")
