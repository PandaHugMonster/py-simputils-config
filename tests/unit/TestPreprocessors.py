import pytest

from simputils.config.base import simputils_pp_with_cast, simputils_pp, simputils_cast
from simputils.config.models import ConfigStore

_params_fixture_names = "key_orig,key_exp,val_orig,val_exp,val_type"
_params_fixture_values = [
	# "key_orig,key_exp,val_orig,val_exp,val_type"
	(
		"my key 1", "MY_KEY_1",
		"My value 1", "My value 1", str
	),
	(
		"my-key-2", "MY_KEY_2",
		"3.14.15", "3.14.15", str
	),

	(
		"MY_KEY_3", "MY_KEY_3",
		"0", 0, int
	),
	(
		"my.KEy-4", "MY_KEY_4",
		"123", 123, int
	),
	(
		"my    KEy-----5", "MY_KEY_5",
		"-15", -15, int
	),
	("K", "K", "+15", 15, int),

	("K", "K", "123.0", 123.0, float),
	("K", "K", "0.0", 0.0, float),
	("K", "K", "-3.1415", -3.1415, float),
	("K", "K", "+3.1415", 3.1415, float),

	("K", "K", "t", True, bool),
	("K", "K", "T", True, bool),
	("K", "K", "f", False, bool),
	("K", "K", "F", False, bool),
	("K", "K", "yes", True, bool),
	("K", "K", "NO", False, bool),
	("K", "K", "enabled", True, bool),
	("K", "K", "DiSaBlEd", False, bool),
	("K", "K", "true", True, bool),
	("K", "K", "False", False, bool),
	("K", "K", "-", False, bool),
	("K", "K", "+", True, bool),

	("K", "K", "nul", "nul", str),
	("K", "K", "null", None, None),
	("K", "K", "None", None, None),
	("K", "K", "NOne", None, None),
	("K", "K", "nil", None, None),
	("K", "K", "nIL", None, None),
]


class TestPreprocessors:

	@pytest.mark.parametrize(_params_fixture_names, _params_fixture_values)
	def test_both_simputils_processor(self, key_orig, key_exp, val_orig, val_exp, val_type):
		k, v = simputils_pp_with_cast(key_orig, val_orig)

		assert key_exp == k

		if val_type is not None:
			assert isinstance(v, val_type) and v == val_exp, f"error \"{v}\" of {val_exp}"
		else:
			assert v is val_exp, f"error \"{v}\" of {val_exp}"

	def test_list_for_preprocessor(self):
		conf = ConfigStore(
			{
				"my key #1": "My first key",
				"my key 2": "0.0",
				"my KEy 3": "",
			},
			preprocessor=[
				simputils_pp,
				simputils_cast,
			],
		)

		assert conf

		assert "MY_KEY_1" in conf
		assert isinstance(conf["MY_KEY_1"], str)
		assert "MY_KEY_2" in conf
		assert isinstance(conf["MY_KEY_2"], float)
		assert "MY_KEY_3" in conf
		assert conf["MY_KEY_3"] is None
