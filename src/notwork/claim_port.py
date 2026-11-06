import sys
from contextlib import ExitStack
from errno import EADDRINUSE
from socket import (
    AF_INET,
    SO_REUSEADDR,
    SOCK_STREAM,
    SOL_SOCKET,
    AddressFamily,
    has_dualstack_ipv6,
    socket,
)

from ._af_inet6 import AF_INET6
from ._ipv6_only_option import IPV6_ONLY_OPTION
from .check_port_is_in_range import check_port_is_in_range
from .exceptions import PortInUseError
from .has_ipv6 import has_ipv6
from .models import ClaimedPort

_LOOPBACKS: dict[AddressFamily, str] = {
    family: host
    for family, host in ((AF_INET, "127.0.0.1"), (AF_INET6, "::1"))
    if family is not None
}
"""The addresses that `localhost` can mean, by address family."""

# Lets a socket bind while connections from a server are still closing, because they
# don't make the port busy.
_REUSE_ADDRESS = sys.platform != "win32"

# macOS and Windows let a socket bind a loopback address while another program listens
# on its wildcard, so they hold the wildcards for as long as the port is claimed, to
# find that program and keep others off. IPv6's wildcard is held only when this machine
# has IPv6.
#
# Linux refuses that bind, and binding the wildcard there would also find programs that
# listen only on other addresses, which `localhost` doesn't reach.
_HOLD_WILDCARDS = sys.platform not in ("android", "linux")

_WILDCARDS: dict[AddressFamily, str] = {
    family: host
    for family, host in ((AF_INET, "0.0.0.0"), (AF_INET6, "::"))
    if family is not None
}
"""
The addresses that a program listens on to accept connections on every address, loopback
included, by address family.
"""


def _bind(
    family: AddressFamily,
    host: str,
    port: int,
    *,
    dual_stack: bool = False,
) -> socket:
    """Bind a TCP socket to `host` and `port`."""
    sock = socket(family, SOCK_STREAM)

    try:
        sock.setsockopt(
            SOL_SOCKET,
            SO_REUSEADDR,
            _REUSE_ADDRESS,
        )

        if family != AF_INET and IPV6_ONLY_OPTION is not None:
            sock.setsockopt(
                *IPV6_ONLY_OPTION,
                not dual_stack,
            )

        try:
            sock.bind((host, port))

        except OSError as error:
            if error.errno == EADDRINUSE:
                raise PortInUseError(port) from error

            raise

    except BaseException:
        sock.close()
        raise

    return sock


def claim_port(port: int) -> ClaimedPort:
    """
    Claim `port` on every address that `localhost` can mean on this machine.

    The claimed port's sockets are bound but not listening. The caller can listen on
    them, and then must release the port by closing the port — not by closing its
    sockets.

    **Windows:** While the port is claimed, another program can still bind it on `::`
    with a socket that accepts IPv4 and IPv6 at once.

    Args:
        port: Port to claim.

    Returns:
        The claimed port, with a bound socket for each address.

    Raises:
        PortTypeError: When `port` isn't an `int`.
        PortOutOfRangeError: When `port` isn't a valid port number.
        PortInUseError: When `port` is in use and cannot be claimed.
        OSError: When `port` can't be claimed for any other reason.

    Examples:
        As a context manager:

        ```python
        with claim_port(8000) as port:
            # Bound to 127.0.0.1, and ::1 when there's IPv6
            for sock in port.sockets:
                sock.listen()

        # Leaving the `with` block closed the port.
        ```

        Without a context manager, you must close the port yourself:

        ```python
        port = claim_port(8000)

        try:
            for sock in port.sockets:
                sock.listen()

        finally:
            port.close()
        ```
    """
    check_port_is_in_range(port)

    families = [AF_INET]

    # Without the IPv6-only option, an IPv6 socket can't be kept from claiming IPv4 too.
    if AF_INET6 is not None and IPV6_ONLY_OPTION is not None and has_ipv6():
        families.append(AF_INET6)

    # Closes every socket bound so far if any bind fails.
    with ExitStack() as stack:
        guards: list[socket] = []

        if _HOLD_WILDCARDS:  # pragma: macos-and-windows-only
            # Windows lets a socket that accepts IPv4 and IPv6 at once share its port
            # with sockets that accept only one. It can't be held alongside the other
            # wildcards, so it's bound and closed first.
            if AF_INET6 is not None and AF_INET6 in families and has_dualstack_ipv6():
                _bind(
                    AF_INET6,
                    _WILDCARDS[AF_INET6],
                    port,
                    dual_stack=True,
                ).close()

            guards = [
                stack.enter_context(
                    _bind(
                        family,
                        _WILDCARDS[family],
                        port,
                    ),
                )
                for family in families
            ]

        sockets = [
            stack.enter_context(
                _bind(
                    family,
                    _LOOPBACKS[family],
                    port,
                ),
            )
            for family in families
        ]

        # Every socket is bound, so stop the stack closing them. The claimed port owns
        # them now, and closes them all when it's closed.
        stack.pop_all()

    return ClaimedPort(
        port=port,
        sockets=sockets,
        guards=guards,
    )
