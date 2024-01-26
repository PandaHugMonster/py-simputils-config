from enum import Enum


class ConfigStoreType(str, Enum):
	YAML = "YAML"
	DOT_ENV = "DotEnv"
	JSON = "JSON"
	ENV_VARS = "EnvVars"
	IO = "IO"
