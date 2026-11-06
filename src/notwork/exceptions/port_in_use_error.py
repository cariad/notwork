from errno import EADDRINUSE
from os import strerror


class PortInUseError(OSError):
    """Raised when a desired port is in use."""

    def __init__(self, port: int) -> None:
        """
        Create an error for a port that's in use.

        Args:
            port: Port that's in use.
        """
        super().__init__(
            EADDRINUSE,
            strerror(EADDRINUSE),
        )

        self.port = port
        """The port that's in use."""

    def __reduce__(self) -> tuple[type[PortInUseError], tuple[int]]:
        """Pickle by the port."""
        return (type(self), (self.port,))

    def __str__(self) -> str:
        """Describe the port that's in use."""
        return f"Port {self.port} is in use"
