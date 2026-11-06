from ..constants import MAX_PORT, MIN_PORT


class PortOutOfRangeError(ValueError):
    """Raised when a port isn't in the valid range."""

    def __init__(self, port: int) -> None:
        """
        Create an error for an out-of-range port.

        Args:
            port: Port that's out of range.
        """
        super().__init__(port)
        self.port = port
        """The port that's out of range."""

    def __str__(self) -> str:
        """Describe the port that's out of range."""
        return f"Port {self.port} must be {MIN_PORT}-{MAX_PORT}"
