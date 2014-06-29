import re
import datetime


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
        self.start = datetime.datetime.strptime(data['starts'], "%w %Y/%m/%d %H:%M:%S")
        if data['ends'] == 'never':
            self.end = None
        else:
            self.end = datetime.datetime.strptime(data['ends'], "%w %Y/%m/%d %H:%M:%S")

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
