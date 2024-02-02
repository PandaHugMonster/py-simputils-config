from enum import Enum

from simputils.config.base import get_enum_defaults, get_enum_annotation_for, get_enum_all_annotations


class BasicConfigEnum(str, Enum):
	"""
	Abstract Enum for configs.

	Basically just str + enum with some additional features.

	After extending from it, can be easily used as an argument for defaults of `ConfigStore`
	"""

	@classmethod
	def defaults(cls) -> dict:
		return get_enum_defaults(cls)

	@classmethod
	def get_annotation_for(cls, name: "BasicConfigEnum | str"):
		return get_enum_annotation_for(cls, name)

	@classmethod
	def get_all_annotations(cls):
		return get_enum_all_annotations(cls)
