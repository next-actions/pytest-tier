from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="function")
def _enable_plugin(pytester: pytest.Pytester):
    pytester.makeconftest(
        """
        import pytest

        pytest_plugins = ["pytest_tier"]
        """
    )


def test_pytest_output__none(pytester: pytest.Pytester):
    """Make sure that no extra data is added when no tier is set."""
    pytester.makepyfile(
        """
        import pytest

        def test_tier(output_data_item):
            assert "pytest-tier" not in output_data_item.extra
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__single(pytester: pytest.Pytester):
    """Make sure that extra data is added when tier is set."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier(0)
        def test_tier(output_data_item):
            assert "pytest-tier" in output_data_item.extra
            assert "Tier" in output_data_item.extra["pytest-tier"]
            assert output_data_item.extra["pytest-tier"]["Tier"] == "0"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__class(pytester: pytest.Pytester):
    """Make sure that extra data is added when tier is set with class."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier(0)
        class TestTier(object):
            def test_0(self, output_data_item):
                assert "pytest-tier" in output_data_item.extra
                assert "Tier" in output_data_item.extra["pytest-tier"]
                assert output_data_item.extra["pytest-tier"]["Tier"] == "0"

            @pytest.mark.tier(1)
            def test_1(self, output_data_item):
                assert "pytest-tier" in output_data_item.extra
                assert "Tier" in output_data_item.extra["pytest-tier"]
                assert output_data_item.extra["pytest-tier"]["Tier"] == "0, 1"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
