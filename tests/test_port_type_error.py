from copy import copy
from pickle import dumps, loads

from notwork.exceptions import PortTypeError


def test_port_type_error_is_type_error() -> None:
    """Assert that `PortTypeError` extends `TypeError`."""
    assert issubclass(PortTypeError, TypeError)


def test_port_type_error_port_and_message() -> None:
    """Assert that `PortTypeError` describes the port that isn't an `int`."""
    error = PortTypeError("80")

    assert error.port == "80"
    assert str(error) == "Port '80' must be an int"


def test_port_type_error_survives_pickling() -> None:
    """Assert that `PortTypeError` keeps its port and message when pickled."""
    error = loads(dumps(PortTypeError("80")))

    assert error.port == "80"
    assert str(error) == "Port '80' must be an int"


def test_port_type_error_survives_copying() -> None:
    """Assert that `PortTypeError` keeps its port and message when copied."""
    error = copy(PortTypeError("80"))

    assert error.port == "80"
    assert str(error) == "Port '80' must be an int"
