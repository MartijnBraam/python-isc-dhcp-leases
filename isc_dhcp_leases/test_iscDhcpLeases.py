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
        self.assertEqual(result[0].sets, {'vendor-class-identifier': 'Some Vendor Identifier'})

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

        leases = IscDhcpLeases("isc_dhcp_leases/test_files/dhcpd6-4.2.4.leases")
        result = leases.get()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].ip, "2001:610:600:891d::60")
        self.assertEqual(result[0].host_identifier, b"4dv\xea\x00\x01\x00\x01\x1df\x1f\xe2\n\x00'\x00\x00\x00")
        self.assertEqual(result[0].iaid, 3933627444)
        self.assertEqual(result[0].duid, b"\x00\x01\x00\x01\x1df\x1f\xe2\n\x00'\x00\x00\x00")
        self.assertEqual(result[0].valid, True)
        self.assertEqual(result[0].active, True)
        self.assertEqual(result[0].binding_state, 'active')
        self.assertEqual(result[0].preferred_life, 375)
        self.assertEqual(result[0].max_life, 600)
        self.assertEqual(result[0].last_communication, datetime(2015, 8, 18, 16, 55, 37))
        self.assertEqual(result[0].type, Lease6.NON_TEMPORARY)

        self.assertEqual(result[1].ip, "2001:610:500:fff::/64")
        self.assertEqual(result[1].host_identifier, b"4dv\xea\x00\x01\x00\x01\x1df\x1f\xe2\n\x00'\x00\x00\x00")
        self.assertEqual(result[1].iaid, 3933627444)
        self.assertEqual(result[1].duid, b"\x00\x01\x00\x01\x1df\x1f\xe2\n\x00'\x00\x00\x00")
        self.assertEqual(result[1].valid, True)
        self.assertEqual(result[1].active, True)
        self.assertEqual(result[1].binding_state, 'active')
        self.assertEqual(result[1].preferred_life, 175)
        self.assertEqual(result[1].max_life, 200)
        self.assertEqual(result[1].last_communication, datetime(2015, 8, 18, 16, 55, 40))
        self.assertEqual(result[1].type, Lease6.PREFIX_DELEGATION)

        leases = IscDhcpLeases("isc_dhcp_leases/test_files/dhcpd6-4.3.3.leases")
        result = leases.get()
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].ip, "2001:10:10::106")
        self.assertEqual(result[0].host_identifier, b"\001\000\000\000\000\001\000\001\034\367\020\245\000'\"3+4")
        self.assertEqual(result[0].iaid, 1)
        self.assertEqual(result[0].duid, b"\x00\x01\x00\x01\x1c\xf7\x10\xa5\x00\'\"3+4")
        self.assertEqual(result[0].valid, True)
        self.assertEqual(result[0].active, True)
        self.assertEqual(result[0].binding_state, 'active')
        self.assertEqual(result[0].preferred_life, 540)
        self.assertEqual(result[0].max_life, 864)
        self.assertEqual(result[0].last_communication, datetime(2016, 1, 6, 14, 50, 34))
        self.assertEqual(result[0].type, Lease6.NON_TEMPORARY)
        self.assertEqual(result[0].sets, dict(iana='2001:10:10:0:0:0:0:106', clientduid='0100011cf710a5002722332b34'))

        self.assertEqual(result[1].ip, "2001:10:30:ff00::/56")
        self.assertEqual(result[1].host_identifier, b"\x00\x00\x00\x00\x00\x01\x00\x01\x1d4L\x00\x00%\x90k\xa14")
        self.assertEqual(result[1].iaid, 0)
        self.assertEqual(result[1].duid, b"\x00\x01\x00\x01\x1d4L\x00\x00%\x90k\xa14")
        self.assertEqual(result[1].valid, True)
        self.assertEqual(result[1].active, True)
        self.assertEqual(result[1].binding_state, 'active')
        self.assertEqual(result[1].preferred_life, 540)
        self.assertEqual(result[1].max_life, 864)
        self.assertEqual(result[1].last_communication, datetime(2016, 1, 6, 14, 52, 37))
        self.assertEqual(result[1].type, Lease6.PREFIX_DELEGATION)
        self.assertEqual(result[1].sets, dict(iapd='2001:10:30:ff00:0:0:0:0', pdsize='56',
                                              pdnet='2001:10:30:ff00:0:0:0:0/56',
                                              clientduid='0100011d344c000025906ba134'))

        leases = IscDhcpLeases("isc_dhcp_leases/test_files/options.leases")
        result = leases.get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].ip, "10.10.10.10")
        self.assertEqual(result[0].valid, False)
        self.assertEqual(result[0].active, True)
        self.assertEqual(result[0].binding_state, 'active')
        self.assertEqual(result[0].hardware, "ethernet")
        self.assertEqual(result[0].ethernet, "24:65:11:d9:a6:b3")
        self.assertEqual(result[0].hostname, "KRONOS")
        self.assertEqual(result[0].start, datetime(2016, 2, 27, 7, 11, 41))
        self.assertEqual(result[0].end, datetime(2016, 2, 27, 9, 11, 41))
        self.assertEqual(len(result[0].options), 4)
        self.assertDictEqual(result[0].options,
                             {'agent.DOCSIS-device-class': '2',
                              'agent.circuit-id': '0:1:3:e9',
                              'agent.remote-id': 'a4:a2:4a:33:db:e5',
                              'agent.unknown-9': '0:0:11:8b:6:1:4:1:2:3:0'})

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
            leases = IscDhcpLeases("isc_dhcp_leases/test_files/dhcpd6-4.2.4.leases")
            result = leases.get_current()
            self.assertEqual(len(result), 2)
            self.assertIn('na-346476ea000100011d661fe20a0027000000', result)
            self.assertIn('pd-346476ea000100011d661fe20a0027000000', result)

            for key, r in result.items():
                self.assertTrue(r.valid, key)

        with freeze_time("2015-08-18 18:0:0"):
            leases = IscDhcpLeases("isc_dhcp_leases/test_files/dhcpd6-4.2.4.leases")
            result = leases.get_current()
            self.assertEqual(len(result), 0)
