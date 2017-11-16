python-isc-dhcp-leases
======================

|Build Status| |PyPI version| |Coverage Status|

Small python module for reading /var/lib/dhcp/dhcpd.leases from
isc-dhcp-server. This module works in Python 2.7 and 3.x

This module also supports reading lease files from the isc dhcp daemon
running in IPv6 mode (Since version 0.4.0).

Installation
------------

Through pypi
~~~~~~~~~~~~

.. code:: bash

    $ sudo pip install isc_dhcp_leases

Through your distribution package manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This python module is currently packaged in Debian unstable (release for Debian 9) and will be packaged in Ubuntu 17.04
(Zesty Zapus)

.. code:: bash

    # For the python 2.7 interpreter
    $ sudo apt install python-isc-dhcp-leases

    # For the python 3 interpreter
    $ sudo apt install python3-isc-dhcp-leases


Through git
~~~~~~~~~~~

.. code:: bash

    $ git clone git@github.com:MartijnBraam/python-isc-dhcp-leases.git
    $ cd python-isc-dhcp-leases
    $ python setup.py build
    $ sudo python setup.py install

Usage
-----

.. code:: python

    from isc_dhcp_leases import Lease, IscDhcpLeases

    leases = IscDhcpLeases('/path/to/dhcpd.leases')
    leases.get()  # Returns the leases as a list of Lease objects
    leases.get_current()  # Returns only the currently valid dhcp leases as dict
                          # The key of the dict is the device mac address and the
                          # Value is a Lease object

Or read a gzip'ed file:

.. code:: python

    from isc_dhcp_leases import Lease, IscDhcpLeases
    # IscDhcpLeases(filename, gzip=False)
    leases = IscDhcpLeases('/path/to/dhcpd.leases', True) # True param starts the gzip reader
    leases.get()  # Returns the leases as a list of Lease objects
    leases.get_current()  # Returns only the currently valid dhcp leases as dict
                          # The key of the dict is the device mac address and the
                          # Value is a Lease object

The Lease object has the following fields (only for IPv4 leases):

.. code:: python

    lease instanceof Lease
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
    lease.options        # List of extra options in the lease file
    lease.sets           # List of the 'set' items in the lease file


The Lease6 object has the following fields (only for IPv6):

.. code:: python

    lease instanceof Lease6
    lease.ip                 # The ip address assigned by this lease as string
    lease.type               # If this is a temporary or permanent address. I's one of the following:
                             # Lease6.TEMPORARY: Temporary lease
                             # Lease6.NON_TEMPORARY: Non-temporary lease
                             # Lease6.PREFIX_DELEGATION: Delegated prefix lease
    lease.host_identifier    # The unique host identifier (replaces mac addresses in IPv6) as bytes
    lease.host_identifier_string # The host_identifier property formatted as an hexadecimal string
    lease.duid               # The DHCP Unique Identifier (DUID) of the host as bytes
    lease.iaid               # The Interface Association Identifier (IAID) of the host
    lease.last_communication # The last communication time with the host
    lease.end                # The time this lease expires as DateTime object or None if this is an infinite lease
    lease.binding_state      # The binding state as string ('active', 'free', 'abandoned', 'backup')
    lease.preferred_life     # The preferred lifetime in seconds
    lease.max_life           # The valid lifetime for this address in seconds
    lease.options            # List of extra options in the lease file
    lease.sets               # List of the 'set' items in the lease file
    lease.data               # Dict of all the info in the dhcpd6.leases file for this lease

Unit tests
----------

The unit tests can be run with ``setup.py``:

.. code:: bash

    $ python3 setup.py test
    # With coverage report:
    $ coverage run setup.py test

.. |Build Status| image:: https://travis-ci.org/MartijnBraam/python-isc-dhcp-leases.svg?branch=master
   :target: https://travis-ci.org/MartijnBraam/python-isc-dhcp-leases
.. |PyPI version| image:: https://badge.fury.io/py/isc_dhcp_leases.svg
   :target: http://badge.fury.io/py/isc_dhcp_leases
.. |Coverage Status| image:: https://coveralls.io/repos/MartijnBraam/python-isc-dhcp-leases/badge.svg
   :target: https://coveralls.io/r/MartijnBraam/python-isc-dhcp-leases
