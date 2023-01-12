from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="function")
def _enable_plugin(pytester: pytest.Pytester):
    pytester.makeconftest(
        """
        pytest_plugins = ["pytest_tier"]
        """
    )


def test_plugin__multiple_values(pytester: pytest.Pytester):
    """Make sure that multiple values yields error."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier(0, 1)
        def test_tier():
            pass
        """
    )

    result = pytester.runpytest()
    result.stdout.re_match_lines(r".*@pytest.mark.tier has more that one arguments*")


def test_plugin__non_integer_values(pytester: pytest.Pytester):
    """Make sure that non integer values yields error."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier("0")
        def test_tier():
            pass
        """
    )

    result = pytester.runpytest()
    result.stdout.re_match_lines(r".*@pytest.mark.tier has non-integer argument*")


def test_plugin__filter_single_value(pytester: pytest.Pytester):
    """Make sure that filter works correctly with single value."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier(1)
        def test_1():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=1")
    result.assert_outcomes(passed=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=2")
    result.assert_outcomes(deselected=1)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")


def test_plugin__filter_multiple_values(pytester: pytest.Pytester):
    """Make sure that filter works correctly with multiple filter values."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier(1)
        def test_1():
            pass

        @pytest.mark.tier(2)
        def test_2():
            pass

        @pytest.mark.tier(3)
        def test_3():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=1", "--tier=2")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=3")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")


def test_plugin__filter_multiple_tests(pytester: pytest.Pytester):
    """Make sure that filter works correctly with multiple tests with same tier."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier(1)
        def test_1():
            pass

        @pytest.mark.tier(1)
        def test_2():
            pass

        @pytest.mark.tier(3)
        def test_3():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=1", "--tier=2")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=3")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")


def test_plugin__class(pytester: pytest.Pytester):
    """Make sure that the mark work with classes."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.tier(0)
        class TestMark(object):
            @pytest.mark.tier(1)
            def test_1(self):
                pass

            def test_2(self):
                pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=2)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=0")
    result.assert_outcomes(passed=2)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")

    result = pytester.runpytest("-vvv", "--tier=1")
    result.assert_outcomes(passed=1, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
