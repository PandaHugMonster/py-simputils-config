from simputils.config.components.simpletons import NotExisting
from simputils.config.generic import BasicMergingStrategy


class MergingStrategyRecursive(BasicMergingStrategy):

	_merge_lists: bool = None

	def __init__(self, merge_lists: bool = False):
		self._merge_lists = merge_lists

	# noinspection PyUnusedLocal
	@classmethod
	def _none_check(cls, val_target, val_incoming):
		res = val_incoming is None
		return res

	# noinspection PyUnusedLocal
	@classmethod
	def _not_existing_check(cls, val_target, val_incoming):
		res = val_target is not None and isinstance(val_target, NotExisting)
		return res

	@classmethod
	def _primitive_check(cls, val_target, val_incoming):
		primitives = (int, float, bool, str)
		res = val_target is not None and val_incoming is not None and \
			(isinstance(val_target, primitives) or isinstance(val_incoming, primitives))
		return res

	@classmethod
	def _incompatible_check(cls, val_target, val_incoming):
		# NOTE  If the val_target class != val_incoming class and val_target is not derivative of val_incoming.
		check = isinstance(val_target, object) and isinstance(val_incoming, object) and \
			not isinstance(val_target, val_incoming.__class__)
		if check:
			return True

		check = (isinstance(val_target, (dict, object)) and not isinstance(val_incoming, (dict, object))) or \
			(not isinstance(val_target, (dict, object)) and isinstance(val_incoming, (dict, object)))
		if check:
			return True

		return False

	def merge(self, key, val_target, val_incoming):
		# NOTE  internally recursion happens
		main_args = (val_target, val_incoming)
		check = self._none_check(*main_args) or \
			self._not_existing_check(*main_args) or \
			self._primitive_check(*main_args) or \
			self._incompatible_check(*main_args)

		if check:
			# NOTE  uses incoming value if not-existing key, primitives or incompatible formats
			#       basically any inconsistency, then the whole value is used of val_incoming
			return val_incoming

		if isinstance(val_target, list) or isinstance(val_incoming, list):
			if self._merge_lists:
				return val_target + val_incoming

			return val_incoming

		if isinstance(val_target, dict) and isinstance(val_incoming, dict):
			return self._dictionaries_merge(*main_args)

		check = (isinstance(val_target, object) and isinstance(val_incoming, object)) or \
			(isinstance(val_target, dict) and isinstance(val_incoming, object)) or \
			(isinstance(val_target, object) and isinstance(val_incoming, dict))
		if check:
			return self._objects_merge(*main_args)

		# note  overrides the target value with the incoming one
		return val_incoming

	def _dictionaries_merge(self, val_target: dict, val_incoming: dict):
		for key, val_in in val_incoming.items():
			if key in val_target:
				val_target[key] = self.merge(key, val_target[key], val_in)
			else:
				val_target[key] = val_in

		return val_target

	def _objects_merge(self, val_target: object, val_incoming: object):
		for key, val_in in val_incoming.__dict__.items():
			if key in val_target.__dict__:
				sub_val = self.merge(key, val_target.__dict__[key], val_in)
				if sub_val is None:
					sub_val = val_target.__dict__[key]
				val_target.__dict__[key] = sub_val
			else:
				val_target.__dict__[key] = val_in

		return val_target
