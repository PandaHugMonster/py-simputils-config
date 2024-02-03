import re
from typing import Any

from simputils.config.generic import BasicPreprocessor


class SimputilsCastingPreprocessor(BasicPreprocessor):

	list_yes = ['enabled', 'yes', 't', 'true', 'y', '+', 'enable']
	list_no = ['disabled', 'no', 'f', 'false', 'n', '-', 'disable']
	list_none = ['null', 'none', 'nil']

	def run(
		self,
		k: str,
		v: Any,
		*args,
		**kwargs
	) -> tuple[str, Any]:

		if isinstance(v, str):
			# Only strings are being processed
			tmp = v.lower()
			if tmp in self.list_yes:
				return k, True
			if tmp in self.list_no:
				return k, False
			if tmp in self.list_none:
				return k, None
			if re.match(r"^[+-]?[0-9.]+$", v) and v.count(".") == 1:
				# MARK  Fix the multiple dots check!
				return k, float(v)
			if re.match(r"^[+-]?[0-9]+$", v):
				return k, int(v)

		return k, v
