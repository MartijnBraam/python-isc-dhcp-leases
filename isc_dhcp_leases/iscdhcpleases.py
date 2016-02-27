import re
import datetime
import codecs
import struct
import binascii


def parse_time(s):
    """
    Like datetime.datetime.strptime(s, "%w %Y/%m/%d %H:%M:%S") but 5x faster.
    """
    _, date_part, time_part = s.split(' ')
    year, mon, day = date_part.split('/')
    hour, minute, sec = time_part.split(':')
    return datetime.datetime(*map(int, (year, mon, day, hour, minute, sec)))


class IscDhcpLeases(object):
    """
    Class to parse isc-dhcp-server lease files into lease objects
    """

    def __init__(self, filename):
        self.filename = filename
        self.last_leases = {}

        self.regex_leaseblock = re.compile(r"lease (?P<ip>\d+\.\d+\.\d+\.\d+) {(?P<config>[\s\S]+?)\n}")
        self.regex_leaseblock6 = re.compile(
            r"ia-(?P<type>ta|na|pd) \"(?P<id>[^\"\\]*(?:\\.[^\"\\]*)*)\" {(?P<config>[\s\S]+?)\n}")
        self.regex_properties = re.compile(r"\s+(?P<key>option\s+\S+|\S+) (?P<value>[\s\S]+?);")
        self.regex_iaaddr = re.compile(r"ia(addr|prefix) (?P<ip>[0-9a-f:]+(/[0-9]+)?) {(?P<config>[\s\S]+?)\n\s+}")

    def get(self):
        """
        Parse the lease file and return a list of Lease instances.
        """
        leases = []
        with open(self.filename) as lease_file:
            lease_data = lease_file.read()
            for match in self.regex_leaseblock.finditer(lease_data):
                block = match.groupdict()

                properties = self.regex_properties.findall(block['config'])
                properties = {key: value for (key, value) in properties}
                if 'hardware' not in properties:
                    # E.g. rows like {'binding': 'state abandoned', ...}
                    continue
                lease = Lease(block['ip'], properties)
                leases.append(lease)

            for match in self.regex_leaseblock6.finditer(lease_data):
                block = match.groupdict()
                properties = self.regex_properties.findall(block['config'])
                properties = {key: value for (key, value) in properties}
                host_identifier = block['id']
                block_type = block['type']
                last_client_communication = parse_time(properties['cltt'])

                for address_block in self.regex_iaaddr.finditer(block['config']):
                    block = address_block.groupdict()
                    properties = self.regex_properties.findall(block['config'])
                    properties = {key: value for (key, value) in properties}

                    lease = Lease6(block['ip'], properties, last_client_communication, host_identifier, block_type)
                    leases.append(lease)

        return leases

    def get_current(self):
        """
        Parse the lease file and return a dict of active and valid Lease instances.
        The key for this dict is the ethernet address of the lease.
        """
        all_leases = self.get()
        leases = {}
        for lease in all_leases:
            if lease.valid and lease.active:
                if type(lease) is Lease:
                    leases[lease.ethernet] = lease
                elif type(lease) is Lease6:
                    leases['%s-%s' % (lease.type, lease.host_identifier_string)] = lease
        return leases


