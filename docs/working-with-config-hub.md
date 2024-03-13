# ConfigHub

The static class `simputils.config.components.ConfigHub` is the major helper to raw `ConfigStore`.

> [!NOTE]
> In the most cases it's highly recommended to use `ConfigHub` to 
> work with configs instead of manual `ConfigStore` object creation.
> 
> `ConfigHub` provides you with instances of `ConfigStore` that you can use further.


It has an essential method `ConfigHub.aggregate()` that can collect multiple different 
sources sequentially (and even conditionally) - apply them one after another.

The sources can be:
* Dictionaries
* String-Enums (aka "Config Enums") [Enums and Annotations](working-with-enums-and-annotations.md)
* Files
    * `string` path
    * `PathLike`
    * `IOBase` (any file-descriptors of this base class)
* `argparse` namespaces
* `ConfigStore` objects
* Callables
* "Empty" values (those then are ignored/skipped)

## How to use it

> [!IMPORTANT]
> Keep in mind that the order of the provided sources **matters**,
> because next argument has higher precedence than the previous one, 
> and the values of the previous one might be overwritten by the values 
> of the next one (if the same key exists)

### Simple usage

The usage of it is fairly simple, you just provide your "sources" as unnamed arguments:
```python
from simputils.config.components import ConfigHub

conf = ConfigHub.aggregate(
    "data/config-default.yml",
    "data/config-local.yml",
    {
        "val1": "My value 1",
        "val3": "My value 3",
    },
    {
        "val4": "My value 4",
    },
)

print(conf, conf.applied_confs)
```

What is important to highlight is that the very first `ConfigStore` object created in this aggregation
will become the resulting instance that is returned.

### Target Config Object

To improve flexibility it's suggested to provide `target` argument with `ConfigStore` 
instance of your own:

```python
from simputils.config.components import ConfigHub
from simputils.config.models import ConfigStore

conf = ConfigHub.aggregate(
    "data/config-default.yml",
    "data/config-local.yml",
    {
        "val1": "My value 1",
        "val3": "My value 3",
    },
    {
        "val4": "My value 4",
    },
    target=ConfigStore(
        {
            "I-Am": "Initial Config"
        }
    )
)

print(conf, conf.applied_confs)
```

Besides, you can provide additional "settings" for your target `ConfigStore` 
like `preprocessor`, `filter`, `strict_keys` and others.

### Preprocessor

Preprocessors allows to modify key or value before applying it to the `ConfigStore`.

In simple words, it's just a callable that modifies keys or values that are being applied to the config

> [!IMPORTANT]
> `preprocessor` callable will be applied for initial config data,
> but as well it would be applied to any new applying of key/value 
> that are set on the config.


```python
from simputils.config.base import simputils_pp
from simputils.config.components import ConfigHub
from simputils.config.models import ConfigStore

conf = ConfigHub.aggregate(
    "data/config-default.yml",
    "data/config-local.yml",
    {
        "val1": "My value 1",
        "val3": "My value 3",
    },
    {
        "val4": "My value 4",
    },
    target=ConfigStore(
        {
            "I-Am": "Initial Config"
        },
        preprocessor=simputils_pp
    )
)

print(conf, conf.applied_confs)
```

The project provides a few default preprocessors out of the box:
1. `simputils.config.base.simputils_pp` - Modifies keys to the common format of 
   "constants" like: `MY_KEY_NAME`, `I_AM`, etc.
   For more info refer to the preprocessor class: `simputils.config.components.preprocessors.SimputilsStandardPreprocessor`
2. `simputils.config.base.simputils_cast` - Modifies values trying to guess a type (if `string`)
   and casts it to the python type. For example `True` or `t` or `1` string would be cast into `bool(True)`
   For more info refer to the preprocessor class: `simputils.config.components.preprocessors.SimputilsCastingPreprocessor`
3. `simputils.config.base.simputils_pp_with_cast` - combination of both above


### Strict Keys

> [!NOTE]
> `strict_keys` will solidify initial key names, so it would not be possible to set
> those that not already present in this initial set of key names.

