import yaml

def dump_no_wrap(data: dict) -> str:
    """
    Dump YAML without automatic line-wrapping so long scalars stay intact.
    """
    return yaml.dump(
        data,
        sort_keys=False,
        width=10**9,
        allow_unicode=True,
    )