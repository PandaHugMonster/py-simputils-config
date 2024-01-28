from dataclasses import dataclass
from typing import Any

from simputils.config.generic import BasicAppliedConf
from simputils.config.types import SourceType, HandlerType


@dataclass
class AppliedConf(BasicAppliedConf):
	"""
	ConfigStore's history record
	"""

	applied_keys: list[str] = None
	type: str = None
	name: str = None
	source: SourceType = None
	handler: HandlerType = None
	ref: Any = None
