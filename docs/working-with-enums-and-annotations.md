# Enums and Annotations

simputils-config allows to create `enum`s as a reference point for config.

It would enable you to:
1. In-code reference/naming decoupled from config (to-user exposed naming). 
   Vital part of decoupling, refactoring and Architecture in general
2. Single "source of truth" in matter of one or multi-grouped `enum`s
3. Attach additional annotations/meta-data to `enum` fields, that you can customize by your taste
4. Filter-out based on that `enum` all/some unknown keys

> [!WARNING]
> It's very reasonable to apply `filter=True` by default to your main target config(s)
> to make sure no unverified key/value pairs would leak from a potential user input!
> Or at least specify your own `filter` callable to control that.

----

## Single enum target config

> [!NOTE]
> If you work on a middle or big size projects, please, 
> preferably use [Multiple enums target config](#Multiple-enums-target-config).
> In this case architecture of your project will tell you "thank you" (due to improved decoupling)!


```python
import os
from typing import Annotated

from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import AnnotatedConfigData


class MyBaseConfEnum(BasicConfigEnum):
   # Annotated with default value and type specified
   KEY_1: Annotated[str, AnnotatedConfigData(
      default=3.1415,
      type=float
   )] = "MY_KEY_1"

   KEY_2: Annotated[str, AnnotatedConfigData(
      default=15,
      type=float
   )] = "MY_KEY_2"

   # Non-annotated, so they will be None by default
   KEY_3 = "MY_KEY_3"
   KEY_4 = "MY_KEY_4"
   
   USER_NAME = "USER"


conf = ConfigHub.aggregate(
   # Config number 1
   {
      MyBaseConfEnum.KEY_4: "Non Empty Value",
      "NON_ALLOWED_KEY": 42,
   },
   
   # Config number 2
   {
      MyBaseConfEnum.KEY_2: True,
   },
   
   # Config number 3
   # Taking EnvVars from OS, though anything not in target config - will be filtered out
   os.environ,
   
   # Config number 0
   # Target config is always number 0
   target=MyBaseConfEnum.target_config(
      preprocessor=simputils_pp,
      filter=True
   ),
)

print("conf: ", conf)
```

Output:
```text
conf:  {
    'MY_KEY_1': 3.1415, 
    'MY_KEY_2': 1.0, 
    'MY_KEY_3': None, 
    'MY_KEY_4': 'Non Empty Value', 
    'USER': 'ivan'
 }
```

> [!NOTE]
> ```python
> MyBaseConfEnum.target_config(preprocessor=simputils_pp, filter=True)
> ```
> in the example - is just a shortcut for
> ```python
> ConfigStore(MyBaseConfEnum, preprocessor=simputils_pp, filter=True)
> ```
> 
> Using `target_config()` method of `enum` is suggested way, but it's really up to you.
> There is no "best practice" in between those 2 ways

In this example the enum-keys are representing in-code references, 
while the corresponding values are used as config key strings (dictionary keys).

This design is very much intentional, it allows to decouple code references 
from param names coming from outside the app.

Declared annotations allow to additionally specify `default` value of any kind,
and `type` value of `callable`, `type` or `Union` of types.

* `default` just sets the default value for the key.
* If `type` specified, then it will be used for casting of an incoming value

> [!IMPORTANT]
> `type` casting will happen after `preprocessor` and `filter` if those are specified,
> so `type` will cast on already modified by `preprocessor` (if it was modifying it in a first place)
> So the order of modifiers is following:
> 1. `preprocessor`
> 2. `filter`
> 3. `type` casting

----

## Multiple enums target config

There is no point to dump all the key/value pairs into a single `enum` for middle/big size applications.

It's always a good practice from architectural standpoint to split those into multiple `enum`s.

```python
import os
from typing import Annotated

from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import AnnotatedConfigData, ConfigStore


class MyInitialBaseConfEnum(BasicConfigEnum):
   KEY_1: Annotated[str, AnnotatedConfigData(
      default=3.1415,
      type=float
   )] = "MY_KEY_1"

   KEY_2: Annotated[str, AnnotatedConfigData(
      default=15,
      type=float
   )] = "MY_KEY_2"


class AnotherModuleBaseConfEnum(BasicConfigEnum):
   KEY_3 = "MY_KEY_3"
   KEY_4 = "MY_KEY_4"

   USER_NAME: Annotated[str, AnnotatedConfigData(
      default="-- no user name found --",
      type=str
   )] = "USER"


conf = ConfigHub.aggregate(
   # Config number 1
   {
      AnotherModuleBaseConfEnum.KEY_4: "Non Empty Value",
      "NON_ALLOWED_KEY": 42,
   },

   # Config number 2
   {
      MyInitialBaseConfEnum.KEY_2: True,
   },

   # Config number 3
   # Taking EnvVars from OS, though anything not in target config - will be filtered out
   os.environ,

   # Config number 0
   # Target config is always number 0
   target=ConfigStore(
      
      # Here we create combined config from those enums
      MyInitialBaseConfEnum.target_config() + AnotherModuleBaseConfEnum.target_config(),
      
      # And then we wrap that combined default config from multiple enums
      # into the target one with preprocessor and filter
      preprocessor=simputils_pp,
      filter=True
   ),
)

print("conf: ", conf)
```

Output:
```text
conf:  {
    'MY_KEY_1': 3.1415, 
    'MY_KEY_2': True, 
    'MY_KEY_3': None, 
    'MY_KEY_4': 'Non Empty Value', 
    'USER': 'ivan'
}
```

It works exactly like previous example with a single `enum`.

> [!IMPORTANT]
> It's very important that you specify `preprocessor` and `filter` on the wrapping `ConfigStore`!
> If you specify those on `target_config()` methods of `enum`s, it will not work as expected,
> and all the following configs will not get processed through them!