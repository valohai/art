def listify(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]
