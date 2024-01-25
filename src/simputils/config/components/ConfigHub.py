from os import PathLike
from typing import Callable

from simputils.config.components.handlers import YamlFileHandler
from simputils.config.generic import BasicConfigStore
from simputils.config.generic.BasicFileHandler import BasicFileHandler
from simputils.config.models import ConfigStore


class ConfigHub:

	file_handlers: list[BasicFileHandler] = [
		YamlFileHandler(),
	]

	@classmethod
	def aggregate(cls, *args: PathLike | str | BasicConfigStore | dict, target: BasicConfigStore = None) -> BasicConfigStore:
		if target is None:
			target = ConfigStore()
		for arg in args:
			if isinstance(arg, (PathLike, str)):
				target += cls.config_from_file(arg)
			elif isinstance(arg, (BasicConfigStore, dict)):
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
		target: BasicConfigStore = None
	):
		if target is None:
			target = ConfigStore()
		return target.config_apply(config, name, source, type)

	@classmethod
	def config_from_file(
		cls,
		file: str,
		name: str = None,
		source: str = None,
		type: str = None,
		target: BasicConfigStore = None
	):
		if not cls.file_handlers:
			# MARK  Add proper exception type
			raise Exception("No file handlers specified")

		for handler in cls.file_handlers:
			sub_res: BasicConfigStore | None = handler.process_file(file)
			if sub_res is not None:
				if target is None:
					return sub_res
				target.config_apply(sub_res, name, source, type)
				break

		return target

	# @classmethod
	# def preprocess(cls, config: dict | BasicConfigStore, preprocessor: dict | Callable):

