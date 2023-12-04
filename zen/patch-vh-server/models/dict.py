from dataclasses import asdict
from typing import Any, Dict


def asdict_remove_none(obj) -> Dict[str, Any]:
    d = asdict(obj)
    return recursive_remove_none(d)


def recursive_remove_none(d) -> Any:
    if not isinstance(d, dict):
        return d

    copy: Dict[str, Any] = {}

    for k, v in d.items():
        if isinstance(v, dict):
            copy[k] = recursive_remove_none(v)
        elif isinstance(v, list):
            list_copy = []
            for i in v:
                list_copy.append(recursive_remove_none(i))
            copy[k] = list_copy
        elif v is not None:
            copy[k] = v

    return copy
