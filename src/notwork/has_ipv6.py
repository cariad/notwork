from errno import EADDRNOTAVAIL, EAFNOSUPPORT, EPROTONOSUPPORT
from socket import SOCK_STREAM, AddressFamily, socket
from socket import has_ipv6 as _PYTHON_HAS_IPV6

_AF_INET6 = AddressFamily.__members__.get("AF_INET6")
"""The IPv6 address family, or `None` if the system doesn't define one."""

_NO_IPV6 = (
    # IPv6 is not available: it's supported, but disabled.
    EADDRNOTAVAIL,
    # IPv6 is not supported, and can't be enabled.
    EAFNOSUPPORT,
    # IPv6 is not supported, as reported by some kernels and sandboxes.
    EPROTONOSUPPORT,
)
"""The errors that mean this machine has no IPv6."""


def has_ipv6() -> bool:
    """
    Return `True` if this machine can bind the IPv6 loopback address (`::1`),
    otherwise `False`.

    Returns:
        `True` when this machine can bind `::1`, otherwise `False`.

    Raises:
        OSError: When the check can't be performed.

    Examples:
        ```python
        has_ipv6()
        # True
        ```
    """
    # Python built with `--disable-ipv6` can still export `AF_INET6` from the
    # system headers, but can't bind IPv6 addresses, so check both.
    if not _PYTHON_HAS_IPV6 or _AF_INET6 is None:
        return False

    try:
        with socket(_AF_INET6, SOCK_STREAM) as sock:
            sock.bind(("::1", 0))

    except OSError as ex:
        if ex.errno in _NO_IPV6:
            return False

        raise

    return True
