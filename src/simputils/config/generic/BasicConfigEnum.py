from enum import Enum
from typing import get_args


class BasicConfigEnum(str, Enum):
	"""
	Abstract Enum for configs.

	Basically just str + enum with some additional features.

	After extending from it, can be easily used as an argument for defaults of `ConfigStore`
	"""

	@classmethod
	def defaults(cls) -> dict:
		res = {}
		annotations = getattr(cls, "__annotations__")
		for m in cls:
			default = None
			if annotations and (d := annotations.get(m.name)):
				try:
					_, annotated_config_data = get_args(d)
					default = annotated_config_data.data.get("default")
				except ValueError:  # pragma: no cover
					pass
			res[m.value] = default

		return res
