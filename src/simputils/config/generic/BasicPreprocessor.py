from abc import ABCMeta
from typing import Any


class BasicPreprocessor(metaclass=ABCMeta):

	def run(self, k: str, v: Any, *args, **kwargs) -> tuple[str, Any]:  # pragma: no cover
		pass

	def __call__(self, k: str, v: Any, *args, **kwargs):
		return self.run(k, v, *args, **kwargs)
