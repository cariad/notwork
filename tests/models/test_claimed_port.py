from socket import AF_INET, SOCK_STREAM, socket

from notwork import ClaimedPort


def _sockets() -> list[socket]:
    """Open two unbound sockets."""
    return [socket(AF_INET, SOCK_STREAM) for _ in range(2)]


def test_claimed_port_close_closes_every_socket() -> None:
    """Assert that `close` closes the sockets and the guards."""
    sockets = _sockets()
    guards = _sockets()

    ClaimedPort(
        port=8000,
        sockets=sockets,
        guards=guards,
    ).close()

    result = [sock.fileno() for sock in (*sockets, *guards)]
    expect = [-1] * 4

    assert result == expect


def test_claimed_port_closes_on_exit() -> None:
    """Assert that leaving a claimed port's context closes every socket."""
    sockets = _sockets()
    guards = _sockets()

    with ClaimedPort(
        port=8000,
        sockets=sockets,
        guards=guards,
    ) as claimed:
        result = claimed.sockets

    assert result is sockets
    assert [sock.fileno() for sock in (*sockets, *guards)] == [-1] * 4


def test_claimed_port_port() -> None:
    """Assert that a claimed port knows its port."""
    claimed = ClaimedPort(
        port=8000,
        sockets=[],
        guards=[],
    )

    result = claimed.port
    expect = 8000

    assert result == expect
