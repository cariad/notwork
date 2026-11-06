from os import strerror


def make_os_error(code: int) -> OSError:
    """
    Make a new `OSError` for `code`, with the same message that the operating
    system would give.

    Args:
        code: The `errno` value.

    Returns:
        An `OSError` with a code and message.
    """
    return OSError(code, strerror(code))
