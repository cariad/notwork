from notwork.constants import MAX_PORT, MIN_PORT


def test_min_port() -> None:
    """Assert that the lowest valid port number is 1."""
    assert MIN_PORT == 1


def test_max_port() -> None:
    """Assert that the highest valid port number is 65535."""
    assert MAX_PORT == 65_535
