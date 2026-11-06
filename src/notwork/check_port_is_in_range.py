from ._is_int import is_int
from .exceptions import PortOutOfRangeError, PortTypeError
from .is_port_in_range import is_port_in_range


def check_port_is_in_range(port: int) -> None:
    """
    Check that `port` is a valid port number.

    Args:
        port: Port to check.

    Raises:
        PortTypeError: When `port` isn't an `int`.
        PortOutOfRangeError: When `port` isn't a valid port number.

    Examples:
        ```python
        check_port_is_in_range(8000)
        # Pass

        check_port_is_in_range(70000)
        # PortOutOfRangeError
        ```
    """
    if not is_int(port):
        raise PortTypeError(port)

    if not is_port_in_range(port):
        raise PortOutOfRangeError(port)
