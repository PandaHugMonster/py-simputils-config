from argparse import Namespace
from io import IOBase
from os import _Environ, PathLike
from typing import Union, Callable, Iterable, Any, TYPE_CHECKING

if TYPE_CHECKING:
	# noinspection PyUnresolvedReferences
	from simputils.config.generic import BasicConfigStore, BasicFileHandler

ConfigType = Union[_Environ, Namespace, dict, "BasicConfigStore"]

FilterType = Union[bool, Iterable, Callable[[str, Any], bool]]

PreProcessorType = Union[dict, Callable[[str, Any], tuple[str, Any]]]

SourceType = Union[str, object]

HandlerType = Union[Callable, "BasicFileHandler"]

FileType = Union[str, PathLike, IOBase]
