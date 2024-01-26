import inspect
from typing import Any
from typing import Callable

from simputils.config.models import AppliedConf


class ConfigStore(dict):

	_name: str = None
	_source: str = None
	_type: str = None
	_applied_confs: list = None
	_storage: dict = None
	_preprocessor: "dict | Callable[[Any, ], tuple[Any, Any]]" = None
	_filter: list | Callable = None
	_handler=None
	_return_default_on_none: bool = True

	@property
	def name(self) -> str:
		return self._name

	@property
	def source(self) -> str:
		return self._source

	@property
	def type(self) -> str:
		return self._type

	@property
	def handler(self) -> Callable:
		return self._handler

	@property
	def applied_confs(self) -> list:
		return self._applied_confs

	@property
	def return_default_on_none(self) -> bool:  # pragma: no cover
		return self._return_default_on_none

	def __init__(
		self,
		values: "dict | ConfigStore" = None,
		name: str = None,
		source: str = None,
		type: str = None,
		preprocessor: Callable = None,
		filter: list | Callable = None,
		handler=None,
		return_default_on_none: bool = True,
	):
		self._applied_confs = []
		self._storage = {}
		self._type = type
		self._source = source
		self._name = name
		self._preprocessor = preprocessor
		self._filter = filter
		self._handler = handler
		self._return_default_on_none = return_default_on_none

		if not self._type:
			self._type = self.__class__.__name__

		self.config_apply(values, name, source, type)

	def _key_replace_callback(self, mapped_keys: dict, key: str, val: Any):
		if key in mapped_keys:
			# NOTE  Replacing old key with a new key
			return mapped_keys[key], val
		# NOTE  Returning key and val intact
		return key, val

	def config_apply(
		self,
		config: "dict | ConfigStore",
		name: str = None,
		source: str = None,
		type: str = None,
		handler=None,
	):
		if not config:  # pragma: no cover
			return self
		if isinstance(config, ConfigStore):
			if not name:
				name = config.name
			if not source:
				source = config.source
			if not type:
				type = config.type
			if not handler:
				handler = config.handler

		if type is None:
			type = "dict"

		preprocessor = self._preprocessor

		if preprocessor:
			if isinstance(preprocessor, dict):
				# MARK  Maybe refactor this to avoid using lambda due to performance limitations
				_preprocessor_data = preprocessor
				preprocessor = lambda k, v: self._key_replace_callback(_preprocessor_data, k, v)

		applied_keys = []
		for key, val in config.items():
			if preprocessor is not None:
				key, val = preprocessor(key, val)
			if self._filter:
				filter = self._filter
				if (isinstance(filter, (list, tuple)) and (key in filter)) or (callable(filter) and filter(key, val)):
					applied_keys.append(key)
					self._storage[key] = val
			else:
				applied_keys.append(key)
				self._storage[key] = val

		self._applied_confs.append(AppliedConf(
			applied_keys=applied_keys,
			type=type,
			name=name,
			source=source,
			ref=config,
			handler=handler,
		))
		return self

	def __setitem__(self, key, value):
		frame_context = inspect.stack()[1][0]
		frame_info = inspect.getframeinfo(frame_context)

		self.config_apply(
			{key: value},
			f"{frame_info.function}:{frame_info.lineno}",
			frame_info.filename,
			"single-value"
		)

	def applied_from(self, key: str, include_unprocessed_keys: bool = False) -> dict:
		for record in reversed(self._applied_confs):
			record: AppliedConf
			if key in record.applied_keys:
				return record
			if include_unprocessed_keys and key in record.ref:  # pragma: no cover
				return record

		return None

	def __getitem__(self, key):  # pragma: no cover
		return self._storage.get(key)

	def __add__(self, other):  # pragma: no cover
		return self.config_apply(other)

	def __repr__(self):  # pragma: no cover
		return repr(self._storage)

	def __len__(self):  # pragma: no cover
		return len(self._storage)

	def __delitem__(self, key):  # pragma: no cover
		del self._storage[key]

	def get(self, key, default: Any = None):
		res = self._storage.get(key)
		if self._return_default_on_none:
			if res is None:
				return default
		else:
			if key not in self:
				return default
		return res

	def clear(self):  # pragma: no cover
		# TODO  Add logging that it's not allowed
		pass

	def copy(self):  # pragma: no cover
		return self._storage.copy()

	def update(self, __m, **kwargs):
		self.config_apply(__m)

	def keys(self):  # pragma: no cover
		return self._storage.keys()

	def values(self):  # pragma: no cover
		return self._storage.values()

	def items(self):  # pragma: no cover
		return self._storage.items()

	def pop(self, __key):  # pragma: no cover
		# TODO  Add logging that it's not allowed
		pass

	def popitem(self):  # pragma: no cover
		# TODO  Add logging that it's not allowed
		pass

	def __cmp__(self, other):  # pragma: no cover
		return self._storage == other

	def __contains__(self, item):  # pragma: no cover
		return item in self._storage

	def __iter__(self):  # pragma: no cover
		return iter(self._storage)

	def __str__(self):  # pragma: no cover
		return str(self._storage)
