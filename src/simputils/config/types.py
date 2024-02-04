from argparse import Namespace
from io import IOBase
# noinspection PyUnresolvedReferences,PyProtectedMember
from os import _Environ, PathLike
from typing import Union, Callable, Iterable, Any

ConfigType = Union[_Environ, Namespace, dict]

FilterType = Union[bool, Iterable, Callable[[str, Any], bool]]

PreProcessorType = Union[dict, list[Callable[[str, Any], tuple[str, Any]]], Callable[[str, Any], tuple[str, Any]]]

SourceType = Union[str, object]

HandlerType = Union[Callable]

FileType = Union[str, PathLike, IOBase]
