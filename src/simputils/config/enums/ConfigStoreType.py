from enum import Enum


class ConfigStoreType(str, Enum):
	"""
	Generic type names for ConfigStore
	"""

	YAML = "YAML"
	DOT_ENV = "DotEnv"
	JSON = "JSON"
	ENV_VARS = "EnvVars"
	IO = "IO"
	SINGLE_VALUE = "single-value"
	DICT = "dict"
	ARGPARSER_NAMESPACE = "argparser"