Very important when you use `strict_keys` to provide "prototype" or initial config into 
the target `ConfigStore`, you have to specify the initial config/keys 
to target config (as dict or Enum Config):

```python

from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore


class MyConfigEnum(BasicConfigEnum):
    VAL1 = "val1"
    VAL2 = "val2"
    VAL3 = "val3"
    VAL4 = "val4"


conf = ConfigHub.aggregate(
    {
        "val1": "My value 1",
        "val3": "My value 3",
    },
    {
        "val4": "My value 4",
    },
    target=ConfigStore(
        # Key names that are not compatible with this enum
        # will raise an exception!
        MyConfigEnum,

        strict_keys=True,
    )
)

print(conf, conf.applied_confs)
```

In this case if applied any non-existing in `MyConfigEnum` key,
the exception will be raised.

> [!NOTE]
> Using `strict_keys` is considered the best practice!


### Filter

`filter` argument allows to filter out anything that is not permitted.
It will do that for any assignment.

> [!IMPORTANT]
> There is a difference between "Conditional Config" and "Filter"
> 
> "Conditional Config" is happening once as a source for your config, it might add/override/modify values,
> but further assignments can override those that are set by the "Conditional Config".
> 
> While "Filter" is applied indefinitely and will not let any assignment that contradicts it
> during the lifetime of the instance of `ConfigStore`

Example:

```python
import os

from simputils.config.components import ConfigHub
from simputils.config.models import ConfigStore

conf = ConfigHub.aggregate(
    os.environ,
    target=ConfigStore(
        filter=lambda k, v: k in ["USER", "LANGUAGE", "SHELL"]
    ),
)

conf["GOO"] = "This one is filtered out"
conf["SHELL"] = "/ggbin/ggtest"

print(conf)
```

And output would be something like:
```python
{'LANGUAGE': 'en_US', 'SHELL': '/ggbin/ggtest', 'USER': 'ivan'}
```

As you can see all the non-compliant key/values from Environmental Variables and `GOO` are filtered out.


### Conditional Config

"Conditional Config" is just a callable that can be supplied into `ConfigHub.aggregate()` as a source,
and this callable should receive 1 argument `target` of `ConfigStore` type and return either None (skip)
or eligible source that `ConfigHub.aggregate()` supports (dict, string path, etc. except `callable`)


#### ExecEnv/EE aka Stage

Let's say you have "prod" stage specified in your main config file, 
and there is an optional "main-local" config file for the developer going second.

But for each stage there are additional config files, which should be loaded only if this stage is selected.

Here is the example how to implement it:
```python
import os

from simputils.config.components.prisms import ObjConfigStorePrism
from simputils.config.generic import BasicConfigEnum
from simputils.config.generic.BasicConditional import BasicConditional
from simputils.config.models import ConfigStore
from simputils.config.components import ConfigHub


class MyConfigEnum(BasicConfigEnum):
    EE = "ee"
    VAL1 = "val1"
    VAL2 = "val2"
    VAL3 = "val3"

    
class MyConditionalEE(BasicConditional):

    EE_PROD = "prod"
    EE_DEMO = "demo"
    EE_DEV = "dev"

    EE_PROD_LOCAL = f"{EE_PROD}-local"
    EE_DEMO_LOCAL = f"{EE_DEMO}-local"
    EE_DEV_LOCAL = f"{EE_DEV}-local"

    def condition(self, target: ConfigStore):
        return f"data/ee/config-{target[MyConfigEnum.EE]}.yml"

if __name__ == "__main__":
    conf = ConfigHub.aggregate(

        # Main config should go first. This config suppose to be part of the repo
        "data/config-main.yml",

        # Local-development config, should not be put in git/repo, but created
        # by each developer manually to override values from the main config.
        # File existence is optional, if does not exist, it will be ignored.
        "data/config-main-local.yml",

        # Conditional stage files `data/ee/config-{prod,demo,dev}.yml` can/should be part of the repo,
        # but `data/ee/config-{prod,demo,dev}-local.yml` files should not be put into the repo, but created
        # manually by each developer when necessary.
        MyConditionalEE(),
    )

    print(conf)
```

This example is avery primitive but effective way to add conditional logic
based on the EE/Stage and Local development.
