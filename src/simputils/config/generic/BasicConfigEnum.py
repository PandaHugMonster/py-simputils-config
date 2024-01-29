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
		for m in cls:
			default = None
			annotated_config_data = cls.get_annotation_for(m.value)
			if annotated_config_data:
				default = annotated_config_data.data.get("default")
			res[m.value] = default

		return res

	@classmethod
	def get_annotation_for(cls, name: "BasicConfigEnum | str"):
		name = cls(name).name

		annotations = getattr(cls, "__annotations__")
		if annotations and (d := annotations.get(name)):
			try:
				_, annotated_config_data = get_args(d)
				return annotated_config_data
			except ValueError:  # pragma: no cover
				pass
		return None

	@classmethod
	def get_all_annotations(cls):
		res = {}
		for m in cls:
			annotated_config_data = cls.get_annotation_for(m)
			if annotated_config_data:
				res[m] = annotated_config_data
		return res
