import json
from typing import Annotated

import pytest
from pydantic import BaseModel

from fixtures import fixture_flat_strategy_default, fixture_recursive_strategy_list_replace, \
	fixture_recursive_strategy_list_merge, fixture_recursive_strategy_objects
from simputils.config.components import ConfigHub
from simputils.config.components.strategies import MergingStrategyFlat, MergingStrategyRecursive
from simputils.config.generic import BasicConfigEnum
from simputils.config.models import ConfigStore, AnnotatedConfigData


class TestMergingStrategies:

	@pytest.mark.parametrize(
		("expected", "args"),
		fixture_flat_strategy_default.data,
	)
	def test_flat_strategy_default(self, expected, args):
		strategy = MergingStrategyFlat()

		conf = ConfigHub.aggregate(
			*args,
			target=ConfigStore(
				strategy=strategy
			)
		)

		assert expected == dict(conf)

	@pytest.mark.parametrize(
		("expected", "args"),
		fixture_recursive_strategy_list_replace.data,
	)
	def test_recursive_strategy_list_replace(self, expected, args):
		strategy = MergingStrategyRecursive(list_extend=False)

		conf = ConfigHub.aggregate(
			*args,
			target=ConfigStore(
				strategy=strategy
			)
		)

		assert expected == dict(conf)

	@pytest.mark.parametrize(
		("expected", "args"),
		fixture_recursive_strategy_list_merge.data,
	)
	def test_recursive_strategy_list_merge(self, expected, args):
		strategy = MergingStrategyRecursive(list_extend=True)

		conf = ConfigHub.aggregate(
			*args,
			target=ConfigStore(
				strategy=strategy
			)
		)

		assert expected == dict(conf)

	@pytest.mark.parametrize(
		("expected", "args"),
		fixture_recursive_strategy_objects.data,
	)
	def test_recursive_strategy_object_merge(self, expected, args):
		ConfigStore._set_pydantic_enabled(True)

		strategy = MergingStrategyRecursive(list_extend=True)

		conf = ConfigHub.aggregate(
			*args,
			target=ConfigStore(
				fixture_recursive_strategy_objects.MyConfigEnum,
				strategy=strategy,
			)
		)

		assert expected == dict(conf)

	def test_recursive_strategy_object_from_files_sanity_check(self):
		ConfigStore._set_pydantic_enabled(True)

		class FavouriteObj(BaseModel):
			things: list = None
			drinks: list = None
			food: list = None

		class GeoObj(BaseModel):
			country: str = None
			city: str = None

		class AboutObj(BaseModel):
			name: str = None
			nickname: str = None
			age: int = None
			geo: GeoObj = None
			contacts: list = None
			favourite: FavouriteObj = None

		class MyConfigEnum(BasicConfigEnum):
			FIRST_PERSON: Annotated[str, AnnotatedConfigData(
				type=AboutObj
			)] = "first_person"

		strategy = MergingStrategyRecursive(list_extend=True)

		conf = ConfigHub.aggregate(
			"tests/data/recursive/main-config.yaml",
			"tests/data/recursive/main-config.local.yaml",
			"tests/data/recursive/adjustments.json",
			target=ConfigStore(
				MyConfigEnum,
				strategy=strategy,
			)
		)

		first_person: AboutObj = conf.obj.first_person
		# print(first_person.json())
		with open("tests/data/recursive/result.json", "r") as fd:
			expected = json.load(fd)
		assert dict(expected) == dict(json.loads(first_person.json()))

