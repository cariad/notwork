from socket import AddressFamily

AF_INET6 = AddressFamily.__members__.get("AF_INET6")
"""The IPv6 address family, or `None` if the system doesn't define one."""
