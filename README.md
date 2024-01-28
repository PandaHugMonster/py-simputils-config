# Python SimpUtils Config
Simplifies working with configs and params.

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

When working with files, keep in mind that the only supported files are `.yml`, `.env` and `.json`.
If you need support for other types, you will have to implement your custom handler for those file-types.

## Documentation
* [The overall example](docs/overall-example.md)
* [Working with `ConfigStore`](docs/working-with-config-store.md)

## Generic examples

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
`Enum` keys are supported out of the box, and `argparser.Namespace` could be used for `ConfigStore`

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