import pytest

from simputils.config.components import ConfigHub
from simputils.config.exceptions import NoAvailableHandlers


@pytest.mark.order(-1)
class TestExceptions:

	def test_plus_unsupported_type(self):
		with pytest.raises(TypeError) as exc_i:
			ConfigHub.aggregate(33)

		assert exc_i.match(r".*unsupported operand type.*")

	def test_no_file_handlers_specified(self):
		orig_file_handlers = ConfigHub.file_handlers
		ConfigHub.file_handlers = []

		with pytest.raises(NoAvailableHandlers) as exc_i:
			ConfigHub.aggregate("test.text")

		assert exc_i.errisinstance(NoAvailableHandlers)

		ConfigHub.file_handlers = orig_file_handlers

	# def test_wrong_format(self):
	#   TODO    Too complicated right now, add later
	# 	ConfigHub.file_handlers = []
	#
	# 	with pytest.raises(WrongFormat) as exc_i:
	# 		io_str = StringIO("//////asdasd")
	# 		ConfigHub.aggregate(io_str)
	#
	# 	assert exc_i.errisinstance(WrongFormat)

