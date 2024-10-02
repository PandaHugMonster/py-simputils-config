from simputils.config.generic import BasicConfigStore
from simputils.config.models import AppliedConf


class ConfigStore(BasicConfigStore):
	"""
	Major object containing the config itself
	"""

	@classmethod
	def applied_conf_class(cls):  # pragma: no cover
		return AppliedConf
