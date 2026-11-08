from importlib import import_module

from pytest import MonkeyPatch

from notwork import claim_port, free_port
from notwork.exceptions import PortInUseError
from notwork.models import ClaimedPort

_MODULE = import_module("notwork.free_port")
"""The module that defines `free_port`, which the package's function shadows."""


def test_free_port_can_be_claimed() -> None:
    """Assert that the port that `free_port` returns can then be claimed."""
    port = free_port()

    with claim_port(port) as claimed:
        result = claimed.port

    assert result == port


def test_free_port_skips_port_in_use(monkeypatch: MonkeyPatch) -> None:
    """Assert that `free_port` tries another port when its first pick is in use."""
    attempts: list[int] = []

    def claim_once_in_use(port: int) -> ClaimedPort:
        attempts.append(port)

        if len(attempts) == 1:
            raise PortInUseError(port)

        return claim_port(port)

    monkeypatch.setattr(_MODULE, "claim_port", claim_once_in_use)

    result = free_port()

    assert len(attempts) == 2
    assert result == attempts[1]
