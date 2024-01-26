## Working with `ConfigStore`

`ConfigStore` stores the state of the config in form of key-value pairs.
But besides that, it contains some additional meta-data and normalization functionality
that is being essential for refactoring and general operation.

### Basics

Let's create our custom config and check how it looks like:
```python
from simputils.config.models import ConfigStore

conf = ConfigStore(
    {"VAL1": "My Val 1", "VAL2": True},
    name="My very special config",
    type="MY-type",
    source="knowhere",
)

print(conf, conf.applied_confs)
```

Output:
```text
{
    'VAL1': 'My Val 1', 
    'VAL2': True
}

[
    AppliedConf(
        applied_keys=['VAL1', 'VAL2'], 
        type='MY-type', 
        name='My very special config', 
        source='knowhere', 
        handler=None, 
        ref={'VAL1': 'My Val 1', 'VAL2': True}
    )
]
```

Now let's create another config with some normalization/preprocessing:
```python
from simputils.config.models import ConfigStore

conf = ConfigStore(
    {"VAL1": "My Val 1", "VAL2": True},
    preprocessor={
        "VAL1": "new-val-1",
    }
)

print(conf, conf.applied_confs)
```

```text
{
    'new-val-1': 'My Val 1', 
    'VAL2': True
} 
[
    AppliedConf(
        applied_keys=['new-val-1', 'VAL2'], 
        type='dict', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'VAL1': 'My Val 1', 'VAL2': True}
    )
]
```
As you can see the key `VAL1` was replaced with `new-val-1`, while `VAL2` is intact.
Besides dict keys mapping, you can provide callable/lambda into `preprocessor` param, 
and fully customize preprocessing.

Now, let's extend our previous example and add `filter` parameter:
```python
from simputils.config.models import ConfigStore

conf = ConfigStore(
    {"VAL1": "My Val 1", "VAL2": True, "VAL3": "my val 3"},
    preprocessor={
        "VAL1": "new-val-1",
    },
    filter=[
        "new-val-1", "VAL3"
    ]
)

print(conf, conf.applied_confs)
```

```text
{
    'new-val-1': 'My Val 1', 
    'VAL3': 'my val 3'
}
[
    AppliedConf(
        applied_keys=['new-val-1', 'VAL3'], 
        type='dict', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'VAL1': 'My Val 1', 'VAL2': True, 'VAL3': 'my val 3'}
    )
]
```

And here only permitted `new-val-1` and `VAL3` were included into the config.
It works with callable/lambda instead of list as well.

### Chain-Inclusion

Sometimes it's necessary to chain multiple `ConfigStore`.
For example to add some multi-stage filtering/preprocessing or for other purposes.

```python
from simputils.config.models import ConfigStore

conf_1 = ConfigStore(
	{"VAL1": "My val 1"},
    name="My conf 1",
    type="My type 1",
    source="My source 1",
)
conf_2 = ConfigStore(
    {"VAL2": "My val 2"},
    name="My conf 2",
    type="My type 2",
    source="My source 2",
)
conf_3 = ConfigStore(
    {"VAL3": "My val 3"},
    name="My conf 3",
    type="My type 3",
    source="My source 3",
)

# Order matters here!
conf_2.config_apply(conf_3)
conf_1.config_apply(conf_2)

print(conf_1, conf_1.applied_confs)
```

```text
{
    'VAL1': 'My val 1', 
    'VAL2': 'My val 2', 
    'VAL3': 'My val 3'
}
[
    AppliedConf(
        applied_keys=['VAL1'], 
        type='My type 1', 
        name='My conf 1', 
        source='My source 1', 
        handler=None, 
        ref={'VAL1': 'My val 1'}
    ), 
    AppliedConf(
        applied_keys=['VAL2', 'VAL3'], 
        type='My type 2', 
        name='My conf 2', 
        source='My source 2', 
        handler=None, 
        ref={'VAL2': 'My val 2', 'VAL3': 'My val 3'}
    )
]
```

As you can see, that 3 daisy-chained confs resulting into only 2 `AppliedConf`s.
It's due to way the inclusion is happening.

