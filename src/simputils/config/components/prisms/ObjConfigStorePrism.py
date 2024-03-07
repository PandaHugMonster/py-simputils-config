import inspect
from typing import Any

from simputils.config.enums import ConfigStoreType
from simputils.config.exceptions import StrictKeysEnabled


class ObjConfigStorePrism:  # pragma: no cover
    # MARK  No Cover might be temporary here

    _config_store = None

    @property
    def applied_confs(self):
        return self._config_store.applied_confs

    def __init__(self, config_store):
        self._config_store = config_store

    def __getattr__(self, item):
        return self._config_store.get(item)

    def __setattr__(self, key, value):
        if key not in ("_config_store", ) and key not in self.__dict__:
            self._config_store[key] = value
        else:
            self.__dict__[key] = value

    def __setitem__(self, key, value):
        preprocessor = self._config_store._preprocessor
        key, _ = preprocessor(key, None)

        if self._config_store._strict_keys and key not in self._config_store:
            raise StrictKeysEnabled(
                f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown")

        frame_context = inspect.stack()[1][0]
        frame_info = inspect.getframeinfo(frame_context)

        self._config_store.config_apply(
            {key: value},
            f"{frame_info.function}:{frame_info.lineno}",
            frame_info.filename,
            ConfigStoreType.SINGLE_VALUE
        )

    def __add__(self, other):  # pragma: no cover
        if self._config_store._strict_keys:
            for key in other:
                preprocessor = self._config_store._preprocessor
                key, _ = preprocessor(key, None)
                if key not in self._config_store:
                    raise StrictKeysEnabled(
                        f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown"
                    )
        return self._config_store.config_apply(other)

    def __repr__(self):  # pragma: no cover
        return repr(self._config_store)

    def __len__(self):  # pragma: no cover
        return len(self._config_store)

    def __delitem__(self, key):  # pragma: no cover
        del self._config_store[key]

    def __getitem__(self, key):
        preprocessor = self._config_store._preprocessor
        key, _ = preprocessor(key, None)

        if self._config_store._strict_keys and key not in self._config_store:
            raise StrictKeysEnabled(
                f"Strict Keys mode enabled. Only initial set of keys allowed. Key \"{key}\" is unknown"
            )

        return self._config_store.get(key)

    def __cmp__(self, other):  # pragma: no cover
        return self._config_store == other

    def __contains__(self, item):  # pragma: no cover
        return item in self._config_store

    def __iter__(self):  # pragma: no cover
        return iter(self._config_store)

    def __str__(self):  # pragma: no cover
        return str(self._config_store)

    def items(self) -> tuple[str, Any]:
        return self._config_store.items()

    def keys(self) -> tuple[str]:
        return self._config_store.keys()

    def values(self) -> tuple[Any]:
        return self._config_store.values()
