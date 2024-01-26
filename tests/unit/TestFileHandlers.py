import os
import re

from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.components.handlers import DotEnvFileHandler, YamlFileHandler, JsonFileHandler
from simputils.config.models import ConfigStore


class TestFileHandlers:

	def test_files_load(self):
		conf = ConfigHub.aggregate(
			"tests/data/config-1.yml",
			"tests/data/config-2.yml",
			"tests/data/config-3.json",
			"tests/data/config-4.env",
			"tests/data/config-4.env",
			"tests/data/missing-file.env",
			os.environ,

			target=ConfigStore(
				preprocessor=simputils_pp,
				filter=lambda k, v: re.match(r"PARAM_[0-9]+", k)
			)
		)

		assert conf["PARAM_1"] == "first parameter"
		assert conf["PARAM_2"] == "two"
		assert conf["PARAM_3"] == "three"
		assert conf["PARAM_4"] == "ENV PARAM 4"
		assert conf["PARAM_5"] == "JSON 5"
		assert conf["PARAM_6"] == [1, 2, 3]

		assert conf.applied_from("PARAM_1").type == YamlFileHandler.CONFIG_TYPE
		assert conf.applied_from("PARAM_1").name == "config-1.yml"

		assert conf.applied_from("PARAM_2").type == YamlFileHandler.CONFIG_TYPE
		assert conf.applied_from("PARAM_2").name == "config-2.yml"

		assert conf.applied_from("PARAM_3").type == YamlFileHandler.CONFIG_TYPE
		assert conf.applied_from("PARAM_3").name == "config-2.yml"

		# print(conf.applied_from("PARAM_4"))
		assert conf.applied_from("PARAM_4").type == DotEnvFileHandler.CONFIG_TYPE
		assert conf.applied_from("PARAM_4").name == "config-4.env"

		assert conf.applied_from("PARAM_5").type == JsonFileHandler.CONFIG_TYPE
		assert conf.applied_from("PARAM_5").name == "config-3.json"

		assert conf.applied_from("PARAM_6").type == YamlFileHandler.CONFIG_TYPE
		assert conf.applied_from("PARAM_6").name == "config-1.yml"

		assert conf.applied_from("Hello World") is None

		# print(conf)

