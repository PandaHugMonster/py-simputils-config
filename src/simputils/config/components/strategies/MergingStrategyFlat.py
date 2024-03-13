from simputils.config.generic import BasicMergingStrategy


class MergingStrategyFlat(BasicMergingStrategy):

	def merge(self, key, val_target, val_incoming):
		return val_incoming
