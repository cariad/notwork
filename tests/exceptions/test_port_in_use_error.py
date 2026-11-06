from copy import copy
from errno import EADDRINUSE
from os import strerror
from pickle import dumps, loads

from notwork.exceptions import PortInUseError


def test_port_in_use_error_is_os_error() -> None:
    """Assert that `PortInUseError` extends `OSError`."""
    assert issubclass(PortInUseError, OSError)


def test_port_in_use_error_errno() -> None:
    """Assert that `PortInUseError` has the system's busy-port code and message."""
    error = PortInUseError(8000)

    assert error.errno == EADDRINUSE
    assert error.strerror == strerror(EADDRINUSE)


def test_port_in_use_error_port_and_message() -> None:
    """Assert that `PortInUseError` describes the port that's in use."""
    error = PortInUseError(8000)

    assert error.port == 8000
    assert str(error) == "Port 8000 is in use"


def test_port_in_use_error_survives_pickling() -> None:
    """Assert that `PortInUseError` keeps its port, code and message when pickled."""
    error = loads(dumps(PortInUseError(8000)))

    assert error.port == 8000
    assert error.errno == EADDRINUSE
    assert str(error) == "Port 8000 is in use"


def test_port_in_use_error_survives_copying() -> None:
    """Assert that `PortInUseError` keeps its port, code and message when copied."""
    error = copy(PortInUseError(8000))

    assert error.port == 8000
    assert error.errno == EADDRINUSE
    assert str(error) == "Port 8000 is in use"
