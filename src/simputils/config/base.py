from typing import Any, get_args


def simputils_pp(k: str, v: Any, replace_pattern=r"[^0-9a-zA-Z_]+", replaced_with="_"):
	"""
	Standard Simputils Preprocessor

	* Turns keys to uppercase
	* Replaces all non-alphanumeric with underscores on keys (and replaces multiple underscores with one)

	:param replaced_with:
	:param replace_pattern:
	:param k:
	:param v:
	:return:
	"""
	from simputils.config.components.preprocessors import SimputilsStandardPreprocessor

	func = SimputilsStandardPreprocessor()

	return func(k, v, replace_pattern, replaced_with)


def simputils_cast(k: str, v: Any):
	from simputils.config.components.preprocessors import SimputilsCastingPreprocessor

	func = SimputilsCastingPreprocessor()

	return func(k, v)


def simputils_pp_with_cast(k: str, v: Any, replace_pattern=r"[^0-9a-zA-Z_]+", replaced_with="_"):
	k, v = simputils_pp(k, v, replace_pattern, replaced_with)
	k, v = simputils_cast(k, v)
	# TODO  Not covered!
	return k, v


def get_enum_defaults(enum_class) -> dict:
	"""
	Extracts key-value pairs as dict, with values pre-filled
	with default values from corresponding `enum_class`.

	Any Enum is supported, not only those that inherited from `BasicConfigEnum`.

	:param enum_class:
	:return:
	"""
	res = {}
	for m in enum_class:
		default = None
		annotated_config_data = enum_class.get_annotation_for(m.value)
		if annotated_config_data:
			default = annotated_config_data.data.get("default")
		res[m.value] = default

	return res


def get_enum_annotation_for(enum_class, name: str):
	name = enum_class(name).name

	annotations = getattr(enum_class, "__annotations__")
	if annotations and (d := annotations.get(name)):
		try:
			_, annotated_config_data = get_args(d)
			return annotated_config_data
		except ValueError:  # pragma: no cover
			pass
	return None


def get_enum_all_annotations(enum_class):
	res = {}
	for m in enum_class:
		annotated_config_data = get_enum_annotation_for(enum_class, m)
		if annotated_config_data:
			res[m] = annotated_config_data
	return res
