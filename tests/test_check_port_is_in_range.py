from typing import cast

from pytest import mark, raises

from notwork import check_port_is_in_range
from notwork.exceptions import PortOutOfRangeError, PortTypeError


@mark.parametrize(
    "port",
    [
        1,
        65_535,
    ],
)
def test_check_port_is_in_range_accepts_port_in_range(port: int) -> None:
    """
    Assert that `check_port_is_in_range` returns nothing for a port that's in the valid
    range.
    """
    check_port_is_in_range(port)


@mark.parametrize(
    "port",
    [
        -1,
        0,
        65_536,
    ],
)
def test_check_port_is_in_range_raises_for_port_out_of_range(port: int) -> None:
    """
    Assert that `check_port_is_in_range` raises for a port that isn't in the valid
    range.
    """
    with raises(PortOutOfRangeError) as ex:
        check_port_is_in_range(port)

    assert ex.value.port == port
    assert str(ex.value) == f"Port {port} must be 1-65535"


@mark.parametrize(
    "port",
    [
        True,
        80.0,
        "80",
    ],
)
def test_check_port_is_in_range_raises_for_non_int(port: object) -> None:
    """Assert that `check_port_is_in_range` raises for a port that isn't an `int`."""
    with raises(PortTypeError) as ex:
        check_port_is_in_range(cast("int", port))

    assert ex.value.port is port
    assert str(ex.value) == f"Port {port!r} must be an int"
