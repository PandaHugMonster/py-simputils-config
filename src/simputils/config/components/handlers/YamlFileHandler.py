import yaml

from simputils.config.enums import ConfigStoreType
from simputils.config.generic import BasicFileHandler
from simputils.config.models import ConfigStore


class YamlFileHandler(BasicFileHandler):

	CONFIG_TYPE: str = ConfigStoreType.YAML

	def process_file(self, file: str) -> ConfigStore | None:
		# NOTE  For some weird reason PyYAML parsing json successfully.
		#       It is unreasonable architecturally, so JSONs are explicitly excluded

		conf = self._prepare_conf(file)
		if conf is not None:

			# noinspection PyBroadException
			try:
				with open(file, "r") as fd:
					return conf.config_apply(
						yaml.safe_load(fd),
					)
			except:
				pass

		return None
