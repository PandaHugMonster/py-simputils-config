# Python SimpUtils Config
Simplifies working with configs and params.

## Installation

This will install the latest version of the major version `1`.
It's safe enough due to followed by the project Semantic Versioning paradigm.

```shell
pip install "simputils-config~=1.0"
```

> [!WARNING]
> Developer of this project has nothing to do with `simputils` package of pypi.
> And installation of both might cause broken code. 
> 
> On the end of this project, the namespace `simputils` is made "shareable".
> But the structure of another developer's package is not designed in such way
> 
> Disclaimer about that you can find here [Potential package collision 2024](docs/disclaimers.md)


## Description
Class `simputils.config.models.ConfigStore` is the keystone of the library.
Object of it represents config, that could be used to sequentially apply different sets of key-value
pairs from different sources (other dicts, files of different kinds, environment variables, etc.).

Object will store the latest values of the applied sets, 
where the earliest applied values could be overriden by the following ones.
Basically, just a dictionary.

But besides being like a dictionary, it records the "history" of applied configs, so it's easier to
debug and control from where which value came from.

The major purpose of the functionality comes from using multiple files as sources for your config,
but it still allows to apply sets directly from the code.

Project follows [Semantic Versioning](https://semver.org/) standard. 
No breaking changes suppose to be within `minor` and `patch` versions of the same `major` version.
Exception is only if there is a bug, that gets fixed.

> [!CAUTION]
> `ConfigStore` object is behaving like a `dict`, so if you need to check if
> the variable with this object is None, always check it like `if conf is None:`,
> and never check it like `if not conf:`!
> 
> The check is implicit, so when you use `not` or simple boolean check, it will check if the object
> is empty (does not contain any value)

> [!NOTE]
> To check if `ConfigStore` object contains at least one key-value pair, 
> you can use simple `if conf:`

----

When working with files, keep in mind that the only supported files are `.yml`/`.yaml`, `.env` and `.json`.
If you need support for other types, you will have to implement your custom handler(s) for those file-types.

## Documentation
* [Changelog](docs/CHANGELOG.md) - Please make sure you check it for new features and changes
* [The overall example](docs/overall-example.md)
* [Working with enums and annotations](docs/working-with-enums-and-annotations.md)
* [Config Object Style Access](docs/config-object-style-access.md)
* [Preprocessing and filtering](docs/preprocessing-and-filtering.md)
* [Working with `ConfigHub`](docs/working-with-config-hub.md)
  (Quick Start, recommended way to work with the configs)
* [Working with `ConfigStore`](docs/working-with-config-store.md)
* [Config Merging Strategies](docs/config-merging-strategies.md)

### Config Modifiers

There are 3 config modifiers that could be applied: `preprocessor`, `filter` and annotation type-casting 

> [!INFO]
> The order of config modifiers applied to each config:
> 1. `preprocessor`
> 2. `filter`
> 3. Annotation type-casting

## Generic examples

### The simplest usage

Aggregation from multiple sources (you can specify any number of sources).

> [!IMPORTANT]
> Keep in mind that order matters, keys/values from the latest might override already specified

From files:
```python
from simputils.config.components import ConfigHub

conf = ConfigHub.aggregate(
    "config-1.yml",
    "config-2.yml",
    # ...
)
print(conf, conf.applied_confs)
```

From dictionaries:
```python
from simputils.config.components import ConfigHub

conf = ConfigHub.aggregate(
	{"key1": "val1", "key2": "val2"},
    {"key2": "redefined val2", "key3": "val3"},
    # ...
)
print(conf, conf.applied_confs)
```

Accessing values:
```python

# Accessing values by name, if does not exist - None is returned
conf["key1"]
conf["key2"]

# Accessing values by name, if does not exist or None - `default` parameter value is returned
conf.get("key1", "My Default Value")
conf.get("key2")

# Iterating as a dictionary
for key, val in conf.items():
    print(key, val)
```

### Enums as default config with filter

```python
import os
from typing import Annotated

from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore, AnnotatedConfigData


class MyEnum(BasicConfigEnum):

    # Annotated without and with default values set
    MY_E_KEY_1: Annotated[str, AnnotatedConfigData()] = "my-e-key-1"

    MY_E_KEY_2: Annotated[str, AnnotatedConfigData(
        default=3.1415
    )] = "my-e-key-2"

    # Non-annotated, so they will be None by default
    MY_E_KEY_3 = "my-e-key-3"
    MY_E_KEY_4 = "my-e-key-4"
    MY_E_KEY_5 = "my-e-key-5"

    # Some of them used in `app-conf.yml`
    MY_FIRST_VAL = "val-1"
    MY_SECOND_VAL = "VAL_2"

    # Will be taken from os.environ,
    # all other os.environ values will be excluded
    ENV_USER_NAME = "USER"


conf = ConfigHub.aggregate(
    "tests/data/config-1.yml",

    os.environ,

    target=ConfigStore(
        MyEnum.defaults(),
        preprocessor=simputils_pp,
        filter=True
    ),
)

print("conf: ", conf)
```

```text
conf:  {
    'MY_E_KEY_1': None, 
    'MY_E_KEY_2': 3.1415, 
    'MY_E_KEY_3': None, 
    'MY_E_KEY_4': None, 
    'MY_E_KEY_5': None, 
    'VAL_1': 'My conf value 1', 
    'VAL_2': 'My conf value 2', 
    'USER': 'ivan'
}
```

### Enums and argparser support
`Enum` keys are supported out of the box, and `argparse.Namespace` could be used for `ConfigStore`

> [!NOTE]
> `BasicConfigEnum` is used for convenience. 
> And it's suggested way, it allows to use `True` as a filter key
> 
> You still can use Enums without that class, 
> just make sure that enum is inherited from `str, Enum` in that order! 

```python
from argparse import ArgumentParser

from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.models import ConfigStore
from simputils.config.generic import BasicConfigEnum


args_parser = ArgumentParser()
args_parser.add_argument("--name", "-n", default="PandaHugMonster")
args_parser.add_argument("--age", default="33")

args = args_parser.parse_args(["--name", "Oldie", "--age", "34"])


class MyEnum(BasicConfigEnum):
	MY_1 = "key-1"
	MY_2 = "key-2"
	MY_3 = "key-3"

	NAME = "name"
	AGE = "age"

c = ConfigHub.aggregate(
	{MyEnum.MY_2: "new val 2", "test": "test"},
	args,
	target=ConfigStore(
        MyEnum.defaults(),
		preprocessor=simputils_pp,
		filter=True
	)
)
```

### Simple Config and EnvVars

```python
import os

from simputils.config.components import ConfigHub

# Sequence of files/values matter!
app_conf = ConfigHub.aggregate(
	"data/app-conf.yml",

	# This one does not exist, and used only for local redefinitions of developer or stage
	"data/app-conf-local.yml",
)

# Sequence of files/values matter!
app_env_vars = ConfigHub.aggregate(
	"data/production.env",

	# This one does not exist, and used only for local redefinitions of developer or stage
	"data/production-local.env",

	# This one does not exist, and used only for local redefinitions of developer or stage
	".env",

	# Environment Variables from OS
	os.environ,
)

print("App Conf: ", app_conf)
print("App EnvVars: ", app_env_vars)
```

```text
App Conf:  {
    'val-1': 'My conf value 1', 
    'val-2': 'My conf value 2', 
    'val-3': 'My conf value 3'
}
App EnvVars:  {
    'APP_MY_ENV_VAR_1': '1', 
    'APP_MY_ENV_VAR_2': '2', 
    'APP_MY_ENV_VAR_3': '3',
    
    ...(values from OS env-vars are here) 
}
```

