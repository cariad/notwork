# notwork

Python functions for when your network might notwork.

Read the documentation at [cariad.github.io/notwork](https://cariad.github.io/notwork/).

## Installation

`notwork` needs Python 3.14 or later, and has no dependencies.

```bash
pip install notwork
```

Or with uv:

```bash
uv add notwork
```

## Usage

### Check a port number

[`is_port_in_range`](https://cariad.github.io/notwork/functions/is_port_in_range/) says whether a port number is valid, and [`check_port_is_in_range`](https://cariad.github.io/notwork/functions/check_port_is_in_range/) raises [`PortOutOfRangeError`](https://cariad.github.io/notwork/exceptions/port_out_of_range_error/) when it isn't.

```python
from notwork import check_port_is_in_range, is_port_in_range

is_port_in_range(8000)
# True

check_port_is_in_range(70000)
# PortOutOfRangeError: Port 70000 must be 1-65535
```

### Check for IPv6

[`has_ipv6`](https://cariad.github.io/notwork/functions/has_ipv6/) says whether this machine can bind `::1`, the IPv6 loopback address.

```python
from notwork import has_ipv6

has_ipv6()
# True when this machine can bind ::1
```

### Claim a port

[`claim_port`](https://cariad.github.io/notwork/functions/claim_port/) claims a port on every address that `localhost` can mean, and returns a [`ClaimedPort`](https://cariad.github.io/notwork/models/claimed_port/) to listen on.

If another program is already using the port on `localhost`, it raises [`PortInUseError`](https://cariad.github.io/notwork/exceptions/port_in_use_error/).

On Linux, the sockets are already listening when they're returned. On Windows, another program can still bind the port on `::` with a socket that accepts IPv4 and IPv6 at once.

```python
from notwork import claim_port

with claim_port(8000) as port:
    # Bound to 127.0.0.1, and ::1 when there's IPv6
    for sock in port.sockets:
        sock.listen()

# Leaving the `with` block closed the port.
```
