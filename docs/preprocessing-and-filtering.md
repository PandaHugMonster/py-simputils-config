# Preprocessing and filtering

## Preprocessing

> [!NOTE]
> Enums type casting is not covered here, for more info about that please refer to
> [Single enum target config](working-with-enums-and-annotations.md#single-enum-target-config)

Preprocessors are callables that perform modification on keys and/or values 
or do not modify those at all.

Preprocessor can be specified through `preprocessor` param of `CoreConfig()`.
Preprocessor callable will receive just 2 params: `key`, `value`.
And it must return tuple of `key`, `value` (modified or not).
You always can write your own preprocessor class or function/lambda. 
Just make sure it's callable.

`dict` or `list` can be provided to this param, where:
* `dict` will map and replace old key with a new one, 
  for example `{"OLD_KEY": "NEW_KEY"}` as a preprocessor will turn
  incoming data of `{"OLD_KEY": "My old key value", "ANOTHER_KEY": "Blah blah blah"}`
  into `{"NEW_KEY": "My old key value", "ANOTHER_KEY": "Blah blah blah"}`
* `list` must be a list of callables that will sequentially be applied to the incoming
  data

There a few classes of simputils preprocessing:
* `simputils.config.components.preprocessors.SimputilsStandardPreprocessor` - normalizes keys only
* `simputils.config.components.preprocessors.SimputilsCastingPreprocessor` - auto-cast some string values only

and a few shortcut functions for those classes:
* `simputils.config.base.simputils_pp()` for `SimputilsStandardPreprocessor`
* `simputils.config.base.simputils_cast()` for `SimputilsCastingPreprocessor`
* `simputils.config.base.simputils_pp_with_cast()` applies both `simputils_pp()` and `simputils_cast()` sequentially.

`SimputilsStandardPreprocessor` turns incoming key to EnvVar format of keys, like "my Key" -> "MY_KEY".
It replaces all non-alphanumeric symbols to underscores, and turn to upper case the whole string.
It does not affect values whatsoever.

`SimputilsCastingPreprocessor` preprocesses only values and only strings.
It basically searches certain values and changes the type of them for `bool`, `int`, `float` and `None` strings.
For the exact logic and values please refer to the logic of `SimputilsCastingPreprocessor` (it's very simple one).

Example:
```python
from simputils.config.base import simputils_pp_with_cast
from simputils.config.models import ConfigStore

conf = ConfigStore(
    {
        "my key #1": "My first key",
        "my key 2": "0.0",
        "my KEy 3": "yes",
    },
    preprocessor=simputils_pp_with_cast,
)
print(conf)
```

Output:
```text
{
    'MY_KEY_1': 'My first key',
    'MY_KEY_2': 0.0,
    'MY_KEY_3': True
}
```

> [!WARNING]
> Empty string with `simputils.config.components.preprocessors.SimputilsCastingPreprocessor` will be considered `None`

If you desire to slightly adjust behaviour of
the `simputils.config.components.preprocessors.SimputilsCastingPreprocessor`,
you might want to redefine static fields of `simputils.config.components.preprocessors.SimputilsCastingPreprocessor`
with lists `list_yes`, `list_no`, `list_none` to your taste.



## Filtering

Filtering allows to filter out certain key or values based on `callable` or `list` of keys.

Filters can be specified through `filter` param of `CoreConfig()`.

Additionally `True` can be specified to the `filter` param instead of `callable` or `list`.
In this case the keys of the initial (first) dictionary will become a reference for the filter.

> [!NOTE]
> It is highly recommended to always specify filter, at least to `True` or your own logic.
> 
> It's not a good practice to dump into config everything without some control.

Example with certain keys:
```python
from simputils.config.models import ConfigStore

conf = ConfigStore(
	{
        "KEY_1": "My first key",
        "KEY_2": "My second key",
        "KEY_3": "My third key",
    },
    filter=["KEY_1", "KEY_3"]
)
print(conf)
```

Output:
```text
{
    'KEY_1': 'My first key', 
    'KEY_3': 'My third key'
}
```

Example with `True`:
```python
from simputils.config.models import ConfigStore

conf = ConfigStore(
    {
        "KEY_1": "My first key",
        "KEY_2": "My second key",
        "KEY_3": "My third key",
    },
    filter=True
)
conf.config_apply({
    "SKIPPED_KEY_1": "This key 1 will be filtered out",
    "SKIPPED_KEY_2": "This key 2 will be filtered out",
    "KEY_3": "This key 3 will replace previous one",
})
print(conf)
```

Output:
```text
{
    'KEY_1': 'My first key', 
    'KEY_2': 'My second key', 
    'KEY_3': 'This key 3 will replace previous one'
}
```

