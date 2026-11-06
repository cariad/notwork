from typing import cast

from pytest import mark

from notwork import is_port_in_range


@mark.parametrize(
    ("port", "expect"),
    [
        (-1, False),
        (0, False),
        (1, True),
        (65_535, True),
        (65_536, False),
    ],
)
def test_is_port_in_range(port: int, expect: bool) -> None:
    """
    Assert that `is_port_in_range` returns whether or not a port is in the valid
    range.
    """
    assert is_port_in_range(port) is expect


@mark.parametrize(
    "port",
    [
        True,
        80.0,
        "80",
    ],
)
def test_is_port_in_range_rejects_non_int(port: object) -> None:
    """Assert that `is_port_in_range` returns `False` for a port that isn't an `int`."""
    assert is_port_in_range(cast("int", port)) is False
