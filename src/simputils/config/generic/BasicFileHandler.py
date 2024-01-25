from abc import ABCMeta, abstractmethod


class BasicFileHandler(metaclass=ABCMeta):

	@abstractmethod
	def supported_types(self) -> tuple:
		pass

	@abstractmethod
	def process_file(self, file: str):
		pass
