from copy import copy
from pickle import dumps, loads

from notwork.exceptions import PortOutOfRangeError


def test_port_out_of_range_error_is_value_error() -> None:
    """Assert that `PortOutOfRangeError` extends `ValueError`."""
    assert issubclass(PortOutOfRangeError, ValueError)


def test_port_out_of_range_error_port_and_message() -> None:
    """Assert that `PortOutOfRangeError` describes the port that's out of range."""
    error = PortOutOfRangeError(70_000)

    assert error.port == 70_000
    assert str(error) == "Port 70000 must be 1-65535"


def test_port_out_of_range_error_survives_pickling() -> None:
    """Assert that `PortOutOfRangeError` keeps its port and message when pickled."""
    error = loads(dumps(PortOutOfRangeError(70_000)))

    assert error.port == 70_000
    assert str(error) == "Port 70000 must be 1-65535"


def test_port_out_of_range_error_survives_copying() -> None:
    """Assert that `PortOutOfRangeError` keeps its port and message when copied."""
    error = copy(PortOutOfRangeError(70_000))

    assert error.port == 70_000
    assert str(error) == "Port 70000 must be 1-65535"
