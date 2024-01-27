import os
from io import IOBase
from os import PathLike

import dotenv

from simputils.config.enums import ConfigStoreType
from simputils.config.generic import BasicFileHandler
from simputils.config.models import ConfigStore


class DotEnvFileHandler(BasicFileHandler):
	"""
	Handles DotEnv files/io and creates `ConfigStore` from them
	"""

	CONFIG_TYPE: str = ConfigStoreType.DOT_ENV

	def process_file(self, file: PathLike | str | IOBase) -> ConfigStore | None:
		conf = self._prepare_conf(file)
		if conf is not None:

			# noinspection PyBroadException
			# try:
			if isinstance(file, IOBase):
				data = dotenv.dotenv_values(stream=file)
				return conf.config_apply(
					dict(data),
					name=conf.name,
					source=conf.source,
					type=conf.type,
					handler=self,
				)
			elif os.path.splitext(file)[1] in (".env",):
				data = dotenv.dotenv_values(file)
				return conf.config_apply(
					dict(data),
					name=conf.name,
					source=conf.source,
					type=conf.type,
					handler=self,
				)
			# except Exception:  # pragma: no cover
			# 	pass

		return None  # pragma: no cover
