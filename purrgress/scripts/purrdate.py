from __future__ import annotations

import click
from purrgress.utils import read_lines, write_lines
from purrgress.utils.date import date_vars, anchored_date_lines
from purrgress.utils.markdown import inject_tags, replace_anchored_blocks, diff_preview

@click.command(name="purrdate")
@click.option('-f', '--file', default="docs/purrboard.md", show_default=True,
              help="Markdown file to update")
@click.option('-p', '--preview', is_flag=True, 
              help="Show changes without writing")
@click.option('-w', '--write', is_flag=True, 
              help="Actually write changes to file")
@click.option('--tags-only', is_flag=True, 
              help="Only update {{TAGS}} blocks; skip anchors.")
@click.option('--anchors-only', is_flag=True, 
              help="Only update <!--DATE-XYZ--> anchors; skip {{TAGS}}")

def purrdate(file, preview, write, tags_only, anchors_only):
    if tags_only and anchors_only:
        click.echo("⚠️  --tags-only and --anchors-only given; nothing to do. Choose one.")
        return
    
    original_lines = read_lines(file, missing_ok=False)
    original_text = "".join(original_lines)

    if anchors_only:
        updated_text = original_text
        lines = original_text.splitlines(keepends=True)
    else:
        tags = date_vars()
        updated_text = inject_tags(original_text, tags)
        lines = updated_text.splitlines(keepends=True)

    if not tags_only:
        lines = replace_anchored_blocks(lines, anchored_date_lines())

    if preview or not write:
        click.echo("\n🐈  Preview of Changes\n" + "-" * 40)
        click.echo(
            diff_preview(
                original_lines,
                lines,
                fromfile=f"{file} (orig)",
                tofile=f"{file} (new)",
            )
        )
        if not write:
            click.echo("\n💡 Use --write to apply changes.\n")
            return
        
    write_lines(file, lines)
    click.echo(f"😸 Updated: {file}")

__all__ = ["purrdate"]