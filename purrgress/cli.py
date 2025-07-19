"""
🐾 purrgr3ss/cli.py - Markdown Productivity CLI
------------------------------------------------------

Central command-line entrypoint for the `purrgress` suite: lightweight tools
for maintaining markdown task boards, injecting date tokens, and archiving
completed work.

Usage:
    purrgress <subcommand> [options]

Examples:
    purrgress purrdate --file docs/purrboard.md --preview
    purrgress purrdate --write
    purrgress archive --preview
    purrgress archive

------------------------------------------------------
Current Subcommands

purrdate
    Update markdown files with current date/time tokens and/or anchored
    <!--DATE-XYZ--> blocks.
    Options:
      -f, --file         Target markdown file (default: docs/purrboard.md)
      --preview / -p     Show unified diff; do not write
      --write / -w       Apply changes
      --tags-only        Update {{TAGS}} only; skip anchors
      --anchors-only     Update anchors only; skip {{TAGS}}

archive
    Move completed tasks (* [x] / - [x]) from an ACTIVE block in the source
    board into a month bucket in the destination archive file. Removes them
    from the source by default.
    Options:
      --src              Source board (default: docs/purrboard.md)
      --dst              Archive file (default: docs/archived.md)
      --preview / -p     Show diffs; do not write

------------------------------------------------------
Markers

The archive tool looks for these markers in your markdown:

    <!-- ============= ACTIVE START ============= -->
    <!-- ============= ACTIVE END ============= -->

    <!-- ============= ARCHIVE START ============= -->
    <!-- ============= ARCHIVE END ============= -->

Content between ACTIVE markers is scanned for completed tasks. Archived items
are inserted just above ARCHIVE END, grouped under `## ✅ Done (YYYY-MM)`.

------------------------------------------------------
Install

Add this to pyproject.toml:

    [project.scripts]
    purrgress = "purrgress.cli:cli"

Then install editable:

    pip install -e .

Run anywhere in that environment:

    purrgress --help

------------------------------------------------------
Built with markdown, cats, and quiet persistence.
"""

import click
from purrgress.scripts.purrdate import purrdate
from purrgress.scripts.archive import archive

@click.group()
def cli():
    """purrgress: CLI tools for boards, dates, archiving."""
    pass

cli.add_command(purrdate)
cli.add_command(archive)
