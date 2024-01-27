from abc import ABCMeta, abstractmethod
from io import IOBase
from os import PathLike
from os.path import exists, basename, realpath

from simputils.config.enums import ConfigStoreType
from simputils.config.models import ConfigStore


class BasicFileHandler(metaclass=ABCMeta):

	CONFIG_TYPE: str = "abstract"

	@abstractmethod
	def process_file(self, file: PathLike | str | IOBase):  # pragma: no cover
		pass

	def supported_types(self) -> tuple:  # pragma: no cover
		return (self.CONFIG_TYPE,)

	def _prepare_conf(self, file):
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
