from __future__ import annotations

from pathlib import Path
from purrgress.utils.path import resolve_pathish
from typing import Iterable, List, Union

Pathish = Union[str, Path]

def read_lines(pathish: Pathish, missing_ok: bool = True, encoding: str = "utf-8") -> List[str]:
    p = resolve_pathish(pathish)
    try:
        with p.open("r", encoding=encoding) as f:
            return f.readlines()
    except FileNotFoundError:
        if missing_ok:
            return []
        raise

def write_lines(pathish: Pathish, lines: Iterable[str], encoding: str = "utf-8") -> None:
    p = resolve_pathish(pathish)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding=encoding) as f:
        for ln in lines:
            f.write(ln)

__all__ = ["read_lines", "write_lines"]
