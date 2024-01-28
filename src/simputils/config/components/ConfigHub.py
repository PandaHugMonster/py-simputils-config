from simputils.config.components.handlers import YamlFileHandler, JsonFileHandler, DotEnvFileHandler
from simputils.config.exceptions import NoAvailableHandlers, NoHandler
from simputils.config.models import ConfigStore
from simputils.config.types import HandlerType, ConfigType, FileType, SourceType


class ConfigHub:
	"""
	Static Helper to operate with `ConfigStore`s

	Allows to aggregate from multiple object types and sources like dict, file, StringIO, etc.
	"""

	skip_files_with_missing_handler: bool = True
	file_handlers: list[HandlerType] = [
		# NOTE  Order matters!
		JsonFileHandler(),
		YamlFileHandler(),
		DotEnvFileHandler(),
	]

	@classmethod
	def aggregate(
		cls,
		*args: ConfigType | FileType,
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
			if isinstance(arg, FileType):
				target += cls.config_from_file(arg)
			elif isinstance(arg, ConfigType):
				target += cls.config_from_dict(arg)
			else:
				raise TypeError(
					f"Unsupported data-type. ConfigStore supports only {ConfigType}"
				)

		return target

	@classmethod
	def config_from_dict(
		cls,
		config: ConfigType,
		name: str = None,
		source: SourceType = None,
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
		file: FileType,
		name: str = None,
		source: SourceType = None,
		type: str = None,
		target: ConfigStore = None,
		handler: HandlerType = None
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
			sub_res: ConfigStore | None = h(file)
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
