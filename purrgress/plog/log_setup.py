import logging

from rich.logging import RichHandler


def init(level="WARNING"):
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_time=level=="DEBUG")],
    )
    return logging.getLogger("plog")
