import re
import datetime

def parse_time(s):
    """
    Like datetime.datetime.strptime(s, "%w %Y/%m/%d %H:%M:%S") but 5x faster.
    """
    _, date_part, time_part = s.split(' ')
    year, mon, day = date_part.split('/')
    hour, minute, sec = time_part.split(':')
    return datetime.datetime(*map(int, (year, mon, day, hour, minute, sec)))

class IscDhcpLeases(object):
    def __init__(self, filename):
        self.filename = filename
        self.last_leases = {}

        self.regex_leaseblock = re.compile(r"lease (?P<ip>\d+\.\d+\.\d+\.\d+) {(?P<config>[\s\S]+?)\n}")
        self.regex_properties = re.compile(r"\s+(?P<key>\S+) (?P<value>[\s\S]+?);")

    def get(self):
        leases = []
        for match in self.regex_leaseblock.finditer(open(self.filename).read()):
            block = match.groupdict()

            properties = self.regex_properties.findall(block['config'])
            properties = {key: value for (key, value) in properties}
            if 'hardware' not in properties:
                # E.g. rows like {'binding': 'state abandoned', ...}
                continue
            lease = Lease(block['ip'], properties)
            leases.append(lease)
        return leases

    def get_current(self):
        all_leases = self.get()
        leases = {}
        for lease in all_leases:
            leases[lease.ethernet] = lease
        return leases


class Lease(object):
    def __init__(self, ip, data):
        self.data = data
        self.ip = ip
        self.start = parse_time(data['starts'])
        if data['ends'] == 'never':
            self.end = None
        else:
            self.end = parse_time(data['ends'])

        self._hardware = data['hardware'].split(' ')
        self.ethernet = self._hardware[1]
        self.hardware = self._hardware[0]
        self.hostname = data.get('client-hostname', '').replace("\"", "")

    @property
    def valid(self):
        if self.end is None:
            return self.start <= datetime.datetime.now()
        else:
            return self.start <= datetime.datetime.now() <= self.end

    def __repr__(self):
        return "<Lease {} for {} ({})>".format(self.ip, self.ethernet, self.hostname)


if __name__ == "__main__":
    leases = IscDhcpLeases('dhcpd.leases')
    print(leases.get_current())
