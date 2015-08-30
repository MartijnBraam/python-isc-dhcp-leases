from unittest import TestCase
from isc_dhcp_leases.iscdhcpleases import IscDhcpLeases, Lease, Lease6
from freezegun import freeze_time
from datetime import datetime

__author__ = 'Martijn Braam <martijn@brixit.nl>'


class TestIscDhcpLeases(TestCase):
    @freeze_time("2015-07-6 8:15:0")
    def test_get(self):
        leases = IscDhcpLeases("isc_dhcp_leases/test_files/debian7.leases")
        result = leases.get()
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].ip, "10.0.0.10")
        self.assertEqual(result[0].valid, False)
        self.assertEqual(result[0].active, False)
        self.assertEqual(result[0].binding_state, 'free')
        self.assertEqual(result[0].hardware, "ethernet")
        self.assertEqual(result[0].ethernet, "60:a4:4c:b5:6a:dd")
        self.assertEqual(result[0].hostname, "")
        self.assertEqual(result[0].start, datetime(2013, 12, 10, 12, 57, 4))
        self.assertEqual(result[0].end, datetime(2013, 12, 10, 13, 7, 4))

        leases = IscDhcpLeases("isc_dhcp_leases/test_files/pfsense.leases")
        result = leases.get()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].ip, "10.0.10.72")
        self.assertEqual(result[0].valid, True)
        self.assertEqual(result[0].active, True)
        self.assertEqual(result[0].binding_state, 'active')
        self.assertEqual(result[0].hardware, "ethernet")
        self.assertEqual(result[0].ethernet, "64:5a:04:6a:07:a2")
        self.assertEqual(result[0].hostname, "Satellite-C700")
        self.assertEqual(result[0].start, datetime(2015, 7, 6, 7, 50, 42))
        self.assertEqual(result[0].end, datetime(2015, 7, 6, 8, 20, 42))

        leases = IscDhcpLeases("isc_dhcp_leases/test_files/dhcpd6.leases")
        result = leases.get()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].ip, "2001:610:600:891d::60")
        self.assertEqual(result[0].host_identifier, "4dv\352\000\001\000\001\035f\037\342\012\000'\000\000\000")
        self.assertEqual(result[0].valid, True)
        self.assertEqual(result[0].active, True)
        self.assertEqual(result[0].binding_state, 'active')
        self.assertEqual(result[0].preferred_life, 375)
        self.assertEqual(result[0].max_life, 600)
        self.assertEqual(result[0].last_communication, datetime(2015, 8, 18, 16, 55, 37))
        self.assertEqual(result[0].type, Lease6.NON_TEMPORARY)

        self.assertEqual(result[1].ip, "2001:610:500:fff::/64")
        self.assertEqual(result[1].host_identifier, "4dv\352\000\001\000\001\035f\037\342\012\000'\000\000\000")
        self.assertEqual(result[1].valid, True)
        self.assertEqual(result[1].active, True)
        self.assertEqual(result[1].binding_state, 'active')
        self.assertEqual(result[1].preferred_life, 175)
        self.assertEqual(result[1].max_life, 200)
        self.assertEqual(result[1].last_communication, datetime(2015, 8, 18, 16, 55, 40))
        self.assertEqual(result[1].type, Lease6.PREFIX_DELEGATION)

    @freeze_time("2015-07-6 8:15:0")
    def test_get_current(self):
        leases = IscDhcpLeases("isc_dhcp_leases/test_files/debian7.leases")
        result = leases.get_current()
        self.assertEqual(len(result), 0)

        leases = IscDhcpLeases("isc_dhcp_leases/test_files/pfsense.leases")
        result = leases.get_current()
        self.assertEqual(len(result), 2)

        self.assertTrue("14:da:e9:04:c8:a3" in result)
        self.assertTrue("64:5a:04:6a:07:a2" in result)
        self.assertTrue(result["14:da:e9:04:c8:a3"].valid)
        self.assertTrue(result["64:5a:04:6a:07:a2"].valid)


    def test_get_current_ipv6(self):
        with freeze_time("2015-08-18 17:0:0"):
            leases =  IscDhcpLeases("isc_dhcp_leases/test_files/dhcpd6.leases")
            result = leases.get_current()
            self.assertEqual(len(result), 2)
            self.assertTrue("pd-4dv\352\000\001\000\001\035f\037\342\012\000'\000\000\000" in result)
            self.assertTrue("na-4dv\352\000\001\000\001\035f\037\342\012\000'\000\000\000" in result)

            for key, r in result.items():
                self.assertTrue(r.valid, key)

        with freeze_time("2015-08-18 18:0:0"):
            leases =  IscDhcpLeases("isc_dhcp_leases/test_files/dhcpd6.leases")
            result = leases.get_current()
            self.assertEqual(len(result), 0)