from collections.abc import Generator
from contextlib import closing, contextmanager
from errno import EACCES, EADDRINUSE
from socket import (
    AF_INET,
    AF_INET6,
    IPPROTO_IPV6,
    IPV6_V6ONLY,
    SO_REUSEADDR,
    SOCK_STREAM,
    SOL_SOCKET,
    create_connection,
    socket,
)
from typing import cast
from unittest.mock import patch

from pytest import mark, param, raises

from notwork import claim_port
from notwork.exceptions import PortInUseError, PortOutOfRangeError, PortTypeError

from .marks import holds_wildcards, needs_dual_stack, needs_ipv6
from .os_error import make_os_error


@contextmanager
def _claimed(port: int) -> Generator[list[socket]]:
    """Claim `port`, yield the sockets, and release the port afterwards."""
    with claim_port(port) as claimed:
        yield claimed.sockets


@contextmanager
def _listen(
    host: str,
    *,
    dual_stack: bool = False,
    reuse_address: bool = False,
) -> Generator[int]:
    """
    Listen on `host` and yield the port.

    Args:
        host: Address to listen on.
        dual_stack: Whether or not an IPv6 socket accepts IPv4 too.
        reuse_address: Whether or not to set `SO_REUSEADDR`.
    """
    family = AF_INET6 if ":" in host else AF_INET

    with socket(family, SOCK_STREAM) as sock:
        sock.setsockopt(
            SOL_SOCKET,
            SO_REUSEADDR,
            reuse_address,
        )

        if family == AF_INET6:
            sock.setsockopt(
                IPPROTO_IPV6,
                IPV6_V6ONLY,
                not dual_stack,
            )

        sock.bind((host, 0))
        sock.listen()

        yield sock.getsockname()[1]


@needs_ipv6
def test_claim_port_claims_every_loopback(free_port: int) -> None:
    """Assert that `claim_port` claims `127.0.0.1` and `::1` on a machine with IPv6."""
    with _claimed(free_port) as sockets:
        result = [sock.getsockname()[:2] for sock in sockets]

    expect = [
        ("127.0.0.1", free_port),
        ("::1", free_port),
    ]

    assert result == expect


def test_claim_port_claims_ipv4_without_ipv6(free_port: int) -> None:
    """Assert that `claim_port` claims only `127.0.0.1` on a machine without IPv6."""
    with (
        patch("notwork.claim_port.has_ipv6", return_value=False),
        _claimed(free_port) as sockets,
    ):
        result = [sock.getsockname()[:2] for sock in sockets]

    expect = [
        ("127.0.0.1", free_port),
    ]

    assert result == expect


def test_claim_port_claims_port_again_after_closing(free_port: int) -> None:
    """
    Assert that a port whose claimed sockets have been closed can be claimed again
    straight away, even with a connection that one of them accepted still open.
    """
    with _claimed(free_port) as sockets:
        listener = sockets[0]
        listener.listen()

        page = create_connection(
            ("127.0.0.1", free_port),
            timeout=5,
        )

        accepted, _ = listener.accept()

    with (
        closing(page),
        closing(accepted),
        _claimed(free_port) as sockets,
    ):
        result = [sock.getsockname()[1] for sock in sockets]

    expect = [free_port] * len(result)

    assert result
    assert result == expect


def test_claim_port_opens_only_ipv4_sockets_without_ipv6(free_port: int) -> None:
    """Assert that `claim_port` opens no IPv6 socket on a machine without IPv6."""
    with (
        patch("notwork.claim_port.has_ipv6", return_value=False),
        patch("notwork.claim_port.socket", wraps=socket) as opened,
        _claimed(free_port),
    ):
        result = {call.args[0] for call in opened.call_args_list}

    expect = {
        AF_INET,
    }

    assert result == expect


