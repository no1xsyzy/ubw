import json

__all__ = ('strange_dict',)


def strange_dict(cls, v):
    try:
        if isinstance(v, (str, bytes, bytearray,)):
            v = json.loads(v)
        if not v:
            return {}
        return v
    except (json.JSONDecodeError, TypeError):
        return {}
