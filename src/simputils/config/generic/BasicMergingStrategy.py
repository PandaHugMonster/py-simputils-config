from abc import ABCMeta, abstractmethod
from typing import Callable

from simputils.config.components.simpletons import NotExisting
from simputils.config.types import ConfigType


class BasicMergingStrategy(metaclass=ABCMeta):

    # noinspection PyShadowingBuiltins
    def apply_data(self, target, config: ConfigType, preprocessor: Callable, filter: Callable):
        applied_keys = []
        storage_result = {}
        for key, val_incoming in dict(config).items():
            key, val_incoming = preprocessor(key, val_incoming)
            if filter(key, val_incoming):
                applied_keys.append(key)
                val_target = NotExisting()
                if key in target:
                    val_target = target.get(key)
                storage_result[key] = self.merge(key, val_target, val_incoming)

        return storage_result, applied_keys

    @abstractmethod
    def merge(self, key, val_target, val_incoming):  # pragma: no cover
        pass
