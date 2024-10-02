import os

from simputils.config.components import ConfigHub
from simputils.config.models import ConfigStore

if __name__ == "__main__":
	only_allowed_keys = ("USER", "HOME")

	# Creating config
	config = ConfigHub.aggregate(
		# Getting all the env-vars from the system
		os.environ,

		target=ConfigStore(
			# Config will contain only the allowed key/value pairs
			filter=only_allowed_keys
		)
	)

	print(f"Filtered env-vars: {config}")
