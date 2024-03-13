from abc import ABCMeta, abstractmethod

from simputils.config.models import ConfigStore


class BasicConditional(metaclass=ABCMeta):

    @abstractmethod
    def condition(self, target: ConfigStore):
        pass  # pragma: no cover

    def __call__(self, target: ConfigStore, *args, **kwargs):
        return self.condition(target)
