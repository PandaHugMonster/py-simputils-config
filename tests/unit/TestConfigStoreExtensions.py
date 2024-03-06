from typing import Annotated

from pydantic import BaseModel

from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore, AnnotatedConfigData


class TestConfigStoreExtensions:

    def test_pydantic_integration(self):
        class MyModelThird(BaseModel):
            city: str = "Vienna"
            country: str = "Austria"

            def my(self):
                return f"{self.country}, {self.city}"

        class MyModelSecond(BaseModel):
            address: str = "Totoro Street 666"
            phone: str = "666666"
            other: MyModelThird | None = None

        class MyModelFirst(BaseModel):
            name: str = "My First Name"
            age: int = 34
            other: MyModelSecond | None = None

        class MyConfigEnum(BasicConfigEnum):
            MY_INT: Annotated[str, AnnotatedConfigData(
                type=int,
                default=33
            )] = "my_int"

            MY_MODEL_1: Annotated[str, AnnotatedConfigData(
                type=MyModelFirst,
                default={"name": "test"}
            )] = "my_model_1"

            MY_MODEL_2: Annotated[str, AnnotatedConfigData(
                type=MyModelFirst | None,
            )] = "my_model_2"

            MY_MODEL_3: Annotated[str, AnnotatedConfigData(
                type=MyModelFirst | None,
            )] = "my_model_3"
        #

        # NOTE  Checking default behaviour
        conf: ConfigStore = ConfigHub.aggregate(
            "data/pydantic-check.yml",

            target=ConfigStore(
                MyConfigEnum,
            )
        )
        model: MyModelFirst = conf[MyConfigEnum.MY_MODEL_1]
        assert model
        assert isinstance(model, MyModelFirst)

        # NOTE  Checking disabled pydantic
        ConfigStore._set_pydantic_enabled(False)
        assert ConfigStore._pydantic_base_model_class is None

        conf: ConfigStore = ConfigHub.aggregate(
            {
                "my_test_1": "value 1",
                "my_test_2": "value 2",
                "my_test_3": "value 3",
            },
        )
        value = conf["my_test_1"]
        assert value
        assert isinstance(value, str)
