# Changelog

## 1.1.0

* Added `names()` class method to `simputils.config.generic.BasicConfigEnum`
* Decreased acceptable Cyclomatic Complexity level 
  from 10 to 5 in the project (for better code quality control)
* Removed unnecessary dependency of `typing_extensions`
* Ticket https://github.com/PandaHugMonster/py-simputils-config/issues/21
  * Implemented flag and functionality for strict set of keys
    * If enabled, and unknown key is accessed the `simputils.config.exceptions.StrictKeysEnabled` exception
      is raised
  * Fixed a small bug with some minimal preprocessing when getting value by the "key". 
    Now all the provided keys are passing the `preprocessor` to conform with the rules.
* Ticket https://github.com/PandaHugMonster/py-simputils-config/issues/29
  * Added document [Working with ConfigHub](working-with-config-hub.md)
  * Implemented "Conditional Config", callables for `ConfigHub.aggregate()`
    * Documentation can be found here: [Working with ConfigHub](working-with-config-hub.md#conditional-config)
    * Simple support for `ExecEnv` aka "Stage" through "Conditional Config"
* Ticket https://github.com/PandaHugMonster/py-simputils-config/issues/20
  * Implemented `simputils.config.components.prisms.ObjConfigStorePrism` for `ConfigStore`.
    It allows to use "Config Object Style Access" for accessing key/value pairs through `obj` field of `ConfigStore` object.
  * And documentation for it: [Config Object Style Access](config-object-style-access.md)
* Ticket https://github.com/PandaHugMonster/py-simputils-config/issues/32
  * Improved compatibility with [pydantic](https://docs.pydantic.dev/latest/) models
    * Now pydantic models can be used as `type` for Enum Config annotations, then the structures
      will be converted accordingly. Useful especially with "Config Object Style Access" aka `ConfigStore.obj`
    * Documentation can be found here: [Pydantic Integration](pydantic-integration.md)
  * Implemented proper `type` processing of union types for Config Enum annotations
* Ticket https://github.com/PandaHugMonster/py-simputils-config/issues/25
  * Prepared documentation and schemes for all strategies: [Config Merging Strategies](config-merging-strategies.md)
  * Polished the concept of Merging Strategies (see schemes in [schemes/images](schemes/images))
  * Implemented general Merging Strategies infrastructure
  * "Implemented" Flat Strategy (teeny-tiny class of couple lines)
* Ticket https://github.com/PandaHugMonster/py-simputils-config/issues/23
  * Implemented Recursive Merging Strategy `simputils.config.components.strategies.MergingStrategyRecursive`
    * With params to **replace lists** (default) or **extend lists**
    * Recursive merge of objects like "pydantic models" is supported
    * Recursive merge of other objects is supported (like `dataclasses`, etc.) but might not
      be fully out of the box working as expected
  * Added additional unit-tests (for combination of recursive merging strategy and pydantic integration)
  * Updated documentation about Merging Strategies in general, and about Recursive Merging Strategy
    * Can be found here: [Config Merging Strategies](config-merging-strategies.md)



## 1.0.5
* Fixed missing dependency of `typing_extensions`


## 1.0.4
* Improved `Enum` usage with configs #13
  * Documentation here [working-with-enums-and-annotations.md](working-with-enums-and-annotations.md)
  * Implemented `simputils.config.base.get_enum_defaults()`
    method to get default values form `Enum` class
  * Implemented `simputils.config.base.get_enum_annotation_for()` 
    method to get specific annotation for specific key of `Enum`
  * Implemented `simputils.config.base.get_enum_all_annotations()` 
    method to get all available annotations of `Enum`
  * Added `ENUM` key to `simputils.config.enums.ConfigStoreType`
  * Implemented `simputils.config.generic.BasicConfigEnum.target_config()` shortcut
  * Added support of `Enum` class for `simputils.config.generic.BasicConfigStore`.
    So you can specify a raw class reference as a source of config
  * Added `type` field to `simputils.config.models.AnnotatedConfigData` for type casting
* Added disclaimer [Potential package collision 2024](disclaimers.md)
* Some more cleanups and small improvements
* Improved preprocessors infrastructure and added type auto-casting for strings #11
  * Improved `simputils.config.base.simputils_pp()` 
    function through class `simputils.config.components.preprocessors.SimputilsStandardPreprocessor`
  * Added `simputils.config.base.simputils_cast()` for auto-casting strings
  * Added `simputils.config.base.simputils_pp_with_cast()` for standard simputils key 
    normalization auto-casting strings
  * Implemented `simputils.config.components.preprocessors.SimputilsCastingPreprocessor` auto-casting preprocessor 
  * Implemented `simputils.config.components.preprocessors.SimputilsStandardPreprocessor` key normalization 
    (just code relocation from `simputils.config.base.simputils_pp()`)
  * Implemented `simputils.config.generic.BasicPreprocessor`
* Added documentation about preprocessing and filtering: 
  [Preprocessing and filtering](preprocessing-and-filtering.md)
* Now `list` or `tuple` with callables can be provided to the `preprocessor` param,
  which sequentially will be applied to incoming key-value pairs.

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
* Added `ARGPARSER_NAMESPACE` key to `simputils.config.enums.ConfigStoreType`
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
