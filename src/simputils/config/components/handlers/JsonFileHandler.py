import json
from io import IOBase
from os import PathLike

from simputils.config.enums import ConfigStoreType
from simputils.config.exceptions import WrongFormat
from simputils.config.generic import BasicFileHandler
from simputils.config.models import ConfigStore


class JsonFileHandler(BasicFileHandler):

	CONFIG_TYPE: str = ConfigStoreType.JSON

	def process_file(self, file: PathLike | str | IOBase) -> ConfigStore | None:
		conf = self._prepare_conf(file)
		if conf is not None:

			# noinspection PyBroadException
			try:
				if isinstance(file, IOBase):
					data = json.loads(file.read())
					if not isinstance(data, dict):
						# MARK  Overlapping error and try/catch that should not catch this error
						raise WrongFormat("JSON file format root element must be dict")
				else:
					with open(file, "r") as fd:
						data = json.load(fd)
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
			except Exception as e:
				pass

		return None
