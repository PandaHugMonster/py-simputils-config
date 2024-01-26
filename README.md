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
but it still allows to apply changes directly from the code.

The overall example:
```python
import os
import re

from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.models import ConfigStore


conf = ConfigHub.aggregate(
    {
        "val1": "value 1",
        "val2": "value 2",
        "val3": "value 3",
    },
    {
        "val2": "new value 2",
        "val4": "value 4",
        "I_EXIST": "Hello World",
        "I_WAS_FILTERED_OUT": "Bye Panda"
    },
    {
        "i exist": "Hello Panda"
    },

    "data/my-test-conf-file-1.yml",
    "data/my-test-conf-file-2.yml",

    "data/my-test-conf-file-4.json",

    "data/first.env",

    "data/.env",

    os.environ,

    target=ConfigStore(
        # Keep in mind that this preprocessor modifies keys to uppercase/underscored format
        preprocessor=simputils_pp,
        # Keep in mind that this filter will filter out those keys/values that do not comply
        # Filter could use just tuple of key names:  filter=("VAL2", "VAL4"),
        filter=lambda k, v: re.match(r"(VAL[0-9]+)|(I_EXIST)|(MY_VALUE)", k),
    ),
)
# Preprocessor is applied before the filter, so all the filtering rules
# must consider that!

# You can work with it (almost) like with a normal dict (with some tiny limitations)
conf["my-value"] = 42

# The latest value comes from `data/my-test-conf-file-1.yml` file
print("VAL1: ", conf["VAL1"])

# The latest value comes from `data/my-test-conf-file-4.json` file
print("VAL2: ", conf["VAL2"])

# The latest value comes from the very first dictionary
print("VAL3: ", conf["VAL3"])

# The latest value comes from `data/.env` file
print("VAL4: ", conf["VAL4"])

# The latest value comes from `data/first.env` file
print("VAL99: ", conf["VAL99"])

print("\n")

# Will be empty, because the name was preprocessed/modified by preprocessor
print("my-value: ", conf["my-value"])

# And this one will work, despite initial `my-value` name (and filter explicitly set to allow it)
print("MY_VALUE: ", conf["MY_VALUE"])

print("\n")

print("Non-existing (returns None): ", conf["i-do-not-exist"])
print("Filtered out (returns None): ", conf["I_WAS_FILTERED_OUT"])
print("Existing: ", conf["I_EXIST"])
print("I_EXIST applied from: ", conf.applied_from("I_EXIST"))

print("\n")

print("All the applied confs: ", conf.applied_confs)


```

> [!CAUTION]
> `ConfigStore` object is behaving like a `dict`, so if you need to check if
> the variable with this object is None, always check it like `if conf is None:`,
> and never check it like `if not conf:`!
> The check is implicit, so when you use `not` or simple boolean check, it will check if the object
> is empty (does not contain any value)

> [!NOTE]
> To check if `ConfigStore` object contains at least one key-value pair, 
> you can use simple `if conf:`