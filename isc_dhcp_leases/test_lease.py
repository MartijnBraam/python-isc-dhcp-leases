import datetime
from unittest import TestCase
from isc_dhcp_leases.iscdhcpleases import Lease
from freezegun import freeze_time

__author__ = 'Martijn Braam <martijn@brixit.nl>'


class TestLease(TestCase):
    def setUp(self):
        self.lease_data = {
            'starts': '2 2013/12/10 12:57:04',
            'uid': '"\\377\\000\\000\\000\\002\\000\\001\\000\\001\\0321\\301\\300\\000#\\213\\360F\\350"',
            'binding': 'state free',
            'ends': 'never',
            'hardware': 'ethernet 60:a4:4c:b5:6a:dd',
            'cltt': '2 2013/12/10 12:57:04',
            'tstp': '2 2013/12/10 13:07:04',
            'client-hostname': '"Satellite-C700"'
        }

    def test_init(self):
        lease = Lease("192.168.0.1", self.lease_data)
        self.assertEqual(lease.ip, "192.168.0.1")
        self.assertEqual(lease.hardware, "ethernet")
        self.assertEqual(lease.ethernet, "60:a4:4c:b5:6a:dd")
        self.assertEqual(lease.hostname, "Satellite-C700")
        self.assertEqual(
            lease.start, datetime.datetime(2013, 12, 10, 12, 57, 4, tzinfo=datetime.timezone.utc))
        self.assertIsNone(lease.end)
        self.assertTrue(lease.valid)
        self.assertFalse(lease.active)
        self.assertEqual(lease.binding_state, 'free')

    def test_repr(self):
        lease = Lease("192.168.0.1", self.lease_data)
        self.assertEqual(repr(lease), '<Lease 192.168.0.1 for 60:a4:4c:b5:6a:dd (Satellite-C700)>')

    def _test_valid(self, now=None):
        lease = Lease("192.168.0.1", self.lease_data, now=now)
        self.assertTrue(lease.valid)  # Lease is forever

        lease.end = datetime.datetime(2015, 7, 6, 13, 57, 4, tzinfo=datetime.timezone.utc)
        self.assertTrue(lease.valid)  # Lease is within start and end

        lease.end = lease.end - datetime.timedelta(hours=7)
        self.assertFalse(lease.valid)  # Lease is ended

        lease.start = datetime.datetime(2015, 7, 6, 12, 57, 4, tzinfo=datetime.timezone.utc)
        lease.end = lease.start + datetime.timedelta(hours=1)
        self.assertFalse(lease.valid)  # Lease is in the future

    @freeze_time("2015-07-6 8:15:0")
    def test_valid_frozen(self):
        self._test_valid()

    def test_valid_historical(self):
        self._test_valid(
            now=datetime.datetime(2015, 7, 6, 8, 15, 0, tzinfo=datetime.timezone.utc))

    def test_eq(self):
        lease_a = Lease("192.168.0.1", self.lease_data)
        lease_b = Lease("192.168.0.1", self.lease_data)

        self.assertEqual(lease_a, lease_b)

        lease_b.ip = "172.16.42.1"
        self.assertNotEqual(lease_a, lease_b)

        lease_b.ip = "192.168.0.1"
        lease_b.ethernet = "60:a4:4c:b5:6a:de"
        self.assertNotEqual(lease_a, lease_b)

    def test_init_no_starts_property(self):
        self.lease_data.pop('starts')
        lease = Lease("192.168.0.1", self.lease_data)
        self.assertEqual(lease.ip, "192.168.0.1")
        self.assertEqual(lease.hardware, "ethernet")
        self.assertEqual(lease.ethernet, "60:a4:4c:b5:6a:dd")
        self.assertEqual(lease.hostname, "Satellite-C700")
        self.assertIsNone(lease.end)
        self.assertIsNone(lease.start)
        self.assertTrue(lease.valid)
        self.assertFalse(lease.active)
        self.assertEqual(lease.binding_state, 'free')

    @freeze_time("2015-07-6 8:15:0")
    def test_valid_no_starts_property(self):
        self.lease_data.pop('starts')
        lease = Lease("192.168.0.1", self.lease_data)
        self.assertTrue(lease.valid)  # Lease is forever

        lease.end = datetime.datetime(2015, 7, 6, 6, 57, 4, tzinfo=datetime.timezone.utc)
        self.assertFalse(lease.valid)  # Lease is ended

        lease.end = lease.end + datetime.timedelta(hours=3)
        self.assertTrue(lease.valid)  # Lease is not expired

    def test_naive_time(self):
        with self.assertRaises(ValueError):
            Lease("192.168.0.1", self.lease_data, now=datetime.datetime.now())
