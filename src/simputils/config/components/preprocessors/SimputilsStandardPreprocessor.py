import re
from typing import Any

from simputils.config.generic import BasicPreprocessor


class SimputilsStandardPreprocessor(BasicPreprocessor):

	def run(
		self,
		k: str,
		v: Any,
		replace_pattern=r"[^0-9a-zA-Z_]+",
		replaced_with="_",
		*args,
		**kwargs
	) -> tuple[str, Any]:
		"""
		Standard Simputils Preprocessor

		* Turns keys to uppercase
		* Replaces all non-alphanumeric with underscores on keys (and replaces multiple underscores with one)

		:param replaced_with:
		:param replace_pattern:
		:param k:
		:param v:
		:return:
		"""
		k = re.sub(replace_pattern, replaced_with, k).upper()

		return k, v
