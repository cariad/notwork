from errno import EADDRNOTAVAIL, EAFNOSUPPORT, EMFILE, EPROTONOSUPPORT
from socket import AF_INET6
from unittest.mock import patch

from pytest import raises

from notwork import has_ipv6

from .os_error import make_os_error


class _SocketWithoutLoopback:
    """A socket on a machine whose IPv6 is turned off."""

    def __init__(self, *args: object) -> None:
        """Accept any arguments, without opening a real socket."""

    def __enter__(self) -> _SocketWithoutLoopback:
        """Enter the socket's context."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit the socket's context."""

    def bind(self, address: object, /) -> None:
        """Refuse to bind."""
        raise make_os_error(EADDRNOTAVAIL)


def test_has_ipv6_is_false_when_not_available() -> None:
    """Assert that `has_ipv6` returns `False` when IPv6 is disabled."""
    with patch("notwork.has_ipv6.socket", _SocketWithoutLoopback):
        result = has_ipv6()

    assert result is False


def test_has_ipv6_is_false_when_python_has_no_ipv6() -> None:
    """Assert that `has_ipv6` returns `False` when Python was built without IPv6."""
    with patch("notwork.has_ipv6._AF_INET6", None):
        result = has_ipv6()

    assert result is False


def test_has_ipv6_is_false_when_python_has_no_ipv6_but_af_inet6_exists() -> None:
    """
    Assert that `has_ipv6` returns `False` when Python was built without IPv6 but still
    exports `AF_INET6`.
    """
    with (
        patch("notwork.has_ipv6._PYTHON_HAS_IPV6", False),
        patch("notwork.has_ipv6._AF_INET6", AF_INET6),
        patch("notwork.has_ipv6.socket") as mock_socket,
    ):
        result = has_ipv6()

    mock_socket.assert_not_called()
    assert result is False


def test_has_ipv6_is_false_when_not_supported() -> None:
    """Assert that `has_ipv6` returns `False` when IPv6 is not supported."""
    with patch("notwork.has_ipv6.socket", side_effect=make_os_error(EAFNOSUPPORT)):
        result = has_ipv6()

    assert result is False


def test_has_ipv6_is_false_when_protocol_not_supported() -> None:
    """Assert that `has_ipv6` returns `False` when the IPv6 protocol isn't supported."""
    with patch("notwork.has_ipv6.socket", side_effect=make_os_error(EPROTONOSUPPORT)):
        result = has_ipv6()

    assert result is False


def test_has_ipv6_is_true_with_ipv6_loopback() -> None:
    """Assert that `has_ipv6` returns `True` when the machine can bind ::1."""
    with patch("notwork.has_ipv6.socket") as mock_socket:
        result = has_ipv6()

    sock = mock_socket.return_value.__enter__.return_value

    sock.bind.assert_called_once_with(("::1", 0))
    mock_socket.return_value.__exit__.assert_called_once()
    assert result is True


def test_has_ipv6_raises_when_it_cannot_check() -> None:
    """Assert that `has_ipv6` raises when it can't make the check."""
    expect = make_os_error(EMFILE)

    with (
        patch("notwork.has_ipv6.socket", side_effect=expect),
        raises(OSError) as ex,
    ):
        has_ipv6()

    result = ex.value

    assert result is expect
