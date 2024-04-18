import contextlib
import random
import string
import types
import typing
from contextvars import ContextVar
from datetime import datetime, timedelta
from typing import Type, Mapping, TypeVar, TypeGuard

from pydantic import BaseModel, RootModel, ValidationError
from pydantic_core import PydanticUndefined


def generate_random_string(mark=None, *, length=16):
    tok = ''.join(random.choices(string.ascii_letters, k=length))
    if mark is None:
        return tok
    return f"<{mark}.{tok}>"


_T = TypeVar('_T')
UNSET = object()
path = ContextVar[tuple[typing.Any, ...]]('path', default=())


def isrootmodel(t) -> TypeGuard[Type[RootModel]]:
    return issubclass(t, RootModel)


def ismodel(t) -> TypeGuard[Type[BaseModel]]:
    return issubclass(t, BaseModel)


@contextlib.contextmanager
def sub_path(p):
    pp = path.get()
    p_: tuple[typing.Any, ...] = (*pp, p)
    tok = path.set(p_)
    try:
        yield
    finally:
        path.reset(tok)


def generate_type(
        type_: Type[_T],
        constraint: Mapping[str, typing.Any] = None,
) -> _T:
    if constraint is None:
        constraint = {}

    try:
        if '$value' in constraint:
            value_ = constraint['$value']
            # assert isinstance(value_, type_)
            return value_

        if typing.get_origin(type_) in [typing.Union, types.UnionType]:
            sub_types = list(typing.get_args(type_))
            random.shuffle(sub_types)
            t, *rt = sub_types
            try:
                return generate_type(t, constraint)
            except Exception:
                # maybe constraint makes some subtypes unavailable
                # thus, all others will be tried in series.
                # call others in except block so all exceptions are chained
                return generate_type(typing.Union[*rt], constraint)

        if typing.get_origin(type_) is tuple:
            results = []
            for idx, t in enumerate(typing.get_args(type_)):
                with sub_path(str(idx)):
                    results.append(generate_type(t, constraint))
            return tuple(results)

        if typing.get_origin(type_) is typing.Literal:
            return random.choice(typing.get_args(type_))

        if typing.get_origin(type_) is dict:
            key_t, val_t = typing.get_args(type_)
            constraint = {**constraint}
            min_len = constraint.pop('$min_len', 1)
            max_len = constraint.pop('$max_len', 3)
            key_c = constraint.pop('$key', {})
            val_c = constraint.pop('$val', {})
            keys = [*constraint.keys()]
            length = random.randint(min_len, max_len)
            result = {}
            for _ in range(length):
                if keys:
                    key = keys.pop(random.randrange(len(keys)))
                else:
                    with sub_path('$key'):
                        key = generate_type(key_t, key_c)
                with sub_path(key):
                    val = generate_type(val_t, {**val_c, **constraint.get(key, {})})
                result[key] = val
            return result

        if typing.get_origin(type_) is not None:
            raise TypeError(f"{type_!r} is a parameterized generic but generate_type() don't know how to create one")

        if type_ is int:
            return random.randrange(constraint.get('$min', 0),
                                    constraint.get('$max', 65536))

        if type_ is str:
            return generate_random_string(constraint.get('field'))

        if type_ is bool:
            return bool(random.getrandbits(1))

        if type_ is datetime:
            return datetime.fromtimestamp(random.randrange(86400))

        if type_ is timedelta:
            return timedelta(random.random() * 86400)

        if type_ is float:
            return random.random() * 10000

        if type_ is dict:
            return constraint

        if type_ is types.NoneType or type_ is None:
            if constraint:
                raise ValueError('required None but have constraint')
            return None

        if isrootmodel(type_):
            return generate_type(type_.model_fields['root'].annotation, constraint)

        if ismodel(type_):
            result = {}
            for field, info in type_.model_fields.items():
                sub_type = info.annotation

                # constraint
                if field in constraint:
                    sub_constraint = constraint[field]
                    with sub_path(field):
                        if not isinstance(sub_constraint, Mapping):
                            result[field] = generate_type(sub_type, {'$value': sub_constraint})
                        else:
                            result[field] = generate_type(sub_type, sub_constraint)
                # default by model definition
                elif info.default is not PydanticUndefined:
                    result[field] = info.default
                elif info.default_factory is not None:
                    result[field] = info.default_factory()
                # generates
                else:
                    with sub_path(field):
                        result[field] = generate_type(sub_type, constraint.get(field, {}))
            try:
                return type_.model_validate(result)
            except ValidationError:  # noqa, only for debug
                raise ValueError(f"error when generating model, generated: {result}")

        raise NotImplementedError
    except Exception:  # noqa, only for debug
        raise TypeError(
            f"{path.get()} requires a `{type_!r}` "
            "but generate_type() don't know how to create one"
        )
