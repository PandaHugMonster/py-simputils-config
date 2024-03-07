from abc import ABCMeta, abstractmethod
from typing import Callable

from simputils.config.types import ConfigType


class BasicMergingStrategy(metaclass=ABCMeta):

    # noinspection PyShadowingBuiltins
    def apply_data(self, config: ConfigType, preprocessor: Callable, filter: Callable):
        applied_keys = []
        storage_result = {}
        for key, val in dict(config).items():
            key, val = preprocessor(key, val)
            if filter(key, val):
                applied_keys.append(key)
                storage_result[key] = self.merge(key, storage_result.get(key), val)

        return storage_result, applied_keys

    @abstractmethod
    def merge(self, key, val_target, val_incoming):  # pragma: no cover
        pass
