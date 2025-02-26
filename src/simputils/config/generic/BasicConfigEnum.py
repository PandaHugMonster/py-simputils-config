from enum import Enum

from simputils.config.base import get_enum_defaults, get_enum_annotation_for, get_enum_all_annotations
from simputils.config.types import SourceType, PreProcessorType, FilterType, HandlerType


class BasicConfigEnum(str, Enum):
	"""
	Abstract Enum for configs.

	Basically just str + enum with some additional features.

	After extending from it, can be easily used as an argument for defaults of `ConfigStore`
	"""

	@classmethod
	def get_strict_keys(cls):
		return False

	@classmethod
	def get_config_name(cls) -> str | None:
		return None

	@classmethod
	def defaults(cls) -> dict:
		return get_enum_defaults(cls)

	@classmethod
	def get_annotation_for(cls, name: "BasicConfigEnum | str"):
		return get_enum_annotation_for(cls, name)

	@classmethod
	def get_all_annotations(cls):
		return get_enum_all_annotations(cls)

	@classmethod
	def target_config(
		cls,
		name: str = None,
		source: SourceType = None,
		type: str = None,
		preprocessor: PreProcessorType = None,
		filter: FilterType = None,
		handler: HandlerType = None,
		return_default_on_none: bool = True,
		none_considered_empty: bool = False,
		strict_keys: bool = False,
		target_class=None,
	):
		if target_class is None:
			# TODO  Yes, ugly, but don't want to waste too much time
			#       on resolving the order at this point.
			from simputils.config.models import ConfigStore
			target_class = ConfigStore

		return target_class(
			cls,
			name=name,
			source=source,
			type=type,
			preprocessor=preprocessor,
			filter=filter,
			handler=handler,
			return_default_on_none=return_default_on_none,
			none_considered_empty=none_considered_empty,
			strict_keys=strict_keys,
			enum=cls,
		)

	@classmethod
	def names(cls):
		return list(map(lambda name: name.value, cls))

	@classmethod
	def preprocess(cls, k, v):
		try:
			annotation = cls.get_annotation_for(k)
			if annotation:
				data = annotation.data
				preprocessor = data.get("preprocessor")
				if preprocessor:
					return preprocessor(k, v)
		except ValueError:
			pass

		return k, v
