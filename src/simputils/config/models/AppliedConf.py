from dataclasses import dataclass
from typing import Any


@dataclass
class AppliedConf:
	"""
	ConfigStore's history record
	"""

	applied_keys: list = None
	type: str = None
	name: str = None
	source: str = None
	handler: Any = None
	ref: dict = None
