from argparse import ArgumentParser
from collections import OrderedDict
from enum import Enum
from typing import Annotated

from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.enums import ConfigStoreType
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore, AppliedConf, AnnotatedConfigData


class TestConfigStore:

	def test_initial_functionality(self):
		conf = ConfigStore({
			"test-init-value-1": "val 1",
			"test-init-value-2": "val 2",
			"test-init-value-3": "val 3",
		})
		assert 3 == len(conf)
		assert "val 2" == conf["test-init-value-2"]

		conf["test-init-new-value-4"] = 3.1415

		assert 4 == len(conf)

		del conf["test-init-value-3"]
		assert 3 == len(conf)

		conf.config_apply(ConfigStore({
			"test-inherit-value-1": "val inherit 1",
			"test-init-value-2": "replacing value",
			"test-inherit-value-2": "val inherit 2",
		}))

		assert 5 == len(conf)

		# [AppliedConf(applied_keys=[], type='single-value', name='test_initial_functionality:15', source='/home/ivan/development/py-simputils-config/tests/unit/TestConfigStore.py', handler=None, ref={'test-init-new-value-4': 3.1415}), AppliedConf(applied_keys=[], type='ConfigStore', name=None, source=None, handler=None, ref={'test-inherit-value-1': 'val inherit 1', 'test-init-value-2': 'replacing value', 'test-inherit-value-2': 'val inherit 2'})] = {'test-init-value-1': 'val 1', 'test-init-value-2': 'replacing value', 'test-init-new-value-4': 3.1415, 'test-inherit-value-1': 'val inherit 1', 'test-inherit-value-2': 'val inherit 2'}
		assert 3 == len(conf.applied_confs)

		applied_conf_ref = conf.applied_confs[0]
		assert isinstance(applied_conf_ref, AppliedConf)
		assert AppliedConf(
			applied_keys=[],
			type="dict",
			name=None,
			source=None,
			handler=None,
			ref={
				"test-init-value-1": "val 1",
				"test-init-value-2": "val 2",
				"test-init-value-3": "val 3",
			}
		), applied_conf_ref

		applied_conf_ref = conf.applied_confs[1]
		assert isinstance(applied_conf_ref, AppliedConf)
		assert "single-value" == applied_conf_ref.type
		assert 3.1415 == applied_conf_ref.ref["test-init-new-value-4"]

		applied_conf_ref = conf.applied_confs[2]
		assert isinstance(applied_conf_ref, AppliedConf)
		assert applied_conf_ref.applied_keys == ["test-inherit-value-1", "test-init-value-2", "test-inherit-value-2"]
		assert applied_conf_ref.type == ConfigStoreType.DICT
		assert OrderedDict(sorted(applied_conf_ref.ref.items())) == OrderedDict(sorted({
			"test-inherit-value-1": "val inherit 1",
			"test-init-value-2": "replacing value",
			"test-inherit-value-2": "val inherit 2"
		}.items()))

		conf.update({
			"new Updated KEY 1": "NUV 1"
		})

		assert len(conf) == 6

		assert conf["new Updated KEY 1"] == "NUV 1"

		conf += {
			"new Updated KEY 1": "Rewritten",
			"new Plus-Added KEY 1": "NPAV 1",
		}

		assert conf["new Updated KEY 1"] == "Rewritten"
		assert conf["new Plus-Added KEY 1"] == "NPAV 1"

		conf += ConfigStore({
			"FILTERED_IN_1": "FILTERED_IN_1",
			"FILTERED_IN_2": "FILTERED_IN_2",
			"FILTERED_IN_3": "FILTERED_IN_3",
		}, filter=["FILTERED_IN_1", "FILTERED_IN_3"])

		assert conf["FILTERED_IN_1"] == "FILTERED_IN_1"
		assert conf["FILTERED_IN_3"] == "FILTERED_IN_3"
		assert conf["FILTERED_IN_2"] is None

	def test_explicit_checks(self):
		conf = ConfigStore()

		assert not bool(conf), "Check if ConfigStore object is false when empty"

		conf["test-val"] = 11

		assert bool(conf), "Check if ConfigStore object is true when non-empty"

	def test_documentation_examples(self):
		conf = ConfigStore(
			{"VAL1": "My Val 1", "VAL2": True},
			name="My very special config",
			type="MY-type",
			source="knowhere",
		)
		first_applied: AppliedConf = conf.applied_confs[0]
		assert first_applied.applied_keys == ["VAL1", "VAL2"]

	def test_getting_with_defaults(self):

		conf = ConfigStore({"v1": 1, "v2": 2, "v3": None})

		assert conf.get("v1", "default") == 1
		assert conf.get("v2", "default") == 2
		assert conf.get("v3", "default") == "default"
		assert conf.get("v4", "default") == "default"

		conf = ConfigStore({"v1": 1, "v2": 2, "v3": None}, return_default_on_none=True)

		assert conf.get("v1", "default") == 1
		assert conf.get("v2", "default") == 2
		assert conf.get("v3", "default") == "default"
		assert conf.get("v4", "default") == "default"

		conf = ConfigStore({"v1": 1, "v2": 2, "v3": None}, return_default_on_none=False)

		assert conf.get("v1", "default") == 1
		assert conf.get("v2", "default") == 2
		assert conf.get("v3", "default") is None
		assert conf.get("v4", "default") == "default"

	def test_keys_replace(self):
		conf = ConfigStore(
			{"v1": 1, "v2": 2, "v3": None},
			preprocessor={"v1": "VAL1", "v3": "VAL3"}
		)

		assert "v1" not in conf
		assert "v3" not in conf
		assert "VAL1" in conf
		assert conf["VAL1"] == 1
		assert conf["VAL3"] is None

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
