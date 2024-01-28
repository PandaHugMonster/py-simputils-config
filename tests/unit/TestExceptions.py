from enum import Enum
from io import StringIO

import pytest

from simputils.config.components import ConfigHub
from simputils.config.components.handlers import JsonFileHandler
from simputils.config.exceptions import NoAvailableHandlers, WrongFormat, NoHandler
from simputils.config.models import ConfigStore


@pytest.mark.order(-1)
class TestExceptions:

	def test_plus_unsupported_type(self):
		with pytest.raises(TypeError) as exc_i:
			ConfigHub.aggregate(33)
		assert exc_i.match(r".*Unsupported data-type.*")

		with pytest.raises(TypeError) as exc_i:
			ConfigStore(Enum)
		assert exc_i.match(r".*Unsupported data-type.*")

	def test_no_available_handlers(self):
		orig_file_handlers = ConfigHub.file_handlers
		ConfigHub.file_handlers = []

		with pytest.raises(NoAvailableHandlers) as exc_i:
			ConfigHub.aggregate("test.text")

		assert exc_i.errisinstance(NoAvailableHandlers)

		ConfigHub.file_handlers = orig_file_handlers

	def test_no_handler(self):
		ConfigHub.skip_files_with_missing_handler = False
		with pytest.raises(NoHandler) as exc_i:
			ConfigHub.aggregate("test.text")
		assert exc_i.errisinstance(NoHandler)

		ConfigHub.skip_files_with_missing_handler = True
		ConfigHub.aggregate("test.text")

	def test_wrong_format(self):
		with pytest.raises(WrongFormat) as exc_i:
			io_str = StringIO('["test", 2, true, null]')
			ConfigHub.config_from_file(io_str, handler=JsonFileHandler())

		assert exc_i.errisinstance(WrongFormat)

