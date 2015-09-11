from unittest import TestCase
from isc_dhcp_leases.iscdhcpleases import Lease6
from freezegun import freeze_time
from datetime import datetime

__author__ = 'Martijn Braam <martijn@brixit.nl>'


class TestLease6(TestCase):
    def setUp(self):
        self.lease_data = {
            'binding': 'state active',
            'ends': 'never',
            'preferred-life': '375',
            'max-life': '600'
        }

    @freeze_time("2015-07-6 8:15:0")
    def test_init(self):
        lease = Lease6("2001:610:600:891d::60", self.lease_data, datetime(2015, 8, 18, 16, 55, 37),
                       "4dv\\352\\000\\001\\000\\001\\035f\\037\\342\\012\\000'\\000\\000\\000", "na")
        self.assertEqual(lease.ip, "2001:610:600:891d::60")

        self.assertEqual(lease.host_identifier, b"4dv\xea\x00\x01\x00\x01\x1df\x1f\xe2\n\x00'\x00\x00\x00")
        self.assertEqual(lease.valid, True)
        self.assertEqual(lease.iaid, 3933627444)
        self.assertEqual(lease.duid, b"\x00\x01\x00\x01\x1df\x1f\xe2\n\x00'\x00\x00\x00")
        self.assertEqual(lease.active, True)
        self.assertEqual(lease.binding_state, 'active')
        self.assertEqual(lease.preferred_life, 375)
        self.assertEqual(lease.max_life, 600)
        self.assertEqual(lease.last_communication, datetime(2015, 8, 18, 16, 55, 37))
        self.assertEqual(lease.type, Lease6.NON_TEMPORARY)

    def test_repr(self):
        lease = Lease6("2001:610:600:891d::60", self.lease_data, datetime(2015, 8, 18, 16, 55, 37),
                       "4dv\\352\\000\\001\\000\\001\\035f\\037\\342\\012\\000'\\000\\000\\000", "na")
        self.assertEqual(repr(lease), '<Lease6 2001:610:600:891d::60>')

    @freeze_time("2015-07-6 8:15:0")
    def test_valid(self):
        lease = Lease6("2001:610:600:891d::60", self.lease_data, datetime(2015, 8, 18, 16, 55, 37),
                       "4dv\\352\\000\\001\\000\\001\\035f\\037\\342\\012\\000'\\000\\000\\000", "na")
        self.assertTrue(lease.valid)  # Lease is forever

        lease.end = datetime(2015, 7, 6, 13, 57, 4)
        self.assertTrue(lease.valid)  # Lease is before end

        lease.end = datetime(2015, 7, 6, 6, 57, 4)
        self.assertFalse(lease.valid)  # Lease is ended

    def test_eq(self):
        lease_a = Lease6("2001:610:600:891d::60", self.lease_data, datetime(2015, 8, 18, 16, 55, 37),
                         "4dv\\352\\000\\001\\000\\001\\035f\\037\\342\\012\\000'\\000\\000\\000", "na")
        lease_b = Lease6("2001:610:600:891d::60", self.lease_data, datetime(2015, 8, 18, 16, 55, 37),
                         "4dv\\352\\000\\001\\000\\001\\035f\\037\\342\\012\\000'\\000\\000\\000", "na")

        self.assertEqual(lease_a, lease_b)

        lease_b.ip = "2001:610:600:891d::42"
        self.assertNotEqual(lease_a, lease_b)

        lease_b.ip = "2001:610:600:891d::60"
        lease_b.host_identifier = "gd4\352\000\001\000\001\035b\037\322\012\000'\000\000\000"
        self.assertNotEqual(lease_a, lease_b)
