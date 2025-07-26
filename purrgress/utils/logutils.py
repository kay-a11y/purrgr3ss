"""
Add the decorator `@log_call()` above any function. If you stack multiple decorators, each one gets its own line, but they must all be directly before the function.

Custom level: `@log_call(logging.INFO)`

Example:

```python
@log_call()
def stop_session(...): ...

@log_group.command()
@log_call(logging.INFO)
def my_cli_command():
    ...
```
"""

import functools
import inspect
import logging


def log_call(level=logging.DEBUG):
    """
    Decorator: log entry (and exit) with args/kwargs at chosen level.
    Skips string-building unless the logger is enabled for `level`.
    """

    def decorator(func):
        log = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if log.isEnabledFor(level):
                bound = inspect.signature(func).bind_partial(*args, **kwargs)
                bound.apply_defaults()
                log.log(level, "%s(%s)", func.__name__, _fmt_params(bound.arguments))
            result = func(*args, **kwargs)
            if log.isEnabledFor(level):
                log.log(level, "%s -> %r", func.__name__, result)
            return result

        return wrapper

    return decorator

def _fmt_params(params: dict) -> str:
    """
    Compact k=v, k2=v2 … string for logging.
    """
    return ", ".join(f"{k}={v!r}" for k, v in params.items())
