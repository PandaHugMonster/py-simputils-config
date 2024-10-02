from simputils.config.components.simpletons import NotExisting
from simputils.config.generic import BasicMergingStrategy


class MergingStrategyFlat(BasicMergingStrategy):

	def merge(self, key, val_target, val_incoming, none_considered_empty: bool = False):
		if not isinstance(val_target, NotExisting) and none_considered_empty and val_incoming is None:
			return val_target
		return val_incoming