def test_claim_port_binds_no_dual_stack_socket_without_support(free_port: int) -> None:
    """
    Assert that `claim_port` binds no socket that accepts IPv4 and IPv6 at once on a
    machine that doesn't support one.
    """
    with (
        patch("notwork.claim_port._HOLD_WILDCARDS", True),
        patch("notwork.claim_port.has_dualstack_ipv6", return_value=False),
        patch("notwork.claim_port._bind") as bound,
        _claimed(free_port),
    ):
        result = [call.kwargs.get("dual_stack", False) for call in bound.call_args_list]

    assert True not in result


@mark.parametrize(
    (
        "host",
        "dual_stack",
    ),
    [
        (
            "127.0.0.1",
            False,
        ),
        param(
            "::1",
            False,
            marks=needs_ipv6,
        ),
        (
            "0.0.0.0",
            False,
        ),
        # Every address, IPv4 and IPv6, as `python -m http.server` listens.
        param(
            "::",
            True,
            marks=needs_dual_stack,
        ),
        # Every IPv6 address, ::1 included.
        param(
            "::",
            False,
            marks=needs_ipv6,
        ),
    ],
)
@mark.parametrize(
    "reuse_address",
    [
        False,
        True,
    ],
)
def test_claim_port_raises_for_busy_port(
    dual_stack: bool,
    host: str,
    reuse_address: bool,
) -> None:
    """Assert that `claim_port` raises `PortInUseError` for a busy port."""
    with (
        _listen(
            host,
            dual_stack=dual_stack,
            reuse_address=reuse_address,
        ) as port,
        raises(PortInUseError) as ex,
    ):
        claim_port(port)

    result = ex.value.port
    expect = port

    assert result == expect


def test_claim_port_raises_system_error_for_other_failures(free_port: int) -> None:
    """
    Assert that `claim_port` raises the system's own error when a port can't be claimed
    for any reason other than being in use.
    """
    error = make_os_error(EACCES)

    with patch("notwork.claim_port.socket") as opened:
        opened.return_value.bind.side_effect = error

        with raises(OSError) as ex:
            claim_port(free_port)

    assert ex.value is error


def test_claim_port_raises_for_non_int() -> None:
    """Assert that `claim_port` raises for a port that isn't an `int`."""
    port = "8000"

    with raises(PortTypeError) as ex:
        claim_port(cast("int", port))

    result = ex.value.port
    expect = port

    assert result is expect


@mark.parametrize(
    "port",
    [
        0,
        65_536,
    ],
)
def test_claim_port_raises_for_port_out_of_range(port: int) -> None:
    """Assert that `claim_port` raises for a port that isn't in the valid range."""
    with raises(PortOutOfRangeError) as ex:
        claim_port(port)

    result = ex.value.port
    expect = port

    assert result == expect


@holds_wildcards
@mark.parametrize(
    (
        "host",
        "dual_stack",
    ),
    [
        (
            "0.0.0.0",
            False,
        ),
        param(
            "::",
            False,
            marks=needs_ipv6,
        ),
        param(
            "::",
            True,
            marks=needs_dual_stack,
        ),
    ],
)
def test_claim_port_keeps_other_programs_off_wildcards(
    dual_stack: bool,
    free_port: int,
    host: str,
) -> None:
    """
    Assert that, while a port is claimed, another program can't bind its wildcard
    addresses.
    """
    family = AF_INET6 if ":" in host else AF_INET

    with (
        _claimed(free_port),
        socket(family, SOCK_STREAM) as other,
        raises(OSError) as ex,
    ):
        other.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

        if family == AF_INET6:
            other.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, not dual_stack)

        other.bind((host, free_port))

    result = ex.value.errno
    expect = EADDRINUSE

    assert result == expect


def test_claim_port_opens_only_loopbacks_without_holding_wildcards(
    free_port: int,
) -> None:
    """
    Assert that `claim_port` opens only the loopback sockets where it doesn't hold the
    wildcard addresses.
    """
    with (
        patch("notwork.claim_port._HOLD_WILDCARDS", False),
        patch("notwork.claim_port.socket", wraps=socket) as opened,
        _claimed(free_port) as sockets,
    ):
        result = opened.call_count

    expect = len(sockets)

    assert result == expect
