from contextlib import ExitStack
from socket import socket
from types import TracebackType
from typing import Self


class ClaimedPort:
    """
    A port claimed on every address that `localhost` can mean on this machine.

    Closing the claimed port, directly or by leaving its context, closes its sockets and
    the sockets that hold the port's wildcard addresses, and releases the port.

    Create claimed ports only via [`claim_port`][notwork.claim_port.claim_port], not by
    instantiating this class directly.
    """

    def __init__(
        self,
        port: int,
        sockets: list[socket],
        guards: list[socket],
    ) -> None:
        """
        Create a claimed port.

        Args:
            port: Port that's claimed.
            sockets: Bound sockets, one for each loopback address.
            guards: Bound sockets that hold the port's wildcard addresses.
        """
        self._guards = guards

        self.port = port
        """The port that's claimed."""

        self.sockets = sockets
        """
        The bound sockets, one for each loopback address, to listen on.

        Closing these doesn't release the port: close the claimed port instead.
        """

    def __enter__(self) -> Self:
        """Return this claimed port."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close every socket and release the port."""
        self.close()

    def close(self) -> None:
        """Close every socket and release the port."""
        with ExitStack() as stack:
            for sock in (*self.sockets, *self._guards):
                stack.callback(sock.close)