class Lease(object):
    """
    Representation of a IPv4 dhcp lease

    Attributes:
        ip              The IPv4 address assigned by this lease as string
        hardware        The OSI physical layer used to request the lease (usually ethernet)
        ethernet        The ethernet address of this lease (MAC address)
        start           The start time of this lease as DateTime object
        end             The time this lease expires as DateTime object or None if this is an infinite lease
        hostname        The hostname for this lease if given by the client
        binding_state   The binding state as string ('active', 'free', 'abandoned', 'backup')
        data            Dict of all the info in the dhcpd.leases file for this lease
    """

    def __init__(self, ip, data):
        self.data = data
        self.ip = ip
        self.start = parse_time(data['starts'])
        if data['ends'] == 'never':
            self.end = None
        else:
            self.end = parse_time(data['ends'])

        self.options = {}
        for key in data:
            if key.startswith('option '):
                part = key.split(' ')
                self.options[part[1]] = self.data[key]

        self._hardware = data['hardware'].split(' ')
        self.ethernet = self._hardware[1]
        self.hardware = self._hardware[0]
        self.hostname = data.get('client-hostname', '').replace("\"", "")
        self.binding_state = " ".join(data['binding'].split(' ')[1:])

    @property
    def valid(self):
        """
        Checks if the lease is currently valid (not expired and not in the future)
        :return: bool: True if lease is valid
        """
        if self.end is None:
            return self.start <= datetime.datetime.utcnow()
        else:
            return self.start <= datetime.datetime.utcnow() <= self.end

    @property
    def active(self):
        """
        Shorthand to check if the binding_state is active
        :return: bool: True if lease is active
        """
        return self.binding_state == 'active'

    def __repr__(self):
        return "<Lease {} for {} ({})>".format(self.ip, self.ethernet, self.hostname)

    def __eq__(self, other):
        return self.ip == other.ip and self.ethernet == other.ethernet and self.start == other.start


class Lease6(object):
    """
    Representation of a IPv6 dhcp lease

    Attributes:
        ip                 The IPv6 address assigned by this lease as string
        type               If this is a temporary or permanent address
        host_identifier    The unique host identifier (replaces mac addresses in IPv6)
        duid               The DHCP Unique Identifier (DUID) of the host
        iaid               The Interface Association Identifier (IAID) of the host
        last_communication The last communication time with the host
        end                The time this lease expires as DateTime object or None if this is an infinite lease
        binding_state      The binding state as string ('active', 'free', 'abandoned', 'backup')
        preferred_life     The preferred lifetime in seconds
        max_life           The valid lifetime for this address in seconds
        data               Dict of all the info in the dhcpd.leases file for this lease
    """

    (TEMPORARY, NON_TEMPORARY, PREFIX_DELEGATION) = ('ta', 'na', 'pd')

    def __init__(self, ip, data, cltt, host_identifier, address_type):
        self.data = data
        self.ip = ip
        self.type = address_type
        self.last_communication = cltt

        self.host_identifier = self._iaid_duid_to_bytes(host_identifier)
        self.iaid = struct.unpack('<I', self.host_identifier[0:4])[0]
        self.duid = self.host_identifier[4:]

        if data['ends'] == 'never':
            self.end = None
        else:
            self.end = parse_time(data['ends'])

        self.options = {}
        for key in data:
            if key.startswith('option '):
                part = key.split(' ')
                self.options[part[1]] = self.data[key]

        self.preferred_life = int(data['preferred-life'])
        self.max_life = int(data['max-life'])
        self.binding_state = " ".join(data['binding'].split(' ')[1:])

    @property
    def host_identifier_string(self):
        """
        Return the host_identifier as a hexidecimal ascii string
        """
        return binascii.hexlify(self.host_identifier).decode('ascii')

    @property
    def valid(self):
        """
        Checks if the lease is currently valid (not expired)
        :return: bool: True if lease is valid
        """
        if self.end is None:
            return True
        else:
            return datetime.datetime.utcnow() <= self.end

    @property
    def active(self):
        """
        Shorthand to check if the binding_state is active
        :return: bool: True if lease is active
        """
        return self.binding_state == 'active'

    def __repr__(self):
        return "<Lease6 {}>".format(self.ip)

    def __eq__(self, other):
        return self.ip == other.ip and self.host_identifier == other.host_identifier

    def _iaid_duid_to_bytes(self, input_string):
        """
        Parse the IAID_DUID from dhcpd.leases to the bytes representation

        This method doesn't support the colon separated hex format yet.
        """
        result = codecs.decode(input_string, 'unicode_escape').encode('latin-1')
        return result


if __name__ == "__main__":
    leases = IscDhcpLeases('dhcpd.leases')
    print(leases.get_current())
