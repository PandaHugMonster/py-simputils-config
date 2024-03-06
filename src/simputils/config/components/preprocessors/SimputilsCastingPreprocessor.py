import re
from typing import Any

from simputils.config.generic import BasicPreprocessor


class SimputilsCastingPreprocessor(BasicPreprocessor):

	list_yes = ["yes", "y", "t", "true", "+", "enable", "enabled", "on"]
	list_no = ["no", "n", "f", "false", "-", "disable", "disabled", "off"]
	list_none = ["null", "none", "nil", ""]

	def run(
		self,
		k: str,
		v: Any,
		*args,
		**kwargs
	) -> tuple[str, Any]:

		if isinstance(v, str):
			# NOTE	Only strings are being processed
			value = v.lower()

			# NOTE	Binary Option Values
			sub_res = self._process_binary_option_values(k, value)
			if sub_res is not None:
				return sub_res

			# NOTE	Numbers
			sub_res = self._process_number_values(k, value)
			if sub_res is not None:
				return sub_res

		return k, v

	# noinspection PyMethodMayBeStatic
	def _process_number_values(self, key, value):
		res = None
		if re.match(r"^[+-]?[0-9.]+$", value) and value.count(".") == 1:
			# MARK  Fix the multiple dots check!
			res = (key, float(value))
		if re.match(r"^[+-]?[0-9]+$", value):
			res = (key, int(value))

		return res

	def _process_binary_option_values(self, key, value):
		res = None
		if value in self.list_yes:
			res = (key, True)
		if value in self.list_no:
			res = (key, False)
		if value in self.list_none:
			res = (key, None)

		return res
