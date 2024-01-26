from collections import OrderedDict

from simputils.config.models import ConfigStore, AppliedConf


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
		assert applied_conf_ref.type == "ConfigStore"
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
