

class AnnotatedConfigData:
	_data: dict = None

	@property
	def data(self):
		return self._data

	def __init__(self, default=None, type=None, **kwargs):
		self._data = {
			"default": default,
			"type": type,
			**kwargs
		}
