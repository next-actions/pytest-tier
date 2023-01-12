from __future__ import annotations

import pytest


class TierPlugin(object):
    def __init__(self, config: pytest.Config) -> None:
        self.filter: list[int] = [int(x) for x in config.getoption("tier")]

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, config: pytest.Config, items: list[pytest.Item]) -> None:
        """
        Filter collected items and deselect these that do not match the tier filter.

        :meta private:
        """
        # There is no tier filter
        if not self.filter:
            return

        selected = []
        deselected = []

        for item in items:
            tiers = []
            for mark in item.iter_markers("tier"):
                if len(mark.args) != 1:
                    raise ValueError("@pytest.mark.tier has more that one arguments")

                if type(mark.args[0]) != int:
                    raise ValueError("@pytest.mark.tier has non-integer argument")

                tiers.append(mark.args[0])

            # There was no tier marker in this item
            if not tiers:
                if self.filter:
                    deselected.append(item)
                else:
                    selected.append(item)
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

    config.pluginmanager.register(TierPlugin(config))
