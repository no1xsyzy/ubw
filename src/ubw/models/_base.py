import json
from base64 import b64decode

from pydantic import BeforeValidator, TypeAdapter, BaseModel

__all__ = ('strange_dict', 'protobuf_decoder',)


def strange_dict(cls, v):
    try:
        if isinstance(v, (str, bytes, bytearray,)):
            v = json.loads(v)
        if not v:
            return {}
        return v
    except (json.JSONDecodeError, TypeError):
        return {}


def protobuf_decoder(pb, model_type: type[BaseModel], *, base64=True):
    """Example Usage:
        class SomeModel(BaseModel):
            # ...
            some_field: Annotated[SubModel, protobuf_decoder(some_pb.SomeMessage, SubModel)]
            # ...
    """

    ta = TypeAdapter(model_type)

    def validator(v):
        if not isinstance(v, str):
            return v
        v = v.encode()
        if base64:
            v = b64decode(v)
        message = pb()
        message.ParseFromString(v)
        model = ta.validate_python(message, from_attributes=True)
        return model

    return BeforeValidator(validator)
