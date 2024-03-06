# Pydantic Integration

There is a possibility to use [pydantic](https://docs.pydantic.dev/latest/) models
natively in combination with Configs.

This functionality make sense the most with `YAML` and `JSON` files or dictionaries as source 
due to their multidimensional nature.

The easiest way to use `pydantic` models is 
through [Config Enums with Annotations](working-with-enums-and-annotations.md).

In simple - you just specify your model classes as `type` argument to annotations of Config Enum.

> [!IMPORTANT]
> To use this functionality, make sure you installed `pydantic` pip package,
> it is not part of the dependencies of SimpUtils Config library!

Example:

```python
from typing import Annotated

from pydantic import BaseModel

from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore, AnnotatedConfigData


class MyModelThird(BaseModel):
    city: str = "Vienna"
    country: str = "Austria"


class MyModelSecond(BaseModel):
    address: str = "Totoro Street 666"
    phone: str = "666666"
    other: MyModelThird | None = None


class MyModelFirst(BaseModel):
    name: str = "My First Name"
    age: int = 34
    other: MyModelSecond | None = None


class MyConfigEnum(BasicConfigEnum):
    MY_MODEL_1: Annotated[str, AnnotatedConfigData(
        type=MyModelFirst | None,
    )] = "my_model_1"

    MY_MODEL_2: Annotated[str, AnnotatedConfigData(
        type=MyModelFirst | None,
    )] = "my_model_2"

    MY_MODEL_3: Annotated[str, AnnotatedConfigData(
        type=MyModelFirst | None,
    )] = "my_model_3"


conf: ConfigStore = ConfigHub.aggregate(
    {
        "my_model_1": {
            "name": "Ivan PandaHugMonster",
            "age": 201,
            "other": {
                "address": "Something Something Street",
                "phone": "42",
                "other": {
                    "country": "Canada",
                    "city": "Toronto"
                }
            }
        }
    },

    target=ConfigStore(
        MyConfigEnum,
    )
)
print(conf[MyConfigEnum.MY_MODEL_1])

```

> [!NOTE]
> Additionally it makes sense to use the `pydantic` functionality 
> in combination with [Config Object Style Access](config-object-style-access.md)

