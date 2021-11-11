from typing import Any, List


def listify(value: Any) -> List[Any]:
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]
