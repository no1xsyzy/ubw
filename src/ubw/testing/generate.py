import random
import string
import types
import typing
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


def isrootmodel(t) -> TypeGuard[Type[RootModel]]:
    return issubclass(t, RootModel)


def ismodel(t) -> TypeGuard[Type[BaseModel]]:
    return issubclass(t, BaseModel)


def generate_type(
        type_: Type[_T],
        constraint: Mapping[str, typing.Any] = None,
) -> _T:
    # print(f'{type_=} {constraint=}')
    if constraint is None:
        constraint = {}

    path = constraint.setdefault('@@path', '')

    try:
        if '$value' in constraint:
            value_ = constraint['$value']
            # assert isinstance(value_, type_)
            return value_

        if typing.get_origin(type_) in [typing.Union, types.UnionType]:
            sub_types = list(typing.get_args(type_))
            random.shuffle(sub_types)
            err = None
            for t in sub_types:  # maybe constraint makes some subtypes unavailable
                try:
                    return generate_type(t, constraint)
                except Exception as e:
                    err = e
            raise err

        if typing.get_origin(type_) is tuple:
            results = []
            for idx, t in enumerate(typing.get_args(type_)):
                results.append(generate_type(t, {**constraint, '@@path': path + '.' + str(idx)}))
            return tuple(results)

        if typing.get_origin(type_) is typing.Literal:
            return random.choice(typing.get_args(type_))

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
            return {}

        if type_ is types.NoneType or type_ is None:
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
                    if not isinstance(sub_constraint, Mapping):
                        result[field] = generate_type(sub_type,
                                                      {'$value': sub_constraint, '@@path': path + '.' + field})
                    else:
                        result[field] = generate_type(sub_type,
                                                      {**sub_constraint, '@@path': path + '.' + field})
                # default by model definition
                elif info.default is not PydanticUndefined:
                    result[field] = info.default
                elif info.default_factory is not None:
                    result[field] = info.default_factory()
                # generates
                else:
                    result[field] = generate_type(sub_type,
                                                  {**constraint.get(field, {}), '@@path': path + '.' + field})
            try:
                # print(f"integrating {path}")
                return type_.model_validate(result)
            except ValidationError:  # noqa, only for debug
                raise ValueError(f"error when generating model, generated: {result}")

        raise NotImplementedError
    except Exception:  # noqa, only for debug
        raise TypeError(
            f"{path} requires a `{type_!r}` "
            "but generate_type() don't know how to create one"
        )
