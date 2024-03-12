import pytest

from fixtures import fixture_flat_strategy_default, fixture_recursive_strategy_list_replace, \
	fixture_recursive_strategy_list_merge, fixture_recursive_strategy_objects
from simputils.config.components import ConfigHub
from simputils.config.components.strategies import MergingStrategyFlat, MergingStrategyRecursive
from simputils.config.models import ConfigStore


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
		strategy = MergingStrategyRecursive(merge_lists=False)

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
		strategy = MergingStrategyRecursive(merge_lists=True)

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
	def test_recursive_strategy_list_merge(self, expected, args):
		ConfigStore._set_pydantic_enabled(True)

		strategy = MergingStrategyRecursive(merge_lists=True)

		conf = ConfigHub.aggregate(
			*args,
			target=ConfigStore(
				fixture_recursive_strategy_objects.MyConfigEnum,
				strategy=strategy,
			)
		)

		assert expected == dict(conf)
