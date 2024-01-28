from abc import ABCMeta, abstractmethod
from io import IOBase
from os.path import exists, basename, realpath

from simputils.config.enums import ConfigStoreType
from simputils.config.types import FileType


class BasicFileHandler(metaclass=ABCMeta):
	"""
	The main ancestor of all file-handlers

	If you want to implement your custom handler, please inherit from this one
	"""

	CONFIG_TYPE: str = "abstract"

	@abstractmethod
	def process_file(self, file: FileType):  # pragma: no cover
		pass

	def supported_types(self) -> tuple:  # pragma: no cover
		return (self.CONFIG_TYPE,)

	def _prepare_conf(self, file: FileType):
		from simputils.config.models import ConfigStore

		if isinstance(file, IOBase):
			name = type(file).__name__
			source = file
			_type = ConfigStoreType.IO.value
		else:
			if not file or not exists(file):  # pragma: no cover
				return None
			name = basename(file)
			source = realpath(file)
			_type = self.CONFIG_TYPE

		return ConfigStore(
			name=name,
			source=source,
			type=_type,
			handler=self,
		)

	def __call__(self, file: FileType):
		return self.process_file(file)
