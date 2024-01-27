import json
import os
from io import IOBase
from os import PathLike

from simputils.config.enums import ConfigStoreType
from simputils.config.exceptions import WrongFormat
from simputils.config.generic import BasicFileHandler
from simputils.config.models import ConfigStore


class JsonFileHandler(BasicFileHandler):

	CONFIG_TYPE: str = ConfigStoreType.JSON

	def _prepare_from_io(self, file, conf):
		data = json.load(file)
		if not isinstance(data, dict):
			# MARK  Overlapping error and try/catch that should not catch this error
			raise WrongFormat("JSON file format root element must be dict")
		return conf.config_apply(
			dict(data),
			name=conf.name,
			source=conf.source,
			type=conf.type,
			handler=self,
		)

	def process_file(self, file: PathLike | str | IOBase) -> ConfigStore | None:
		conf = self._prepare_conf(file)
		if conf is not None:
			if isinstance(file, IOBase):
				return self._prepare_from_io(file, conf)
			elif os.path.splitext(file)[1] in (".json", ):
				with open(file, "r") as fd:
					return self._prepare_from_io(fd, conf)

		return None
