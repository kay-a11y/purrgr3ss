from pathlib import Path
from purrgress.utils.path import resolve_pathish
import yaml

_CFG_CACHE = None

def CFG():
    global _CFG_CACHE
    if _CFG_CACHE is None:
        path = resolve_pathish("purrgress/plog/config.yaml")
        _CFG_CACHE = yaml.safe_load(Path(path).read_text())
    return _CFG_CACHE
