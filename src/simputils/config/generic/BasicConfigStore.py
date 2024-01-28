import inspect
from abc import ABCMeta, abstractmethod
from argparse import Namespace
from collections.abc import Iterable
from enum import Enum
from os import _Environ
from typing import Any, Callable

from typing_extensions import Self

from simputils.config.enums import ConfigStoreType
from simputils.config.exceptions import NotPermitted
from simputils.config.generic import BasicAppliedConf
from simputils.config.types import ConfigType, PreProcessorType, FilterType, SourceType, HandlerType


class BasicConfigStore(dict, metaclass=ABCMeta):

	_return_default_on_none: bool = True
	_name: str = None
	_source: SourceType = None
	_type: str = None
	_applied_confs: list[BasicAppliedConf] = None
	_storage: dict = None
	_preprocessor: PreProcessorType = None
	_filter: FilterType = None
	_applied_conf_class = None
	_initial_preprocessed_keys: list[str] = None

	_handler: HandlerType = None
	"""Handler is just a reference, it is not being called from within ConfigStore"""

	@classmethod
	@abstractmethod
	def applied_conf_class(cls):  # pragma: no cover
		pass

	@property
	def name(self) -> str | None:
		return self._name

	@property
	def source(self) -> SourceType | None:
		return self._source

	@property
	def type(self) -> str | None:
		return self._type

	@property
	def handler(self) -> HandlerType | None:
		"""Handler is just a reference, it is not being called from within ConfigStore"""
		return self._handler

	@property
	def applied_confs(self) -> list[BasicAppliedConf]:
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
		values: ConfigType = None,
		name: str = None,
		source: SourceType = None,
		type: str = None,
		preprocessor: PreProcessorType = None,
		filter: FilterType = None,
		handler: HandlerType = None,
		return_default_on_none: bool = True,
	):
		self._applied_confs = []
		self._storage = {}
		self._initial_preprocessed_keys = []
		self._return_default_on_none = return_default_on_none
		self._applied_conf_class = self.applied_conf_class()

		values, self._name, self._source, self._type, self._handler = self._prepare_supported_types(
			values,
			name,
			source,
			type,
			handler,
		)

		self._handler = handler
		self._preprocessor = preprocessor = self._prepare_preprocessor(preprocessor)
		self._filter = self._prepare_filter(filter, preprocessor)

		self.config_apply(
			values,
			self._name,
			self._source,
			self._type,
			self._handler
		)

	def __val_or_val(self, val1: Any | None, val2: Any | None):
		return val2 if val1 is None else val1

	def _prepare_supported_types(
		self,
		values,
		name: str = None,
		source: SourceType = None,
		type: str = None,
		handler: HandlerType = None
	):
		if isinstance(values, _Environ):
			name = self.__val_or_val(name, "environ")
			source = self.__val_or_val(source, "os")
			type = self.__val_or_val(type, ConfigStoreType.ENV_VARS)
		elif isinstance(values, Namespace):
			name = self.__val_or_val(name, "args")
			source = self.__val_or_val(source, values)
			type = self.__val_or_val(type, ConfigStoreType.ARGPARSER_NAMESPACE)
			values = vars(values)
		elif isinstance(values, self.__class__):
			name = self.__val_or_val(name, values.name)
			source = self.__val_or_val(source, values.source)
			type = self.__val_or_val(type, values.type)
			handler = self.__val_or_val(handler, values.handler)
		elif isinstance(values, dict):
			type = self.__val_or_val(type, ConfigStoreType.DICT)
		elif values is not None:
			raise TypeError(
				f"Unsupported data-type. ConfigStore supports only {ConfigType}"
			)

		if not type:
			type = self.__class__.__name__

		return values, name, source, type, handler

	def _key_replace_callback(self, mapped_keys: dict[str, str], key: str, val: Any):
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

	def _prepare_preprocessor(self, preprocessor):

		if isinstance(preprocessor, dict):
			# MARK  Maybe refactor this to avoid using lambda due to performance limitations
			_preprocessor_data = preprocessor

			def _wrapper(k, v):
				return self._key_replace_callback(_preprocessor_data, k, v)

			preprocessor = _wrapper
		elif not callable(preprocessor):

			def _wrapper(k, v):
				return k, v

			preprocessor = _wrapper

		return preprocessor

	def _prepare_filter(self, filter: FilterType, preprocessor: Callable):
		_filter = filter
		if isinstance(filter, Iterable) or filter is True:

			# NOTE  In case if filter is set to True
			_filter = self._initial_preprocessed_keys if _filter is True else _filter

			def _wrapper(key: str, val: Any):
				key, _ = preprocessor(key, val)
				if not _filter:
					return True
				for filter_key in _filter:
					filter_key, _ = preprocessor(filter_key, None)
					if filter_key == key:
						return True
				return False

			filter = _wrapper

		elif not callable(filter):
			def _wrapper(key: str, val: Any):
				return True
			filter = _wrapper

		return filter

	def _apply_data(self, config: ConfigType, preprocessor: Callable, filter: Callable):
		applied_keys = []

		for key, val in dict(config).items():
			key, val = preprocessor(key, val)
			if filter(key, val):
				applied_keys.append(key)
				self._storage[key] = val

		if not self._initial_preprocessed_keys and config is not None:
			for key in dict(config).keys():
				key, _ = preprocessor(key, None)
				self._initial_preprocessed_keys.append(key)

		return applied_keys

	def config_apply(
		self,
		config: ConfigType,
		name: str = None,
		source: SourceType = None,
		type: str = None,
		handler: HandlerType = None,
	) -> Self:
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

		applied_conf_class = self._applied_conf_class

		config, name, source, type, handler = self._prepare_supported_types(config, name, source, type, handler)

		applied_keys = self._apply_data(config, self._preprocessor, self._filter)

		self._applied_confs.append(
			applied_conf_class(
				applied_keys=applied_keys,
				type=type,
				name=name,
				source=source,
				ref=config,
				handler=handler,
			)
		)
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
			if key in record.applied_keys:
				return record
			if include_unprocessed_keys and key in record.ref:  # pragma: no cover
				return record

		return None

	def __add__(self, other):  # pragma: no cover
		return self.config_apply(other)

	def __repr__(self):  # pragma: no cover
		return repr(self._storage)

	def __len__(self):  # pragma: no cover
		return len(self._storage)

	def __delitem__(self, key):  # pragma: no cover
		del self._storage[key]

	def __getitem__(self, key):
		preprocessor = self._preprocessor

		if isinstance(key, str) and isinstance(key, Enum):
			key, _ = preprocessor(key.value, None)
		return self._storage.get(key)

	def get(self, key: str, default: Any = None):
		"""
		Equivalent to `conf["my-key"]` but you can specify default if the key is not found

		:param key:
		:param default:
		:return:
		"""
		preprocessor = self._preprocessor

		if isinstance(key, str) and isinstance(key, Enum):
			key, _ = preprocessor(key.value, None)

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
