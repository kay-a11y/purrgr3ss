from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

def path_to(*subdirs) -> Path:
    return _REPO_ROOT.joinpath(*subdirs).resolve()

def resolve_pathish(pathish) -> Path:
    if isinstance(pathish, Path):
        return pathish if pathish.is_absolute() else path_to(*pathish.parts)

    s = str(pathish).strip()
    p = Path(s)
    if p.is_absolute():
        return p.resolve()

    parts = s.replace("\\", "/").split("/")
    parts = [p for p in parts if p]  
    return path_to(*parts)
