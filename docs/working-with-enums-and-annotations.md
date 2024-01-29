# Enums and Annotations

simputils-config allows to create `enum`s as a reference point for config.

It would enable you to:
1. In-code reference/naming decoupled from config (to user exposed naming). 
   Vital part of decoupling, refactoring and Architecture in general
2. Single "source of truth" in matter of one or multiple grouped `enum`s
3. Attach additional annotations/meta-data to `enum` fields
4. Filter-out based on that `enum` all/some unknown keys

## Simple Example

```python
import os
from simputils.config.base import simputils_pp
from simputils.config.models import ConfigStore
from simputils.config.components import ConfigHub
from simputils.config.models import AnnotatedConfigData
from typing import Annotated
from simputils.config.generic import BasicConfigEnum


class MyEnum(BasicConfigEnum):
   # Annotated without and with default values set
   MY_E_KEY_1: Annotated[str, AnnotatedConfigData()] = "my-e-key-1"

   MY_2: Annotated[str, AnnotatedConfigData(
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
   # Config from file (technically it's not first buy second in line, 
   # because `target` contains defaults, which are first in line)
   "data/config-1.yml",

   # Taking EnvVars from OS, though anything not in `MyEnum` class - will be filtered out
   os.environ,

   target=ConfigStore(
      # These defaults + preprocessor + filter will define how conf will behave
      # and apply other confs
      MyEnum.defaults(),
      preprocessor=simputils_pp,
      filter=True
   ),
)

print("conf: ", conf, conf.applied_confs)
```

Output:
```text
conf:  {
   'MY_E_KEY_1': None, 
   'MY_E_KEY_2': 3.1415, 
   'MY_E_KEY_3': None, 
   'MY_E_KEY_4': None, 
   'MY_E_KEY_5': None, 
   'VAL_1': None, 
   'VAL_2': None, 
   'USER': 'ivan'
}
[
   AppliedConf(
      applied_keys=['MY_E_KEY_1', 'MY_E_KEY_2', 'MY_E_KEY_3', 'MY_E_KEY_4', 'MY_E_KEY_5', 'VAL_1', 'VAL_2', 'USER'], 
      type=<ConfigStoreType.DICT: 'dict'>, 
      name=None, 
      source=None, 
      handler=None, 
      ref={'my-e-key-1': None, 'my-e-key-2': 3.1415, 'my-e-key-3': None, 'my-e-key-4': None, 'my-e-key-5': None, 'val-1': None, 'VAL_2': None, 'USER': None}
   ), 
   AppliedConf(
      applied_keys=['USER'], 
      type='ConfigStore', 
      name=None, 
      source=None, 
      handler=None, 
      ref={...}
   )
]

```