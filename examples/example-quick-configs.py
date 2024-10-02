from simputils.config.components import ConfigHub


if __name__ == "__main__":
	# Creating config (order matters!)
	config = ConfigHub.aggregate(
		# Default values
		{
			"name": "PandaHugMonster",
			"surname": "No surname",
			"age": 34,
		},

		# File does not exist (if exists, values might be used from it)
		"my-config.yaml",
	)

	# Hard coded values
	config.update({
		"surname": "Pandytch",
		"age": 900,
	})

	name = config.get("name", "noname")
	surname = config["surname"]
	age = config.get("age", 0)
	# Country does not exist anywhere
	country = config["country"]

	print(f"Name: {name}")
	print(f"Surname: {surname}")
	print(f"Age: {age}")
	print(f"Country: {country}")