When you have 2 `ConfigStore`s, and the second one is included into first one,
meta-data of the second will persist only in `AppliedConf` after merge. 
Because only key-values are transferred without binding to the original object.

And when you have multiple chained `ConfigStore`s, for example 3 - 
the third config's data is transferred to the second one, 
but meta-data is stored in the second's history of `AppliedConf`s,
which during the merge into the first conf is not persisting.

> [!NOTE]
> `AppliedConf` are not transferred to the target `ConfigStore` from the included `ConfigStore`.
> (at least for now)


### Additional operations

Because `ConfigStore` is like a dictionary, you can do some interesting operations with it
as with a dictionary

#### Summation of confs

It works differently than the Chain-Inclusion!

```python
from simputils.config.models import ConfigStore

conf_1 = ConfigStore({"VAL1": "My val 1"}, name="My conf 1")
conf_2 = ConfigStore({"VAL2": "My val 2"}, name="My conf 2")
conf_3 = ConfigStore({"VAL3": "My val 3"}, name="My conf 3")


conf = conf_1 + conf_2 + conf_3

print(conf, conf.applied_confs)
```

```text
{
    'VAL1': 'My val 1', 
    'VAL2': 'My val 2', 
    'VAL3': 'My val 3'
}
[
    AppliedConf(
        applied_keys=['VAL1'], 
        type='dict', 
        name='My conf 1', 
        source=None, 
        handler=None, 
        ref={'VAL1': 'My val 1'}
    ), 
    AppliedConf(
        applied_keys=['VAL2'], 
        type='ConfigStore', 
        name='My conf 2', 
        source=None, 
        handler=None, 
        ref={'VAL2': 'My val 2'}
    ), 
    AppliedConf(
        applied_keys=['VAL3'], 
        type='ConfigStore', 
        name='My conf 3', 
        source=None, 
        handler=None, 
        ref={'VAL3': 'My val 3'}
    )
]
```

So, as you can see it does not work like a daisy-chaining, 
but rather takes the first `ConfigStore` and applies all others on it.

The same could be done with simple dictionaries if the first value is `ConfigStore`.
```python
from simputils.config.models import ConfigStore

# Important that the first value is the `ConfigStore` object!
conf = ConfigStore({"VAL1": "My val 1"}, name="My conf 1") \
       + {"VAL2": "My val 2"} \
       + {"VAL3": "My val 3"}
    
print(conf, conf.applied_confs)
```

```text
{
    'VAL1': 'My val 1', 
    'VAL2': 'My val 2', 
    'VAL3': 'My val 3'
}
[
    AppliedConf(
        applied_keys=['VAL1'], 
        type='dict', 
        name='My conf 1', 
        source=None, 
        handler=None, 
        ref={'VAL1': 'My val 1'}
    ), 
    AppliedConf(
        applied_keys=['VAL2'], 
        type='dict', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'VAL2': 'My val 2'}
    ), 
    AppliedConf(
        applied_keys=['VAL3'], 
        type='dict', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'VAL3': 'My val 3'}
    )
]
```

#### `update()` method

It works the same way as summation
```python
from simputils.config.models import ConfigStore

conf = ConfigStore({"VAL1": "My val 1"}, name="My conf 1")

conf.update({"VAL2": "My val 2"})
conf.update({"VAL3": "My val 3"})
    
print(conf, conf.applied_confs)
```

```text
{
    'VAL1': 'My val 1', 
    'VAL2': 'My val 2', 
    'VAL3': 'My val 3'
}
[
    AppliedConf(
        applied_keys=['VAL1'], 
        type='dict', 
        name='My conf 1', 
        source=None, 
        handler=None, 
        ref={'VAL1': 'My val 1'}
    ),
    AppliedConf(
        applied_keys=['VAL2'],
        type='dict',
        name=None,
        source=None, 
        handler=None, 
        ref={'VAL2': 'My val 2'}
    ),
    AppliedConf(
        applied_keys=['VAL3'],
        type='dict', 
        name=None, 
        source=None, 
        handler=None, 
        ref={'VAL3': 'My val 3'}
    )
]
```
