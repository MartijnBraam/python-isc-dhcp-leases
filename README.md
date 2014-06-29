python-isc-dhcp-leases
======================

Small python module for reading /var/lib/dhcp/dhcpd.leases from isc-dhcp-server

## Installation

### Through pypi

```bash
$ sudo pip install python-isc-dhcp-leases
```

### Through git

```bash
$ git clone git@github.com:MartijnBraam/python-isc-dhcp-leases.git
$ cd python-isc-dhcp-leases
$ python setup.py build
$ python setup.py install
```

## Usage

```python
from python-isc-dhcp-leases.iscdhcpleases import *  # Lease and IscDhcpLeases

leases = IscDhcpLeases('/path/to/dhcpd.leases')
leases.get()  # Returns the leases as a list of Lease objects
leases.get_current()  # Returns only the currently valid dhcp leases as dict
                      # The key of the dict is the device mac address and the
                      # Value is a Lease object
```

The Lease object has the following fields
```python
lease = Lease()
lease.ip        # The ip address assigned by this lease as string
lease.ethernet  # The mac address of the lease
lease.start     # The start time of this lease as DateTime object
lease.end       # The time this lease expires as DateTime object
lease.hostname  # The hostname for this lease if given by the client
lease.data      # Dict of all the info in the dhcpd.leases file for this lease
```
