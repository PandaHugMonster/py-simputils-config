from argparse import ArgumentParser

from simputils.config.components import ConfigHub
from simputils.config.models import ConfigStore

if __name__ == "__main__":

	parser = ArgumentParser()
	parser.add_argument("-n", "--name", type=str, required=True)
	parser.add_argument("-s", "--surname", type=str)
	parser.add_argument("-a", "--age", type=int)

	args = parser.parse_args()

	# MARK  Issue with defaults and argparser, none overrides

	# Creating config
	config = ConfigHub.aggregate(
		# Defaults
		{
			"surname": "no surname",
			"age": 0,
			"country": "no country",
		},

		# Arg-parser values
		args,

		target=ConfigStore(
			none_considered_empty=True
		)
	)

	print(f"Arg-parser values: {config} / {config.applied_from('age')}")
	# print(f"Arg-parser values: {config} / {config.applied_confs}")
