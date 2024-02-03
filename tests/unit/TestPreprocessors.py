from simputils.config.base import simputils_pp, simputils_cast


class TestPreprocessors:

	def test_standard_preprocessor(self):
		to_check = {
			"my key 1": "MY_KEY_1",
			"my-key-2": "MY_KEY_2",
			"MY_KEY_3": "MY_KEY_3",
			"my.KEy-4": "MY_KEY_4",
			"my    KEy-----5": "MY_KEY_5",
		}
		for orig_k, exp_k in to_check.items():
			k, _ = simputils_pp(orig_k, None)
			assert exp_k == k

	def test_casting_preprocessor(self):
		to_check = (
			("My value 1", str, "My value 1"),
			("3.14.15", str, "3.14.15"),

			("0", int, 0),
			("123", int, 123),
			("-15", int, -15),
			("+15", int, 15),

			("123.0", float, 123.0),
			("0.0", float, 0.0),
			("-3.1415", float, -3.1415),
			("+3.1415", float, 3.1415),

			("t", bool, True),
			("T", bool, True),
			("f", bool, False),
			("F", bool, False),
			("yes", bool, True),
			("NO", bool, False),
			("enabled", bool, True),
			("DiSaBlEd", bool, False),
			("true", bool, True),
			("False", bool, False),
			("-", bool, False),
			("+", bool, True),

			("nul", str, "nul"),
			("null", None, None),
			("None", None, None),
			("NOne", None, None),
			("nil", None, None),
			("nIL", None, None),
		)
		for group in to_check:
			orig_v, exp_type, exp_value = group
			_, v = simputils_cast("gg", orig_v)
			if exp_type is not None:
				assert isinstance(v, exp_type) and v == exp_value, f"error \"{v}\" of {exp_value}"
			else:
				assert v is exp_value, f"error \"{v}\" of {exp_value}"
