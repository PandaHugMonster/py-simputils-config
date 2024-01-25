import re
from typing import Callable, Any

from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigStore


def config_from_dict(
	config: dict | BasicConfigStore,
	name: str = None,
	source: str = None,
	type: str = None,
	target: BasicConfigStore = None
) -> BasicConfigStore:
	return ConfigHub.config_from_dict(config, name, source, type, target)


def config_from_file(
	file: str,
	name: str = None,
	source: str = None,
	type: str = None,
	target: BasicConfigStore = None
) -> BasicConfigStore:
	return ConfigHub.config_from_file(file, name, source, type, target)


def simputils_pp(k: str, v: Any, replace_pattern=r"[^0-9a-zA-Z]+", replaced_with="_"):
	"""
	Standard Simputils Preprocessor

	* Turns keys to uppercase
	* Replaces all non-alphanumeric with underscores on keys

	:param replaced_with:
	:param replace_pattern:
	:param k:
	:param v:
	:return:
	"""
	k = re.sub(replace_pattern, replaced_with, k).upper()

	return k, v
