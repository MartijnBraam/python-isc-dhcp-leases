python-isc-dhcp-leases
======================

[![Build Status](https://travis-ci.org/MartijnBraam/python-isc-dhcp-leases.svg?branch=master)](https://travis-ci.org/MartijnBraam/python-isc-dhcp-leases)
[![PyPI version](https://badge.fury.io/py/isc_dhcp_leases.svg)](http://badge.fury.io/py/isc_dhcp_leases)
[![Coverage Status](https://coveralls.io/repos/MartijnBraam/python-isc-dhcp-leases/badge.svg)](https://coveralls.io/r/MartijnBraam/python-isc-dhcp-leases)

Small python module for reading /var/lib/dhcp/dhcpd.leases from isc-dhcp-server. This module works in Python 2.7 and 3.x

This module also supports reading lease files from the isc dhcp daemon running in IPv6 mode (Since version 0.4.0). 

## Installation

### Through pypi

```bash
$ sudo pip install isc_dhcp_leases
```

### Through git

```bash
$ git clone git@github.com:MartijnBraam/python-isc-dhcp-leases.git
$ cd python-isc-dhcp-leases
$ python setup.py build
$ sudo python setup.py install
```

## Usage

```python
from isc_dhcp_leases.iscdhcpleases import Lease, IscDhcpLeases

leases = IscDhcpLeases('/path/to/dhcpd.leases')
leases.get()  # Returns the leases as a list of Lease objects
leases.get_current()  # Returns only the currently valid dhcp leases as dict
                      # The key of the dict is the device mac address and the
                      # Value is a Lease object
```

The Lease object has the following fields (only for IPv4 leases)

```python
lease = Lease()
lease.ip             # The ip address assigned by this lease as string
lease.ethernet       # The mac address of the lease
lease.hardware       # The OSI physical layer used to request the lease (usually ethernet)
lease.start          # The start time of this lease as DateTime object
lease.end            # The time this lease expires as DateTime object or None if this is an infinite lease
lease.hostname       # The hostname for this lease if given by the client
lease.binding_state  # The binding state as string ('active', 'free', 'abandoned', 'backup')
lease.data           # Dict of all the info in the dhcpd.leases file for this lease
lease.valid          # True if the lease hasn't expired and is not in the future
lease.active         # True if the binding state is active
```

The Lease6 object has the following fields (only for IPv6)

```python
lease = Lease6()
lease.ip                 # The ip address assigned by this lease as string
lease.type               # If this is a temporary or permanent address. I's one of the following:
                         # Lease6.TEMPORARY: Temporary lease
                         # Lease6.NON_TEMPORARY: Non-temporary lease
                         # Lease6.PREFIX_DELEGATION: Delegated prefix lease
lease.host_identifier    # The unique host identifier (replaces mac addresses in IPv6)
lease.duid               # The DHCP Unique Identifier (DUID) of the host
lease.iaid               # The Interface Association Identifier (IAID) of the host
lease.last_communication # The last communication time with the host
lease.end                # The time this lease expires as DateTime object or None if this is an infinite lease
lease.binding_state      # The binding state as string ('active', 'free', 'abandoned', 'backup')
lease.preferred_life     # The preferred lifetime in seconds
lease.max_life           # The valid lifetime for this address in seconds
lease.data               # Dict of all the info in the dhcpd6.leases file for this lease
```

## Unit tests

The unit tests can be run with setup.py

```bash
$ python3 setup.py test
# With coverage report:
$ coverage run setup.py test
```
