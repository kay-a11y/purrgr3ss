from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

def path_to(*subdirs) -> Path:
    """
    Return an absolute path from the project root.

    Example:
        path_to('docs', 'purrboard.md')
    """
    return _REPO_ROOT.joinpath(*subdirs).resolve()
