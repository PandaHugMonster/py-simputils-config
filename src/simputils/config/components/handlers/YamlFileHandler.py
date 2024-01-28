import os
from io import IOBase

import yaml

from simputils.config.enums import ConfigStoreType
from simputils.config.generic import BasicFileHandler
from simputils.config.models import ConfigStore
from simputils.config.types import FileType


class YamlFileHandler(BasicFileHandler):
	"""
	Handles YAML files/io and creates `ConfigStore` from them
	"""

	CONFIG_TYPE: str = ConfigStoreType.YAML

	def process_file(self, file: FileType) -> ConfigStore | None:
		# NOTE  For some weird reason PyYAML parsing json successfully.
		#       It is unreasonable architecturally, so JSONs are explicitly excluded

		conf = self._prepare_conf(file)
		if conf is not None:

			if isinstance(file, IOBase):
				return conf.config_apply(
					yaml.safe_load(file),
					name=conf.name,
					source=conf.source,
					type=conf.type,
					handler=self,
				)
			elif os.path.splitext(file)[1] in (".yml", ".yaml"):
				with open(file, "r") as fd:
					return conf.config_apply(
						yaml.safe_load(fd),
						name=conf.name,
						source=conf.source,
						type=conf.type,
						handler=self,
					)

		return None
