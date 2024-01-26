# Overall example - Python SimpUtils Config

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

Output:
```text
VAL1:  100500
VAL2:  my new val2. Goooo JSON
VAL3:  value 3
VAL4:  dotenv4
VAL99:  12


my-value:  None
MY_VALUE:  42


Non-existing (returns None):  None
Filtered out (returns None):  None
Existing:  Hello Panda
I_EXIST applied from:  AppliedConf(
    applied_keys=['I_EXIST'], 
    type='ConfigStore', 
    name=None, 
    source=None, 
    handler=None, 
    ref={'i exist': 'Hello Panda'}
)


All the applied confs:  [
    AppliedConf(
        applied_keys=['VAL1', 'VAL2', 'VAL3'], 
        type='ConfigStore', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'val1': 'value 1', 'val2': 'value 2', 'val3': 'value 3'}
    ), 
    AppliedConf(
        applied_keys=['VAL2', 'VAL4', 'I_EXIST'], 
        type='ConfigStore', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'val2': 'new value 2', 'val4': 'value 4', 'I_EXIST': 'Hello World', 'I_WAS_FILTERED_OUT': 'Bye Panda'}
    ), 
    AppliedConf(
        applied_keys=['I_EXIST'], 
        type='ConfigStore', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'i exist': 'Hello Panda'}
    ), 
    AppliedConf(
        applied_keys=['VAL1', 'VAL5'], 
        type='YAML', 
        name='my-test-conf-file-1.yml', 
        source='/home/ivan/development/py-simputils-config/data/my-test-conf-file-1.yml', 
        handler=<simputils.config.components.handlers.YamlFileHandler.YamlFileHandler object at 0x7f208474afb0>, 
        ref={'val1': 100500, 'val5': False}
    ), 
    AppliedConf(
        applied_keys=['VAL2', 'VAL4'], 
        type='YAML', 
        name='my-test-conf-file-2.yml', 
        source='/home/ivan/development/py-simputils-config/data/my-test-conf-file-2.yml', 
        handler=<simputils.config.components.handlers.YamlFileHandler.YamlFileHandler object at 0x7f208474afb0>, 
        ref={'val2': 'VVV', 'test': [1, 2, 3], 'vaL4': 'kokoko'}
    ), 
    AppliedConf(
        applied_keys=['VAL2'], 
        type='JSON', 
        name='my-test-conf-file-4.json', 
        source='/home/ivan/development/py-simputils-config/data/my-test-conf-file-4.json', 
        handler=<simputils.config.components.handlers.JsonFileHandler.JsonFileHandler object at 0x7f208474a7d0>, 
        ref={'Val2': 'my new val2. Goooo JSON'}
    ), 
    AppliedConf(
        applied_keys=['VAL99'], 
        type='DotEnv', 
        name='first.env', 
        source='/home/ivan/development/py-simputils-config/data/first.env', 
        handler=<simputils.config.components.handlers.DotEnvFileHandler.DotEnvFileHandler object at 0x7f2084749960>, 
        ref={'TEST6666': 'rrrr', 'VAL99': '12'}
    ), 
    AppliedConf(
        applied_keys=['VAL4'], 
        type='DotEnv', 
        name='.env', 
        source='/home/ivan/development/py-simputils-config/data/.env', 
        handler=<simputils.config.components.handlers.DotEnvFileHandler.DotEnvFileHandler object at 0x7f2084749960>, 
        ref={'TEST6666': 'KKKKK', 'val4': 'dotenv4'}
    ), 
    AppliedConf(
        applied_keys=['VAL500', 'VAL300'], 
        type=<ConfigStoreType.ENV_VARS: 'EnvVars'>, 
        name='environ', 
        source='os' 
        handler=None, 
        ref={...}
    ), 
    AppliedConf(
        applied_keys=['MY_VALUE'], 
        type='single-value', 
        name='main:51', 
        source='/home/ivan/development/py-simputils-config/run.py', 
        handler=None, 
        ref={'my-value': 42}
    )
]
```
