from socket import (
    AF_INET,
    AF_INET6,
    IPPROTO_IPV6,
    IPV6_V6ONLY,
    SOCK_STREAM,
    has_dualstack_ipv6,
    socket,
)

from pytest import fixture

from notwork import has_ipv6


@fixture
def free_port() -> int:
    """A port that nothing listens on, on any IPv4 or IPv6 address."""
    if has_ipv6() and has_dualstack_ipv6():
        sock = socket(
            AF_INET6,
            SOCK_STREAM,
        )

        sock.setsockopt(
            IPPROTO_IPV6,
            IPV6_V6ONLY,
            False,
        )

        host = "::"

    else:
        sock = socket(
            AF_INET,
            SOCK_STREAM,
        )

        host = "0.0.0.0"

    with sock:
        sock.bind((host, 0))
        port: int = sock.getsockname()[1]

    return port
