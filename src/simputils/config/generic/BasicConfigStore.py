import importlib.util
import inspect
from abc import ABCMeta, abstractmethod
from argparse import Namespace
from collections.abc import Iterable
from enum import Enum
# noinspection PyUnresolvedReferences,PyProtectedMember
from os import _Environ
from typing import Any, Callable, get_args

from simputils.config.base import get_enum_defaults, get_enum_all_annotations
from simputils.config.components.prisms import ObjConfigStorePrism
from simputils.config.components.strategies import MergingStrategyFlat, MergingStrategyRecursive
from simputils.config.enums import ConfigStoreType, MergingStrategiesEnum
from simputils.config.exceptions import NotPermitted, StrictKeysEnabled
from simputils.config.generic import BasicAppliedConf, BasicMergingStrategy
from simputils.config.types import ConfigType, PreProcessorType, FilterType, SourceType, HandlerType

_type_func = type


# noinspection PyMissingConstructor
class BasicConfigStore(dict, metaclass=ABCMeta):

	_op_class = None
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
	_strict_keys: bool = False
	_strategy: str | BasicMergingStrategy = None

	_handler: HandlerType = None
	"""Handler is just a reference, it is not being called from within ConfigStore"""

	_obj_prism: ObjConfigStorePrism = None

	_pydantic_base_model_class = None

	@classmethod
	@abstractmethod
	def applied_conf_class(cls):  # pragma: no cover
		pass

	@property
	def obj(self) -> ObjConfigStorePrism:
		"""
		Returns Object Prism for ConfigStore
		"""
		if not self._obj_prism:
			self._obj_prism = ObjConfigStorePrism(self)
		return self._obj_prism

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
	def strategy(self):  # pragma: no cover
		return self._strategy

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

	_is_pydantic_enabled: bool = True

	@classmethod
	def _set_pydantic_enabled(cls, val: bool):
		if val is False:
			cls._pydantic_base_model_class = None
		cls._is_pydantic_enabled = val

	# noinspection PyShadowingBuiltins
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
		strict_keys: bool = False,
		strategy: str | BasicMergingStrategy = MergingStrategiesEnum.FLAT,
	):
		if self._is_pydantic_enabled:
			self._pydantic_setup()

		self._applied_confs = []
		self._storage = {}
		self._initial_preprocessed_keys = []
		self._strict_keys = strict_keys
		self._return_default_on_none = return_default_on_none
		self._applied_conf_class = self.applied_conf_class()

		self._prepare_strategy(strategy)

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

	def _prepare_strategy(self, strategy):
		strategies_group = {
			MergingStrategiesEnum.FLAT: MergingStrategyFlat,
			MergingStrategiesEnum.RECURSIVE: MergingStrategyRecursive,
		}

		if isinstance(strategy, BasicMergingStrategy):
			self._strategy = strategy
		else:
			strategy_class = strategies_group[MergingStrategiesEnum.FLAT]

			if strategy in strategies_group:
				strategy_class = strategies_group[strategy]

			self._strategy = strategy_class()

	@classmethod
	def _pydantic_setup(cls):
		try:
			if not cls._pydantic_base_model_class:
				pydantic_namespace = importlib.util.find_spec("pydantic")
				if pydantic_namespace:
					cls._pydantic_base_model_class = getattr(
						importlib.import_module("pydantic"),
						"BaseModel"
					)
		except (ModuleNotFoundError, AttributeError):  # pragma: no cover
			pass

	def __val_or_val(self, val1: Any | None, val2: Any | None):
		return val2 if val1 is None else val1

	def _prepare_supported_types(  # noqa (The complexity here is necessary)
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
		elif inspect.isclass(values) and issubclass(values, Enum) and issubclass(values, str):
			name = _type_func(values)
			source = values
			type = ConfigStoreType.ENUM
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

	def _get_prepare_pp_for_dict(self, preprocessor_data):
		def _wrapper(k, v):
			return self._key_replace_callback(preprocessor_data, k, v)
		return _wrapper

	def _get_prepare_pp_for_list(self, callable_list):
		def _wrapper(k, v):
			for cbk in callable_list:
				k, v = cbk(k, v)
			return k, v
		return _wrapper

	def _get_prepare_pp_for_non_callable(self):
		def _wrapper(k, v):
			return k, v
		return _wrapper

	def _prepare_preprocessor(self, preprocessor):

		if isinstance(preprocessor, dict):
			preprocessor = self._get_prepare_pp_for_dict(preprocessor)
		elif isinstance(preprocessor, (tuple, list)):
			preprocessor = self._get_prepare_pp_for_list(preprocessor)
		elif not callable(preprocessor):
			preprocessor = self._get_prepare_pp_for_non_callable()

		return preprocessor

	def _get_prepare_filter_wrapper(self, filter, preprocessor):
		def _wrapper(key: str, val: Any):
			key, _ = preprocessor(key, val)
			if not filter:
				return True
			for filter_key in filter:
				filter_key, _ = preprocessor(filter_key, None)
				if filter_key == key:
					return True
			return False
		return _wrapper

	# noinspection PyShadowingBuiltins
	def _prepare_filter(self, filter: FilterType, preprocessor: Callable):
		_filter = filter
		if isinstance(filter, Iterable) or filter is True:

			# NOTE  In case if filter is set to True
			_filter = self._initial_preprocessed_keys if _filter is True else _filter

			filter = self._get_prepare_filter_wrapper(_filter, preprocessor)

		elif not callable(filter):
			def _wrapper(key: str, val: Any):
				return True
			filter = _wrapper

		return filter

	# noinspection PyShadowingBuiltins
	def _apply_data(self, config: ConfigType, preprocessor: Callable, filter: Callable):
		storage_result, applied_keys = self._strategy.apply_data(self, config, preprocessor, filter)
		for key, val in storage_result.items():
			self._storage[key] = val

		# MARK	Can be optimized with help of `applied_keys`
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

		# MARK	Here missing the check for unknown keys!

		applied_conf_class = self._applied_conf_class

		config, name, source, type, handler = self._prepare_supported_types(config, name, source, type, handler)

		if not self.applied_confs and inspect.isclass(config) and issubclass(config, Enum) and issubclass(config, str):
			self._op_class = config

		if config and inspect.isclass(config) and issubclass(config, Enum) and issubclass(config, str):
			config = get_enum_defaults(self._op_class)

		if self._op_class and issubclass(self._op_class, Enum) and issubclass(self._op_class, str):
			config = self._process_str_enum(config)

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

	def _process_str_enum(self, config):
		annotations = get_enum_all_annotations(self._op_class)
		for key, val in config.items():
			if key not in annotations:
				continue
			annotated_data = annotations[key].data

			if annotated_data and "type" in annotated_data and annotated_data["type"]:
				like_union = get_args(annotated_data["type"])
				if not like_union:
					like_union = (annotated_data["type"],)

				self._process_union_subtypes(config, like_union, key, val)

		return config

	def _process_union_subtypes(self, config, like_union, key, val):
		pydantic_base_model_class = self._pydantic_base_model_class
		for subtype in like_union:
			if val is None:
				config[key] = val
				break
			elif callable(subtype):
				# noinspection PyTypeChecker
				if pydantic_base_model_class and issubclass(subtype, pydantic_base_model_class):
					# noinspection PyTypeChecker
					if isinstance(val, subtype):
						config[key] = val
					else:
						config[key] = subtype(**val)
				else:
					config[key] = subtype(val)
				break

	def applied_from(self, key: str, include_unprocessed_keys: bool = False) -> dict | None:
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

	def get(self, key: str, default: Any = None):
		"""
		Equivalent to `conf["my-key"]` but you can specify default if the key is not found

		:param key:
		:param default:
		:return:
		"""
		preprocessor = self._preprocessor
		key, _ = preprocessor(key, None)

		if self._strict_keys and key not in self._storage:
			raise StrictKeysEnabled(
				f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown"
			)

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
		if self._strict_keys:
			for key in __m:
				preprocessor = self._preprocessor
				key, _ = preprocessor(key, None)
				if key not in self._storage:
					raise StrictKeysEnabled(
						f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown"
					)
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

	def __setitem__(self, key, value):
		preprocessor = self._preprocessor
		key, _ = preprocessor(key, None)

		if self._strict_keys and key not in self._storage:
			raise StrictKeysEnabled(
				f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown"
			)

		frame_context = inspect.stack()[1][0]
		frame_info = inspect.getframeinfo(frame_context)

		self.config_apply(
			{key: value},
			f"{frame_info.function}:{frame_info.lineno}",
			frame_info.filename,
			ConfigStoreType.SINGLE_VALUE
		)

	def __add__(self, other):  # pragma: no cover
		if self._strict_keys:
			for key in other:
				preprocessor = self._preprocessor
				key, _ = preprocessor(key, None)
				if key not in self._storage:
					raise StrictKeysEnabled(
						f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown"
					)
		return self.config_apply(other)

	def __repr__(self):  # pragma: no cover
		return repr(self._storage)

	def __len__(self):  # pragma: no cover
		return len(self._storage)

	def __delitem__(self, key):  # pragma: no cover
		del self._storage[key]

	def __getitem__(self, key):
		preprocessor = self._preprocessor
		key, _ = preprocessor(key, None)

		if self._strict_keys and key not in self._storage:
			raise StrictKeysEnabled(
				f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown"
			)

		return self._storage.get(key)

	def __cmp__(self, other):  # pragma: no cover
		return self._storage == other

	def __contains__(self, item):  # pragma: no cover
		return item in self._storage

	def __iter__(self):  # pragma: no cover
		return iter(self._storage)

	def __str__(self):  # pragma: no cover
		return str(self._storage)
