import reprlib


class PortTypeError(TypeError):
    """Raised when a port isn't an `int`."""

    def __init__(self, port: object) -> None:
        """
        Create an error for a port that isn't an `int`.

        Args:
            port: Port that isn't an `int`.
        """
        super().__init__(port)
        self.port = port
        """The port that isn't an `int`."""

    def __str__(self) -> str:
        """Describe the port that isn't an `int`."""
        return f"Port {reprlib.repr(self.port)} must be an int"
