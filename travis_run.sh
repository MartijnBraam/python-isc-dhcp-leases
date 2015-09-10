#!/bin/bash
set -e
coverage run --source isc_dhcp_leases setup.py test
/usr/bin/env python setup.py test