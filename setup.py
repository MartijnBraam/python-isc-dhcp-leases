from distutils.core import setup

setup(
    name='isc_dhcp_leases',
    version='0.2.1',
    packages=['isc_dhcp_leases'],
    url='https://github.com/MartijnBraam/python-isc-dhcp-leases',
    license='MIT',
    author='Martijn Braam',
    author_email='martijn@brixit.nl',
    description='Small python module for reading /var/lib/dhcp/dhcpd.leases from isc-dhcp-server'
)
