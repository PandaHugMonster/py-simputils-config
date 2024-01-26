import json

from simputils.config.enums import ConfigStoreType
from simputils.config.generic import BasicFileHandler
from simputils.config.models import ConfigStore


class JsonFileHandler(BasicFileHandler):

	CONFIG_TYPE: str = ConfigStoreType.JSON

	def process_file(self, file: str) -> ConfigStore | None:
		conf = self._prepare_conf(file)
		if conf is not None:

			# noinspection PyBroadException
			try:
				with open(file, "r") as fd:
					data = json.load(fd)
					if not isinstance(data, dict):
						# MARK  Overlapping error and try/catch that should not catch this error
						raise Exception("JSON file format root element must be dict")

					return conf.config_apply(data)
			except:
				pass

		return None
