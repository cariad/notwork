from typing import TypeGuard


def is_int(value: object) -> TypeGuard[int]:
    """
    Return `True` if `value` is an `int`, otherwise `False`.

    A `bool` is a subclass of `int` but isn't considered to be an `int`.

    Args:
        value: Value to check.

    Returns:
        `True` if `value` is an `int`, otherwise `False`.
    """
    return isinstance(value, int) and not isinstance(value, bool)
