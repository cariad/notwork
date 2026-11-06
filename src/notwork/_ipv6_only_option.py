import socket

IPV6_ONLY_OPTION: tuple[int, int] | None = (
    (socket.IPPROTO_IPV6, socket.IPV6_V6ONLY)
    if hasattr(socket, "IPPROTO_IPV6") and hasattr(socket, "IPV6_V6ONLY")
    else None
)
"""
The level and name of the socket option that makes an IPv6 socket accept only IPv6, or
`None` if the system doesn't define one.
"""
