import inspect
from typing import Any
from typing import Callable

from simputils.config.enums import ConfigStoreType
from simputils.config.exceptions import NotPermitted
from simputils.config.models import AppliedConf


class ConfigStore(dict):
	"""
	Major object containing the config itself
	"""

	_name: str = None
	_source: str = None
	_type: str = None
	_applied_confs: list = None
	_storage: dict = None
	_preprocessor: "dict | Callable[[Any, ], tuple[Any, Any]]" = None
	_filter: list | Callable = None
	_handler = None
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
		"""
		If set to True and `get()` method is used with `default` param supplied,
		then `default` value will be returned on "non-existing" and "None" values

		If set to False and `get()` method is used with `default` param supplied,
		then `default` value will be returned ONLY on "non-existing", but None values will not be affected

		Empty values are not affected by this setting, and considered as a solid value
		:return:
		"""
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
		"""
		Callback for replacing old key with a new key where `mapped_keys` is {"OLD KEY": "NEW KEY"}

		:param mapped_keys:
		:param key:
		:param val:
		:return:
		"""
		if key in mapped_keys:
			# NOTE  Replacing old key with a new key
			return mapped_keys[key], val
		# NOTE  Returning key and val intact
		return key, val

	def _preprocess_filter_and_apply(self, config):
		"""
		Running preprocessing, filtering and applying final values

		:param config:
		:return:
		"""
		preprocessor = self._preprocessor

		if preprocessor:
			if isinstance(preprocessor, dict):
				# MARK  Maybe refactor this to avoid using lambda due to performance limitations
				_preprocessor_data = preprocessor

				def _wrapper(k, v):
					return self._key_replace_callback(_preprocessor_data, k, v)

				preprocessor = _wrapper

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

		return applied_keys

	def config_apply(
		self,
		config: "dict | ConfigStore",
		name: str = None,
		source: str = None,
		type: str = None,
		handler=None,
	):
		"""
		Setting values to the object that could be accessed dict-like style

		Alternatives for this are `update()` method and `+` operator

		:param config:
		:param name:
		:param source:
		:param type:
		:param handler:
		:return:
		"""
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
			type = ConfigStoreType.DICT

		applied_keys = self._preprocess_filter_and_apply(config)

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
			ConfigStoreType.SINGLE_VALUE
		)

	def applied_from(self, key: str, include_unprocessed_keys: bool = False) -> dict:
		"""
		Returns the latest `AppliedConf` which affected `key` value

		:param key:
		:param include_unprocessed_keys:
		:return:
		"""
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
		"""
		Equivalent of `conf["my-key"]` but you can specify default if the key is not found

		:param key:
		:param default:
		:return:
		"""
		res = self._storage.get(key)
		if self._return_default_on_none:
			if res is None:
				return default
		else:
			if key not in self:
				return default
		return res

	def clear(self):  # pragma: no cover
		raise NotPermitted("Clearing of ConfigStore is not permitted due to architecture")

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
		raise NotPermitted("Popping from ConfigStore is not permitted due to architecture")

	def popitem(self):  # pragma: no cover
		raise NotPermitted("Popping from ConfigStore is not permitted due to architecture")

	def __cmp__(self, other):  # pragma: no cover
		return self._storage == other

	def __contains__(self, item):  # pragma: no cover
		return item in self._storage

	def __iter__(self):  # pragma: no cover
		return iter(self._storage)

	def __str__(self):  # pragma: no cover
		return str(self._storage)
