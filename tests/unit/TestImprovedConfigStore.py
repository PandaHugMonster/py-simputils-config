from simputils.config.components import ConfigHub
from simputils.config.generic import BasicConfigEnum
from simputils.config.generic.BasicConditional import BasicConditional
from simputils.config.models import ConfigStore


class TestImprovedConfigStore:

    def test_conditional_aggregation(self):
        exp_str = "I'm very very old now ^_^"

        class MyConfigEnum(BasicConfigEnum):
            VAL1 = "val1"
            VAL2 = "val2"
            VAL3 = "val3"

        def _conditional_config(target: ConfigStore):
            if target[MyConfigEnum.VAL2] >= 34:
                return {MyConfigEnum.VAL1: exp_str}

        default_conf_dict = {
            MyConfigEnum.VAL1: "Test",
            MyConfigEnum.VAL2: 34,
            MyConfigEnum.VAL3: True,
        }

        conf = ConfigHub.aggregate(
            default_conf_dict,

            _conditional_config,

            target=ConfigStore(
                MyConfigEnum,
                strict_keys=True
            )
        )
        assert conf[MyConfigEnum.VAL2] >= 34 and conf[MyConfigEnum.VAL1] == exp_str

        conf = ConfigHub.aggregate(
            default_conf_dict,
            {
                MyConfigEnum.VAL2: 33
            },

            _conditional_config,

            target=ConfigStore(
                MyConfigEnum,
                strict_keys=True
            )
        )
        assert conf[MyConfigEnum.VAL2] < 34 and conf[MyConfigEnum.VAL1] == "Test"

    def test_conditional_aggregation_with_class(self):
        exp_str = "I'm very very old now ^_^"

        class MyConfigEnum(BasicConfigEnum):
            VAL1 = "val1"
            VAL2 = "val2"
            VAL3 = "val3"

        class MyConditional(BasicConditional):
            def condition(self, target: ConfigStore):
                if target[MyConfigEnum.VAL2] >= 34:
                    return {MyConfigEnum.VAL1: exp_str}

        default_conf_dict = {
            MyConfigEnum.VAL1: "Test",
            MyConfigEnum.VAL2: 34,
            MyConfigEnum.VAL3: True,
        }

        conf = ConfigHub.aggregate(
            default_conf_dict,

            MyConditional(),

            target=ConfigStore(
                MyConfigEnum,
                strict_keys=True
            )
        )
        assert conf[MyConfigEnum.VAL2] >= 34 and conf[MyConfigEnum.VAL1] == exp_str

        conf = ConfigHub.aggregate(
            default_conf_dict,
            {
                MyConfigEnum.VAL2: 33
            },

            MyConditional(),

            target=ConfigStore(
                MyConfigEnum,
                strict_keys=True
            )
        )
        assert conf[MyConfigEnum.VAL2] < 34 and conf[MyConfigEnum.VAL1] == "Test"
