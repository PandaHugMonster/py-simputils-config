from simputils.config.generic import BasicMergingStrategy


class FlatMergingStrategy(BasicMergingStrategy):

	def merge(self, key, val_target, val_incoming):
		return val_incoming
