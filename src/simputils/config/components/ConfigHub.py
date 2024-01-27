from io import IOBase
# noinspection PyUnresolvedReferences,PyProtectedMember
from os import PathLike, _Environ

from simputils.config.components.handlers import YamlFileHandler, JsonFileHandler, DotEnvFileHandler
from simputils.config.enums import ConfigStoreType
from simputils.config.exceptions import NoAvailableHandlers, NoHandler
from simputils.config.generic.BasicFileHandler import BasicFileHandler
from simputils.config.models import ConfigStore


class ConfigHub:
	"""
	Static Helper to operate with `ConfigStore`s

	Allows to aggregate from multiple object types and sources like dict, file, StringIO, etc.
	"""

	file_handlers: list[BasicFileHandler] = [
		# NOTE  Order matters!
		JsonFileHandler(),
		YamlFileHandler(),
		DotEnvFileHandler(),
	]
	skip_files_with_missing_handler: bool = True

	@classmethod
	def aggregate(
		cls,
		*args: PathLike | str | ConfigStore | dict | IOBase,
		target: ConfigStore = None
	) -> ConfigStore:
		"""
		Aggregate configs from multiple sources.

		Just list file paths, dict, etc. and it will aggregate values from all of those
		sources to a single config

		:param args:
		:param target:
		:return:
		"""
		if target is None:  # pragma: no cover
			target = ConfigStore()
		for arg in args:
			if isinstance(arg, (PathLike, str, IOBase)):
				target += cls.config_from_file(arg)
			elif isinstance(arg, _Environ):
				target += cls.config_from_dict(
					arg,
					name="environ",
					source="os",
					type=ConfigStoreType.ENV_VARS,
				)
			elif isinstance(arg, (ConfigStore, dict)):
				target += cls.config_from_dict(arg)
			else:
				# MARK  Proper exception type needed!
				raise TypeError(
					f"unsupported operand type(s) for +: '{PathLike | str | ConfigStore | dict}' and '{type(arg).__name__}'"
				)
		return target

	@classmethod
	def config_from_dict(
		cls,
		config: dict,
		name: str = None,
		source: str = None,
		type: str = None,
		target: ConfigStore = None
	):
		"""
		Just an alias for `ConfigStore`

		:param config:
		:param name:
		:param source:
		:param type:
		:param target:
		:return:
		"""
		if target is None:  # pragma: no cover
			target = ConfigStore(
				name=name,
				source=source,
				type=type,
			)
		return target.config_apply(config, name, source, type)

	@classmethod
	def config_from_file(
		cls,
		file: PathLike | str | IOBase,
		name: str = None,
		source: str = None,
		type: str = None,
		target: ConfigStore = None,
		handler: BasicFileHandler = None
	):
		"""
		Creates `ConfigStore` from a file path, fd, StringIO, etc.

		Keep in mind that for fd or any BaseIO value, you most likely will need to specify
		explicitly `handler` param with an object of your handler.

		:param file:
		:param name:
		:param source:
		:param type:
		:param target:
		:param handler:
		:return:
		"""
		available_handlers = cls.file_handlers
		if handler:
			available_handlers = [handler, ]
		if not available_handlers:
			raise NoAvailableHandlers("No file handlers specified")

		is_handled = False
		for h in available_handlers:
			sub_res: ConfigStore | None = h.process_file(file)
			if sub_res is not None:
				is_handled = True
				if target is None:
					target = sub_res
				else:  # pragma: no cover
					target.config_apply(sub_res, name, source, type)

				break

		if not cls.skip_files_with_missing_handler and not is_handled:
			raise NoHandler(f"No handler for {file} is found")

		return target
