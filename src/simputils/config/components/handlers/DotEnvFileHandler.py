import dotenv

from simputils.config.enums import ConfigStoreType
from simputils.config.generic import BasicFileHandler
from simputils.config.models import ConfigStore


class DotEnvFileHandler(BasicFileHandler):

	CONFIG_TYPE: str = ConfigStoreType.DOT_ENV

	def process_file(self, file: str) -> ConfigStore | None:
		conf = self._prepare_conf(file)
		if conf is not None:

			# noinspection PyBroadException
			try:
				data = dotenv.dotenv_values(file)
				if not isinstance(data, dict):
					# MARK  Overlapping error and try/catch that should not catch this error
					raise Exception("JSON file format root element must be dict")

				return conf.config_apply(data)
			except:  # pragma: no cover
				pass

		return None  # pragma: no cover
