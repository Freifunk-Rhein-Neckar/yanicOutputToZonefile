#!/usr/bin/python3
import urllib.request
import json
import re
import time
from config import ZONE_TPL, LINE_TPL, DOMAIN, HOSTMASTERMAIL, MESHVIEWERJSON_URL, MESHVIEWERJSON_LOCAL, GETWARNINGS, \
    NOTALLOWED

IPv6regex = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
ISO8601regex = "^(?:[1-9]\d{3}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1\d|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[1-9]\d(?:0[48]|[2468][048]|[13579][26])|(?:[2468][048]|[13579][26])00)-02-29)T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:Z|[+-][01]\d:?[0-5]\d)$"


class FFNode:
    def __init__(self, hostname, address, firstseen):
        self.hostname = hostname
        self.address = address
        self.firstseen = firstseen

    def __eq__(self, other):
        if not isinstance(other, FFNode):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.hostname == other.hostname

    def __hash__(self):
        return hash(('hostname', self.hostname))


def warning(*args, sep=' ', end='\n', file=None):
    if GETWARNINGS:
        print(*args, sep=sep, end=end, file=file)


def get_json_from_url(url):
    with urllib.request.urlopen(url) as url:
        return json.loads(url.read().decode())


def get_json_from_file(path):
    with urllib.request.urlopen(path) as url:
        return json.loads(url.read().decode())


def main():
    lines = []
    nodes = []

    # get the data
    if MESHVIEWERJSON_URL != "":
        data = get_json_from_url(MESHVIEWERJSON_URL)
    else:
        data = get_json_from_file(MESHVIEWERJSON_LOCAL)

    for node in data["nodes"]:
        node["hostnameLower"] = node["hostname"].lower()
        # look if the hostname can formally be a subdomain
        node = generate_node_hostname(node)
        if node:
            nodes.append(node)

    # sort by hostname and after that firstseen. Purpose is to keep only the first apperance of a hostname
    nodes.sort(key=lambda x: (x.hostname, x.firstseen))

    # remove duplicates from the list
    nodes = list(set(nodes))

    # sort again, since set doesn't keep the order
    nodes.sort(key=lambda x: x.hostname)

    hostname_list = []
    for node in nodes:
        lines.append(LINE_TPL.format(name=node.hostname, type="AAAA", data=node.address))
        hostname_list.append(node.hostname)

    # get a serial number
    serial = int(time.time())

    # save json file with all generated subdomains
    f = open(DOMAIN + ".json", "w")
    f.write(json.dumps({"timestamp": serial, "domain": DOMAIN, "nodes": hostname_list}))
    f.close()

    # save zone file for bind
    f = open(DOMAIN + ".zone", "w")
    f.write(ZONE_TPL.format(
        domainname=DOMAIN,
        hostmastermail=(HOSTMASTERMAIL.replace("@", ".") + "."),
        serial=serial,
    ))
    f.write('\n'.join(lines) + '\n')
    f.close()


def generate_node_hostname(node):
    if not re.match("^[0-9a-zäöü]([0-9a-zäöü-]{0,38}[0-9a-zäöü])?$", node["hostnameLower"]):
        # Really dirty workaround for python3.5 under Debian 9 which seems to run into a problem with ß
        warning("not valid: \t", end='')
        warning(repr(node["hostnameLower"].encode())[2:-1])
        return

    node["hostnameLower"] = node["hostnameLower"].encode('idna').decode('utf-8')
    # Check if address field exists and contains at least one address
    if "addresses" not in node or len(node["addresses"]) < 1:
        warning("no address: \t" + node["hostnameLower"])
        return

    if not node["addresses"]:
        warning("no valid addr: \t" + node["hostname"])
        return

    # Loop over all addresses
    for address in node["addresses"]:
        # Don't use unicast addresses or the dns server ip of a gateway
        if address[:2] == "fe" \
                or address[:2] == "fd" \
                or address[-4:] == "::53" \
                or not re.match(IPv6regex, address):
            warning("false-Addr: \t" + node["hostnameLower"] + " " + address)
            continue

        # Check if firstseen ist valid ISO 8601
        if not re.match(ISO8601regex, node["firstseen"]):
            warning("false-fseen: \t" + node["hostnameLower"] + " " + node["firstseen"])
            continue

        # Check if nodename isn't in list of not allowed names
        if node["hostnameLower"] in NOTALLOWED:
            warning("not allowed: \t" + node["hostnameLower"] + " " + node["firstseen"])
            return

        return FFNode(node["hostnameLower"], address, node["firstseen"])


if __name__ == "__main__":
    main()
