import os
from argparse import ArgumentParser
from enum import Enum
from typing import Annotated

import pytest

from simputils.config.base import simputils_pp, simputils_pp_with_cast
from simputils.config.components import ConfigHub
from simputils.config.enums import ConfigStoreType
from simputils.config.exceptions import StrictKeysEnabled
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore, AnnotatedConfigData


class TestConfigStoreThroughAggregate:

	def test_aggregate_dict(self):
		conf = ConfigHub.aggregate({"test1": "test1", "test2": "test2"})

		assert conf["test1"] == "test1"
		assert conf["test2"] == "test2"

	def test_dict_keys_for_filter(self):
		defaults = {
			"key-1": "val 1",
			"key-2": "val 2",
			"key-3": "val 3",
		}

		conf = ConfigHub.aggregate(
			defaults,
			{"key-2": "new val 2", "test": "test"},
			target=ConfigStore(
				preprocessor=simputils_pp,
				filter=defaults.keys(),
			)
		)

		assert len(conf) == 3
		assert conf["KEY_1"] == "val 1"
		assert conf["KEY_2"] == "new val 2"
		assert conf["KEY_3"] == "val 3"
		assert not conf["TEST"]

	def test_enum_proper_support(self):
		class MyEnum(str, Enum):
			MY_1 = "key-1"
			MY_2 = "key-2"
			MY_3 = "key-3"

		defaults = {
			MyEnum.MY_1: "val 1",
			MyEnum.MY_2: "val 2",
			# MyEnum.MY_3: "val 3",
		}

		conf = ConfigHub.aggregate(
			defaults,
			{MyEnum.MY_2: "new val 2", "test": "test"},
			target=ConfigStore(
				preprocessor=simputils_pp,
				filter=defaults.keys(),
			)
		)

		conf[MyEnum.MY_3] = "EQ"

		assert conf["KEY_1"]
		assert conf["KEY_1"] == "val 1"

		assert conf[MyEnum.MY_1]
		assert conf[MyEnum.MY_1] == "val 1"

		assert conf.get("KEY_1")
		assert conf.get("KEY_1") == "val 1"

		assert conf.get(MyEnum.MY_1)
		assert conf.get(MyEnum.MY_1) == "val 1"

		#

		assert conf["KEY_2"]
		assert conf["KEY_2"] == "new val 2"

		assert conf[MyEnum.MY_2]
		assert conf[MyEnum.MY_2] == "new val 2"

		assert conf.get("KEY_2")
		assert conf.get("KEY_2") == "new val 2"

		assert conf.get(MyEnum.MY_2)
		assert conf.get(MyEnum.MY_2) == "new val 2"

	def test_arg_parser_namespace(self):
		args_parser = ArgumentParser()
		args_parser.add_argument("--name", "-n", default="MyName")
		args_parser.add_argument("--age", default="33")

		args = args_parser.parse_args(["-n", "PandaHugMonster"])

		conf = ConfigHub.aggregate(
			args,
			target=ConfigStore(
				preprocessor=simputils_pp,
			)
		)

		assert conf["NAME"] == "PandaHugMonster"
		assert int(conf["AGE"]) == 33

	def test_arg_parser_check_applied_confs_history(self):
		parser = ArgumentParser()
		parser.add_argument("-n", "--name", type=str, required=True)
		parser.add_argument("-s", "--surname", type=str)
		parser.add_argument("-a", "--age", type=int)

		args = parser.parse_args(["-n", "PandaHugMonster"])

		config = ConfigHub.aggregate(
			{
				"name": "My Name",
			},
			args,
			os.environ,
		)
		applied_conf_dict = config.applied_confs[0]
		assert applied_conf_dict.type == ConfigStoreType.DICT

		applied_conf_args = config.applied_confs[1]
		assert applied_conf_args.type == ConfigStoreType.ARGPARSER_NAMESPACE

		applied_conf_env_vars = config.applied_confs[2]
		assert applied_conf_env_vars.type == ConfigStoreType.ENV_VARS

	def test_arg_parser_none_considered_empty(self):
		parser = ArgumentParser()
		parser.add_argument("-n", "--name", type=str, required=True)
		parser.add_argument("-s", "--surname", type=str)
		parser.add_argument("-a", "--age", type=int)

		args = parser.parse_args(["-n", "PandaHugMonster"])

		config = ConfigHub.aggregate(
			{
				"name": "My Name",
				"surname": "test",
				"age": 68
			},
			args,
			target=ConfigStore(
				none_considered_empty=True
			)
		)

		assert config["age"] == 68

	def test_annotated_config_data(self):
		class MyEnum(BasicConfigEnum):
			MY_E_KEY_1 = "my-e-key-1"

			MY_E_KEY_2: Annotated[str, AnnotatedConfigData(
				default=3.1415
			)] = "my-e-key-2"

			MY_E_KEY_3 = "my-e-key-3"
			MY_E_KEY_4: Annotated[str, AnnotatedConfigData(
				default="GOO GOO"
			)] = "my-e-key-4"
			MY_E_KEY_5 = "my-e-key-5"

		conf = ConfigHub.aggregate(
			{"MY_E_KEY_1": "gg", "TEST_1": "another val ", "test 2": "test", "my-e-key-4": "TOOT TOOT"},
			target=ConfigStore(
				MyEnum.defaults(),
				preprocessor=simputils_pp,
				filter=True
			),
		)

		assert conf[MyEnum.MY_E_KEY_1] == "gg"
		assert conf[MyEnum.MY_E_KEY_2] == 3.1415
		assert conf[MyEnum.MY_E_KEY_3] is None
		assert conf[MyEnum.MY_E_KEY_4] == "TOOT TOOT"

		conf = ConfigHub.aggregate(
			{"MY_E_KEY_1": "gg", "TEST_1": "another val ", "test 2": "test", "my-e-key-4": "TOOT TOOT"},
			target=ConfigStore(
				MyEnum.defaults(),
				preprocessor=simputils_pp,
				filter=[]
			),
		)

		assert conf

		conf = ConfigHub.aggregate(
			{"MY_E_KEY_1": "gg", "TEST_1": "another val ", "test 2": "test", "my-e-key-4": "TOOT TOOT"},
			target=ConfigStore(
				MyEnum.defaults(),
				preprocessor=simputils_pp,
				filter=False
			),
		)

		assert conf

	def test_enum_default_filter_out_unknown(self):
		class MyEnum(BasicConfigEnum):
			MY_E_KEY_1 = "my-e-key-1"

			MY_E_KEY_2: Annotated[str, AnnotatedConfigData(
				default=3.1415
			)] = "my-e-key-2"

			MY_E_KEY_3 = "my-e-key-3"
			MY_E_KEY_4 = "my-e-key-4"
			MY_E_KEY_5 = "my-e-key-5"

			# Some of them used in `app-conf.yml`
			MY_FIRST_VAL = "val-1"
			MY_SECOND_VAL = "VAL_2"

		conf = ConfigHub.aggregate(
			"tests/data/config-1.yml",

			target=ConfigStore(
				MyEnum.defaults(),
				preprocessor=simputils_pp,
				filter=MyEnum.defaults().keys()
			),
		)

		assert conf
		assert conf["MY_E_KEY_1"] is None
		assert conf["MY_E_KEY_2"] == 3.1415
		assert conf["VAL_1"] == "My conf value 1"
		assert conf["VAL_2"] == "My conf value 2"
		assert conf["VAL_3"] is None
		assert conf["PARAM_1"] is None

		conf = ConfigHub.aggregate(
			"tests/data/config-1.yml",

			target=ConfigStore(
				MyEnum.defaults(),
				preprocessor=simputils_pp,
				filter=True
			),
		)

		assert conf
		assert conf["MY_E_KEY_1"] is None
		assert conf["MY_E_KEY_2"] == 3.1415
		assert conf["VAL_1"] == "My conf value 1"
		assert conf["VAL_2"] == "My conf value 2"
		assert conf["VAL_3"] is None
		assert conf["PARAM_1"] is None

	def test_enum_annotations(self):
		class MyEnum(BasicConfigEnum):
			MY_E_KEY_1 = "my-e-key-1"

			MY_E_KEY_2: Annotated[str, AnnotatedConfigData(
				default=3.1415
			)] = "my-e-key-2"

			MY_E_KEY_3 = "my-e-key-3"
			MY_E_KEY_4 = "my-e-key-4"
			MY_E_KEY_5 = "my-e-key-5"

			# Some of them used in `app-conf.yml`
			MY_FIRST_VAL = "val-1"
			MY_SECOND_VAL = "VAL_2"

		conf = ConfigHub.aggregate(
			"tests/data/config-1.yml",

			target=ConfigStore(
				MyEnum.defaults(),
				preprocessor=simputils_pp,
				filter=True
			),
		)

		annotations = MyEnum.get_all_annotations()

		assert conf
		assert len(annotations) == 1
		assert isinstance(annotations[MyEnum.MY_E_KEY_2], AnnotatedConfigData)
		assert annotations[MyEnum.MY_E_KEY_2].data["default"] == 3.1415

	def test_raw_enum_class_usage_single(self):
		class MyEnum(BasicConfigEnum):
			MY_E_KEY_1 = "my-e-key-1"

			MY_E_KEY_2: Annotated[str, AnnotatedConfigData(
				default=3.1415
			)] = "my-e-key-2"

			MY_E_KEY_3 = "my-e-key-3"
			MY_E_KEY_4 = "my-e-key-4"
			MY_E_KEY_5 = "my-e-key-5"

			# Some of them used in `app-conf.yml`
			MY_FIRST_VAL = "val-1"
			MY_SECOND_VAL = "VAL_2"

		conf = ConfigHub.aggregate(
			"tests/data/config-1.yml",

			target=ConfigStore(
				MyEnum,

				preprocessor=simputils_pp,
				filter=True
			),
		)

		annotations = MyEnum.get_all_annotations()

		assert conf
		assert len(conf) == 7
		assert conf[MyEnum.MY_E_KEY_2] == 3.1415
		assert conf[MyEnum.MY_FIRST_VAL] == "My conf value 1"

	def test_raw_enum_class_usage_multiple(self):
		class MyEnum1(BasicConfigEnum):
			MY_E_KEY_1 = "my-e-key-1"

			MY_E_KEY_2: Annotated[str, AnnotatedConfigData(
				default=3.1415
			)] = "my-e-key-2"

		class MyEnum2(BasicConfigEnum):
			MY_E_KEY_3 = "my-e-key-3"
			MY_E_KEY_4 = "my-e-key-4"
			MY_E_KEY_5 = "my-e-key-5"

			# Some of them used in `app-conf.yml`
			MY_FIRST_VAL = "val-1"
			MY_SECOND_VAL = "VAL_2"

		conf = ConfigHub.aggregate(
			"tests/data/config-1.yml",

			target=ConfigStore(

				MyEnum1.target_config() + MyEnum2.target_config(),

				preprocessor=simputils_pp,
				filter=True
			),
		)

		assert conf
		assert len(conf) == 7
		assert conf[MyEnum1.MY_E_KEY_2] == 3.1415
		assert conf[MyEnum2.MY_FIRST_VAL] == "My conf value 1"

	def test_enum_type_casting(self):
		class MyEnum(BasicConfigEnum):
			MY_E_KEY_1: Annotated[str, AnnotatedConfigData(
				default=True,
				type=float,
			)] = "my-e-key-1"

			MY_E_KEY_2: Annotated[str, AnnotatedConfigData(
				default=False,
				type=float,
			)] = "my-e-key-2"

		conf = ConfigHub.aggregate(
			"tests/data/config-1.yml",

			target=ConfigStore(
				MyEnum,

				preprocessor=simputils_pp,
				filter=True
			),
		)

		assert conf
		assert len(conf) == 2
		assert isinstance(conf[MyEnum.MY_E_KEY_1], float)
		assert isinstance(conf[MyEnum.MY_E_KEY_2], float)
		assert conf[MyEnum.MY_E_KEY_1] == 1
		assert conf[MyEnum.MY_E_KEY_2] == 0

	def test_strict_keys(self):
		class MyEnum(BasicConfigEnum):
			VAL_1 = "VAL_1"
			VAL_2 = "VAL_2"
			VAL_3 = "VAL_3"
			VAL_4 = "VAL_4"
			VAL_5 = "VAL_5"

		conf = ConfigHub.aggregate(
			{"val-1": "First value", "val-2": 12, "val-3": "f"},
			target=ConfigStore(
				MyEnum,
				filter=True,
				preprocessor=simputils_pp_with_cast,
				strict_keys=True
			)
		)
		with pytest.raises(StrictKeysEnabled) as exc_i:
			conf.update({"test": "test1"})

		with pytest.raises(StrictKeysEnabled) as exc_i:
			conf["test"] = "test2"

		with pytest.raises(StrictKeysEnabled) as exc_i:
			g = conf["test"]

		with pytest.raises(StrictKeysEnabled) as exc_i:
			g = conf.get("test")
