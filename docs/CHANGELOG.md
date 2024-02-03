# Changelog


## 1.0.4
* Improved `Enum` usage with configs #13
  * Documentation here [working-with-enums-and-annotations.md](working-with-enums-and-annotations.md)

## 1.0.3
* Added `simputils.config.generic.BasicConfigEnum.get_annotation_for()` class method
* Added initial documentation about `Enum` 
  usage [working-with-enums-and-annotations.md](working-with-enums-and-annotations.md)
* Improved some documentation [../README.md](../README.md)
* Added automated tests for `Enum` annotations in `tests.unit.TestConfigStore`

## 1.0.2
* Improved type hints and fixed typing in general in the code.
  * This python module for reference `simputils.config.types`
* Extracted basic functionality from `simputils.config.models.ConfigStore` to 
  `simputils.config.generic.BasicConfigStore` in fully backward-compatible way
* Extracted basic fields from `simputils.config.models.AppliedConf` to 
  `simputils.config.generic.BasicAppliedConf` in fully backward-compatible way
* Improved some of `simputils.config.generic.BasicConfigStore` functionality
* Added `ARGPARSER_NAMESPACE` key to `src.simputils.config.enums.ConfigStoreType`
* Some general code cleanups and code format improvement
* Improved some documentation [../README.md](../README.md)
* `Enum` support added:
  * Added abstract `simputils.config.generic.BasicConfigEnum` class
  * Added `simputils.config.models.AnnotatedConfigData` annotation class for enums
  * For documentation about this feature refer 
    to [working-with-enums-and-annotations.md](working-with-enums-and-annotations.md)

## 1.0.1
* Some tini-tiny improvements

## 1.0.0 (Initial)
* Added support of:
  * `pytest`
  * `flake8`
* Implemented:
  * `simputils.config.base` utils
  * `simputils.config.components.ConfigHub` static class
  * `simputils.config.components.handlers.DotEnvFileHandler` DotEnv support
  * `simputils.config.components.handlers.JsonFileHandler` JSON support
  * `simputils.config.components.handlers.YamlFileHandler` YAML support
  * `simputils.config.enums.ConfigStoreType` enum for config source types
  * Different exception types in `simputils.config.exceptions`
  * `simputils.config.generic.BasicFileHandler` to create custom file-handlers
  * `simputils.config.models.AppliedConf` model to store history of the applied configs
  * `simputils.config.models.ConfigStore` model to store config (foundation code of the library)
  * Almost full test-coverage
* Added some documentation:
  * [README.md](../README.md)
  * [docs/overall-example.md](overall-example.md)
  * [docs/working-with-config-store.md](working-with-config-store.md)
* Added `docs/overall-example.md` documentation
