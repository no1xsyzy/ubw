# 自动化模块发现与导入
import importlib
import pkgutil
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from ._base import *

AnnotatedCommandModel = None
BLIVE_ADAPTER = None
__all__ = None


def _make_module():
    global AnnotatedCommandModel, BLIVE_ADAPTER, __all__

    package_path = Path(__file__).parent
    package_name = __name__
    discovered_models: list[type[CommandModel]] = []
    module_dict: dict[str, Any] = {}

    for importer, modname, ispkg in pkgutil.iter_modules([str(package_path)]):
        if modname in ('__init__', '_base'):
            continue
        try:
            module = importlib.import_module(f'{package_name}.{modname}')
            if hasattr(module, '__all__'):
                for attr_name in module.__all__:
                    attr = getattr(module, attr_name)
                    if attr not in discovered_models:
                        discovered_models.append(attr)
                        module_dict[attr_name] = attr
            else:
                for attr_name in dir(module):
                    if attr_name.startswith('_'):
                        continue
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                            issubclass(attr, CommandModel) and
                            attr is not CommandModel):
                        if attr not in discovered_models:
                            discovered_models.append(attr)
                            module_dict[attr_name] = attr
        except Exception as e:
            import warnings

            warnings.warn(f"Failed to import {modname}: {e}")

    globals().update(module_dict)
    AnnotatedCommandModel = Annotated[Union[tuple(discovered_models)], Field(discriminator='cmd')]
    BLIVE_ADAPTER = TypeAdapter(AnnotatedCommandModel)
    __all__ = (
        *sorted(module_dict.keys()),
        'Summary', 'Summarizer', 'CommandModel',
        'AnnotatedCommandModel', 'BLIVE_ADAPTER',
    )


_make_module()
