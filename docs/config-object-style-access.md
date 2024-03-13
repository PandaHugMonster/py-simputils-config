# Config Object Style Access

> [!NOTE]
> "Object Style Access", "Dot-notation Access" or "Object Style Notation" 
> in this project refers to accessing content of "Dictionary-Alike" through object field/property.

When you create an instance/object of `ConfiStore`, despite it being an object,
you still have to access key/value pairs through "Dict-Alike" notation. 
This is designed like that on purpose, because depending on architecture of your project,
the "Object Style Access" might cause issues either to your code, or worse - to your architecture.

But, to provide tools for all other cases when you'd prefer to use "Object Style Access",
the `simputils.config.components.prisms.ObjConfigStorePrism` prism was implemented.

> [!NOTE]
> Concept of `Prism` was introduced in PHP "SimpUtils" project as sort of "Gateway" or "Interface"
> to the original object. It means when you create/get `Prism` of certain sort for the object,
> the `Prism` itself does not contain any real data, but stores reference to the target object
> and provides additional functionality, that affects the target object.
> For example: You try to modify `Prism` object, but in fact it modifies the underlying target object,
> or you are getting value from a `Prism` and it gets the value first from the target object, and then
> returns it. It's essentially ephemeral.

Why might you prefer to use "Object Style Access"?! Due to some very important benefits:
1. IDE Auto-Completion would improve your code quality.
2. IDE inspection highlights and other static analysis tools.
3. Reduction of unnecessary imports from your "Config-Enums" (fewer imports - less coupling).
4. Prisms customization is separated from the `ConfigStore` 
   which can improve architecture in some cases.

> [!NOTE]
> Best practise for this project is to use "Object Style Access", but it's up to you
> if it really fits your needs.

Though prisms do not require using "Enum Configs", it is considered 
a good practise generally for this project.

In short, to get "Object Style Access" config prism, just use `obj` property of `ConfigStore`
```python
from simputils.config.models import ConfigStore
conf = ConfigStore({
   "field1": "value1",
   "field2": "value2",
   "field3": "value3",
})

conf_obj = conf.obj

# "Object Style Access" or "Dot-notation Access"
print(conf_obj.field2)
```

For the most part this object will behave identically to `ConfigStore` object.

## How to use it (primitive variant)

> [!IMPORTANT]
> This is a very brief and quite crude example, it's only for demonstration, 
> more info and examples will be added to best-practises documentation later on.

Example:

```python
from simputils.config.components import ConfigHub
from simputils.config.components.prisms import ObjConfigStorePrism
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore


# Creating Enum Config
class MyConfigEnum(BasicConfigEnum):
   VAL1 = "val1"
   VAL2 = "val2"
   VAL3 = "val3"


# Creating "Object Style Access" hints
class _Hints(ObjConfigStorePrism):
   val1: str = ...
   val2: int = ...
   val3: bool = ...


# The class itself should not be used directly for type hints, so we
# create the new type for this case based on our _Hints class
MyConfigType = type[_Hints]

if __name__ == "__main__":
   # Type-hint here will let our IDE provide autocompletion for developers
   conf: MyConfigType = ConfigHub.aggregate(
      {
         "val1": "test",
         "val2": 34,
         "val3": True,
      },
      target=ConfigStore(
         MyConfigEnum,
         strict_keys=True,
      ),
   ).obj
   
   # These will behave identically to `ConfigStore`
   print(conf, conf.applied_confs)
   
   # Accessing our keys in object-style
   print(conf.val1, conf.val2, conf.val3)
```

In this way the IDE hints and autocompletion should work on `conf` as expected.