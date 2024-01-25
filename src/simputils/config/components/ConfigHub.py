from os import PathLike, _Environ

from simputils.config.components.handlers import YamlFileHandler, JsonFileHandler, DotEnvFileHandler
from simputils.config.generic.BasicFileHandler import BasicFileHandler
from simputils.config.models import ConfigStore


class ConfigHub:

	file_handlers: list[BasicFileHandler] = [
		# NOTE  Order matters!
		JsonFileHandler(),
		YamlFileHandler(),
		DotEnvFileHandler(),
	]

	@classmethod
	def aggregate(cls, *args: PathLike | str | ConfigStore | dict, target: ConfigStore = None) -> ConfigStore:
		if target is None:  # pragma: no cover
			target = ConfigStore()
		for arg in args:
			if isinstance(arg, (PathLike, str)):
				target += cls.config_from_file(arg)
			elif isinstance(arg, (ConfigStore, dict, _Environ)):
				target += cls.config_from_dict(arg)
			else:
				# MARK  Proper exception type needed!
				raise Exception("Not supported operand type")
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
		if target is None:  # pragma: no cover
			target = ConfigStore()
		return target.config_apply(config, name, source, type)

	@classmethod
	def config_from_file(
		cls,
		file: str,
		name: str = None,
		source: str = None,
		type: str = None,
		target: ConfigStore = None
	):
		if not cls.file_handlers:
			# MARK  Add proper exception type
			raise Exception("No file handlers specified")

		is_handled = False
		for handler in cls.file_handlers:
			sub_res: ConfigStore | None = handler.process_file(file)
			if sub_res is not None:
				is_handled = True
				if target is None:
					target = sub_res
				else:  # pragma: no cover
					target.config_apply(sub_res, name, source, type)

				break

		if not is_handled:
			print(handler, sub_res)
			raise Exception(f"No handler for {file} is found")

		return target
