from logging import getLogger
from pathlib import Path

import yaml

from purrgress.utils.path import resolve_pathish

_CFG_CACHE = None
log = getLogger("plog")

def CFG() -> dict | None:
    """
    Return the parsed config dict (moods / tags / badges).

    Returns:
        dict | None: The parsed config, or None if not found or failed.

    Raises:
        Exception: If the config file cannot be read or parsed.
    """
    global _CFG_CACHE

    if _CFG_CACHE is None:
        try:
            path = resolve_pathish("purrgress/plog/config.yaml")
            _CFG_CACHE = yaml.safe_load(Path(path).read_text())
        except Exception as e:
            log.error("[CFG] Failed to read config file: %s. Edit the config file first, which is 'purrgress/plog/config.yaml' by default", e)
            raise
    return _CFG_CACHE
