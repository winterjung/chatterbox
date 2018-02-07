def listify(obj):
    if obj is None:
        return []
    if isinstance(obj, (list, tuple)):
        return obj
    return [obj]
