import binascii
import codecs
import datetime
import re
import struct

from six import iteritems


def parse_time(s):
    """
    Like datetime.datetime.strptime(s, "%w %Y/%m/%d %H:%M:%S") but 5x faster.
    """
    _, date_part, time_part = s.split(' ')
    year, mon, day = date_part.split('/')
    hour, minute, sec = time_part.split(':')
    return datetime.datetime(*map(int, (year, mon, day, hour, minute, sec)))


def _extract_prop_option(line):
    """
    Extract the (key,value)-tuple from a string like:
    >>> "option foobar 123"
    :param line:
    :return: tuple (key, value)
    """
    line = line[7:]
    pos = line.find(' ')
    return line[:pos], line[pos + 1:]


def _extract_prop_set(line):
    """
    Extract the (key, value)-tuple from a string like:
    >>> 'set foo = "bar"'
    :param line:
    :return: tuple (key, value)
    """
    token = ' = "'
    line = line[4:]
    pos = line.find(token)
    return line[:pos], line[pos + 4:-1]


def _extract_prop_general(line):
    """
    Extract the (key, value)-tuple from a "standard" property line like:
    >>> 'hardware ethernet 12:34:56:78:90:AB'
    :param line:
    :return: tuple (key, value)
    """
    pos = line.find(' ')
    return line[:pos], line[pos + 1:]


def _extract_properties(config):
    """
    Parse a line within a lease block
    The line should basically match the expression:
    >>> r"\s+(?P<key>(?:option|set)\s+\S+|\S+) (?P<value>[\s\S]+?);"
    For easier seperation of the cases and faster parsing this is done using substrings etc..
    :param config:
    :return: tuple of properties dict, options dict and sets dict
    """
    general, options, sets = {}, {}, {}
    for line in config.splitlines():

        # skip empty & malformed lines
        if not line or not line[-1:] == ';':
            continue

        # strip the trailing ';' and remove any whitespaces on the left side
        line = line[:-1].lstrip()

        # seperate the three cases
        if line[:6] == 'option':
            key, value = _extract_prop_option(line)
            options[key] = value

        elif line[:3] == 'set':
            key, value = _extract_prop_set(line)
            sets[key] = value

        else:
            # fall through to generic case
            key, value = _extract_prop_general(line)
            general[key] = value

    return general, options, sets


class IscDhcpLeases(object):
    """
    Class to parse isc-dhcp-server lease files into lease objects
    """

    regex_leaseblock = re.compile(r"lease (?P<ip>\d+\.\d+\.\d+\.\d+) {(?P<config>[\s\S]+?)\n}")
    regex_leaseblock6 = re.compile(
        r"ia-(?P<type>ta|na|pd) \"(?P<id>[^\"\\]*(?:\\.[^\"\\]*)*)\" {(?P<config>[\s\S]+?)\n}")
    regex_iaaddr = re.compile(r"ia(addr|prefix) (?P<ip>[0-9a-f:]+(/[0-9]+)?) {(?P<config>[\s\S]+?)\n\s+}")

    def __init__(self, filename):
        self.filename = filename

    def get(self):
        """
        Parse the lease file and return a list of Lease instances.
        """
        leases = []
        with open(self.filename) as lease_file:
            lease_data = lease_file.read()
            for match in self.regex_leaseblock.finditer(lease_data):
                block = match.groupdict()

                properties, options, sets = _extract_properties(block['config'])

                if 'hardware' not in properties:
                    # E.g. rows like {'binding': 'state abandoned', ...}
                    continue
                lease = Lease(block['ip'], properties=properties, options=options, sets=sets)
                leases.append(lease)

            for match in self.regex_leaseblock6.finditer(lease_data):
                block = match.groupdict()
                properties, options, sets = _extract_properties(block['config'])

                host_identifier = block['id']
                block_type = block['type']
                last_client_communication = parse_time(properties['cltt'])

                for address_block in self.regex_iaaddr.finditer(block['config']):
                    block = address_block.groupdict()
                    properties, options, sets = _extract_properties(block['config'])

                    lease = Lease6(block['ip'], properties, last_client_communication, host_identifier, block_type,
                                   options=options, sets=sets)
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


class BaseLease(object):
    """
    Base Implementation for all leases. This does most of the common work that is shared among v4 and v6 leases.

    Attributes:
        ip          The IP address assigned by this lease as string
        data        Dict of all the info in the dhcpd.leases file for this lease
        options     Options on this lease
        sets        Dict of key-value set statement values from this lease
    """

    def __init__(self, ip, properties, options=None, sets=None):
        if options is None:
            options = {}

        if sets is None:
            sets = {}

        self.ip = ip
        self.data = properties
        self.options = options
        self.sets = sets
        _, self.binding_state = properties['binding'].split(' ', 1)

    @property
    def active(self):
        """
        Shorthand to check if the binding_state is active
        :return: bool: True if lease is active
        """
        return self.binding_state == 'active'


class Lease(BaseLease):
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

    def __init__(self, ip, properties, options=None, sets=None):
        super(Lease, self).__init__(ip, properties=properties, options=options, sets=sets)

        self.start = parse_time(properties['starts'])
        if properties['ends'] == 'never':
            self.end = None
        else:
            self.end = parse_time(properties['ends'])

        self._hardware = properties['hardware'].split(' ')
        self.ethernet = self._hardware[1]
        self.hardware = self._hardware[0]
        self.hostname = properties.get('client-hostname', '').replace("\"", "")

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

    def __repr__(self):
        return "<Lease {} for {} ({})>".format(self.ip, self.ethernet, self.hostname)

    def __eq__(self, other):
        return self.ip == other.ip and self.ethernet == other.ethernet and self.start == other.start


class Lease6(BaseLease):
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

    def __init__(self, ip, properties, cltt, host_identifier, address_type, options=None, sets=None):
        options = options or {}
        sets = sets or {}

        super(Lease6, self).__init__(ip, properties=properties, options=options, sets=sets)

        self.type = address_type
        self.last_communication = cltt

        self.host_identifier = self._iaid_duid_to_bytes(host_identifier)
        self.iaid = struct.unpack('<I', self.host_identifier[0:4])[0]
        self.duid = self.host_identifier[4:]

        if properties['ends'] == 'never':
            self.end = None
        else:
            self.end = parse_time(properties['ends'])

        self.preferred_life = int(properties['preferred-life'])
        self.max_life = int(properties['max-life'])

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


if __name__ == "__main__":  # pragma: no cover
    leases = IscDhcpLeases('dhcpd.leases')
    print(leases.get_current())
