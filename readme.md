# pytest-tier

This is a `pytest` plugin that adds the ability to filter test cases by
associated tier.

It adds:
* `@pytest.mark.tier(number)` mark to associate test case with given tier
* `--tier` command line option to filter out test cases that are not
  associated with selected tier(s)

## Example usage

1. Enable plugin in conftest.py

    ```python
    pytest_plugins = (
        "pytest_tier",
    )
    ```

2. Define test with tier mark

    ```python
    @pytest.mark.tier(0)
    def test_tier():
        pass
    ```

4. Run pytest with tier filter

    ```
    $ pytest --tier=0
    ```

## Tier mark

The tier mark takes single integer as an argument.

```
@pytest.mark.tier(int)
```

## --tier command line option

You can filter tests using the `--tier` option, which takes the desired tier as
an argument. This option can be passed multiple times.

```
pytest --tier=0 --tier=1 ...
```
