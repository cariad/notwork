from socket import AF_INET, SOCK_STREAM, socket

from .claim_port import claim_port
from .exceptions import PortInUseError


def free_port() -> int:
    """
    Return a port that [`claim_port`][notwork.claim_port.claim_port] can claim right
    now, on every address that `localhost` can mean on this machine.

    The port isn't held after it's returned, so another program can take it before you
    use it. Use `free_port` in tests and local tools, not to choose a port for a server
    that other programs depend on.

    Returns:
        A port that can be claimed right now.

    Raises:
        OSError: When a port can't be found for any reason other than one being in use.

    Examples:
        ```python
        port = free_port()

        with claim_port(port) as claimed:
            for sock in claimed.sockets:
                sock.listen()
        ```
    """
    while True:
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port: int = sock.getsockname()[1]

        try:
            claim_port(port).close()

        except PortInUseError:
            continue

        return port
