from os.path import exists, basename, realpath

import yaml

from simputils.config.generic import BasicFileHandler, BasicConfigStore
from simputils.config.models import ConfigStore


class YamlFileHandler(BasicFileHandler):

	CONFIG_TYPE: str = "YAML"

	def supported_types(self) -> tuple:
		return (self.CONFIG_TYPE, )

	def process_file(self, file: str) -> BasicConfigStore | None:
		if not exists(file):
			print("File does not exist")
			return None
		conf = ConfigStore()
		# noinspection PyBroadException
		try:
			with open(file, "r") as fd:
				return conf.config_apply(
					yaml.safe_load(fd),
					name=basename(file),
					source=realpath(file),
					type=self.CONFIG_TYPE,
				)
		except:
			return None
