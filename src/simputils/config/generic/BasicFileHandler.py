from abc import ABCMeta, abstractmethod
from io import IOBase
from os import PathLike
from os.path import exists, basename, realpath

from simputils.config.models import ConfigStore


class BasicFileHandler(metaclass=ABCMeta):

	CONFIG_TYPE: str = "abstract"

	@abstractmethod
	def process_file(self, file: PathLike | str | IOBase):  # pragma: no cover
		pass

	def supported_types(self) -> tuple:  # pragma: no cover
		return (self.CONFIG_TYPE,)

	def _prepare_conf(self, file):
		if not file or not exists(file):  # pragma: no cover
			return None

		return ConfigStore(
			name=basename(file),
			source=realpath(file),
			type=self.CONFIG_TYPE,
			handler=self,
		)
