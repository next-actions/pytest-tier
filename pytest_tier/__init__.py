from __future__ import annotations

import pytest

TierStashKey = pytest.StashKey[list[int]]()


class TierPlugin(object):
    def __init__(self, config: pytest.Config) -> None:
        self.filter: list[int] = [int(x) for x in config.getoption("tier")]

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, config: pytest.Config, items: list[pytest.Item]) -> None:
        """
        Filter collected items and deselect these that do not match the tier filter.

        :meta private:
        """
        selected = []
        deselected = []

        for item in items:
            tiers: list[int] = []
            item.stash[TierStashKey] = tiers
            for mark in item.iter_markers("tier"):
                if len(mark.args) != 1:
                    raise ValueError("@pytest.mark.tier has more that one arguments")

                if type(mark.args[0]) != int:
                    raise ValueError("@pytest.mark.tier has non-integer argument")

                tiers.append(mark.args[0])

            tiers.sort()

            if not self.filter:  # There is no ticket filter
                selected.append(item)
                continue
            elif not tiers:  # There was no ticket marker in this item but filter is set
                deselected.append(item)
                continue

            found = False
            for tier in tiers:
                if tier in self.filter:
                    found = True
                    break

            if found:
                selected.append(item)
            else:
                deselected.append(item)

        config.hook.pytest_deselected(items=deselected)
        items[:] = selected

    # Hook from pytest-output plugin
    @pytest.hookimpl(optionalhook=True)
    def pytest_output_item_collected(self, config: pytest.Config, item) -> None:
        try:
            from pytest_output.output import OutputDataItem
        except ImportError:
            pass

        if not isinstance(item, OutputDataItem):
            raise ValueError(f"Unexpected item type: {type(item)}")

        data: list[int] = item.item.stash[TierStashKey]
        if data:
            item.extra.setdefault("pytest-tier", {})["Tier"] = ", ".join(map(str, data))


def pytest_addoption(parser: pytest.Parser):
    """
    :meta private:
    """
    parser.addoption(
        "--tier",
        action="append",
        help="Filter tests by tier, can be set multiple times",
        required=False,
        default=list(),
    )


def pytest_configure(config: pytest.Config):
    """
    :meta private:
    """

    # register additional markers
    config.addinivalue_line("markers", "tier(number): tier that the test belongs to, the value is integer")

    config.pluginmanager.register(TierPlugin(config), name="PytestTier")
