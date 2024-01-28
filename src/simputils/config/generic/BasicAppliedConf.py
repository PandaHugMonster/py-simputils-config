from dataclasses import dataclass
from typing import Any

from simputils.config.types import SourceType, HandlerType


@dataclass
class BasicAppliedConf:
	applied_keys: list[str] = None
	type: str = None
	name: str = None
	source: SourceType = None
	handler: HandlerType = None
	ref: Any = None
