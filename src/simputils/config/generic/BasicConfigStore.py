import inspect
from abc import ABCMeta
from typing import Any
from typing import Callable


class BasicConfigStore(dict, metaclass=ABCMeta):

	_name: str = None
	_source: str = None
	_type: str = None
	_applied_confs: list = None
	_storage: dict = None
	_preprocessor: "Callable[[Any, ], tuple[Any, Any]]" = None

	@property
	def name(self):
		return self._name

	@property
	def source(self):
		return self._source

	@property
	def type(self):
		return self._type

	@property
	def applied_confs(self):
		return self._applied_confs

	@classmethod
	def default_preprocessor(cls, key: Any, value: Any):
		return key, value

	def __init__(
		self,
		values: "dict | BasicConfigStore" = None,
		name: str = None,
		source: str = None,
		type: str = None,
		preprocessor: Callable = None
	):
		self._applied_confs = []
		self._storage = {}
		self._type = type
		self._source = source
		self._name = name
		self._preprocessor = preprocessor
		if not self._preprocessor:
			self._preprocessor = self.default_preprocessor

		if not self._type:
			self._type = self.__class__.__name__

		self.config_apply(values, name, source, type)

	def config_apply(
		self,
		config: "dict | BasicConfigStore",
		name: str = None,
		source: str = None,
		type: str = None
	):
		if not config:
			return self
		if isinstance(config, BasicConfigStore):
			if not name:
				name = config.name
			if not source:
				source = config.source
			if not type:
				type = config.type

		if type is None:
			type = "dict"

		for key, val in config.items():
			if self._preprocessor:
				preprocessor = self._preprocessor
				key, val = preprocessor(key, val)
			self._storage[key] = val

		self._applied_confs.append({
			"ref": config,
			"type": type,
			"name": name,
			"source": source,
		})
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

	def __getitem__(self, key):
		return self._storage.get(key)

	def __getattr__(self, key):
		return self._storage.get(key)

	def __add__(self, other):
		return self.config_apply(other)

	def __repr__(self):
		return repr(self._storage)

	def __len__(self):
		return len(self._storage)

	def __delitem__(self, key):
		del self._storage[key]

	def clear(self):
		# TODO  Add logging that it's not allowed
		pass

	def copy(self):
		return self._storage.copy()

	def update(self, __m, **kwargs):
		self.config_apply(__m)

	def keys(self):
		return self._storage.keys()

	def values(self):
		return self._storage.values()

	def items(self):
		return self._storage.items()

	def pop(self, __key):
		# TODO  Add logging that it's not allowed
		pass

	def popitem(self):
		# TODO  Add logging that it's not allowed
		pass

	def __cmp__(self, other):
		return self._storage == other

	def __contains__(self, item):
		return item in self._storage

	def __iter__(self):
		return iter(self._storage)

	def __str__(self):
		return str(self._storage)
