from ._is_int import is_int
from .constants import MAX_PORT, MIN_PORT


def is_port_in_range(port: int) -> bool:
    """
    Return `True` if `port` is a valid port number, otherwise `False`.

    Args:
        port: Port to check.

    Returns:
        `True` if `port` is a valid port number, otherwise `False`.

    Examples:
        ```python
        is_port_in_range(8000)
        # True

        is_port_in_range(70000)
        # False
        ```
    """
    return is_int(port) and MIN_PORT <= port <= MAX_PORT
