import logging, functools, inspect

def log_call(level=logging.DEBUG):
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
    return ", ".join(f"{k}={v!r}" for k, v in params.items())
