import click

from pathlib import Path
from purrgress.utils import read_lines, write_lines
from purrgress.utils.text import clean_punctuation
from purrgress.utils.path import resolve_pathish

@click.command("clean")
@click.argument("files", nargs=-1, type=str, required=True)
@click.option("-w", "--write", is_flag=True, 
              help="Overwrite the file(s) instead of printing.")
def clean_cmd(files: tuple[str], write: bool) -> None:
    for raw in files:
        path: Path = resolve_pathish(raw)

        text = "".join(read_lines(path, missing_ok=False))
        fixed = clean_punctuation(text)

        if write:
            write_lines(path, [fixed])
            click.secho(f"🖊️ scrubbed {path}", fg="green")
        else:
            click.echo(fixed)
