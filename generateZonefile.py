#!/usr/bin/python3
import urllib.request
import json
import re
import time
from config import ZONE_TPL, LINE_TPL, ZONEFILE, DOMAIN, HOSTMASTERMAIL, MESHVIEWERJSON, GETWARNINGS

class ffnode:
    def __init__(self, hostname, address, firstseen):
        self.hostname = hostname
        self.address = address
        self.firstseen = firstseen
    def __eq__(self, other):
        if not isinstance(other, ffnode):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.hostname == other.hostname
    def __hash__(self):
        return hash(('hostname', self.hostname))

lines = []
nodes = []
# get the source file
with urllib.request.urlopen(MESHVIEWERJSON) as url:
    data = json.loads(url.read().decode())
    for node in data["nodes"]:
        node["hostnameLower"] = node["hostname"].lower()
        # look if the hostname can formally be a subdomain
        if re.match('^[0-9a-z]([0-9a-z-]{0,38}[0-9a-z])?$', node["hostnameLower"]):
            if "addresses" in node and len(node["addresses"])>=1:
                # loop over all adresses
                for address in node["addresses"]:
                    # don't use unicast addresses or the dns server ip of a gateway
                    if address[:2] != "fe" and address[-4:] !="::53":
                        nodes.append(ffnode(node["hostnameLower"], address, node["firstseen"]))
                        # print("\t\t\t\t" + node["hostnameLower"] + ": " + address)
                        break
                    elif GETWARNINGS:
                        print("false-Addr: \t" + node["hostnameLower"]+" "+address)
                else:
                    if GETWARNINGS:
                        print("no valid addr: \t" + node["hostname"])
            elif GETWARNINGS:
                print("no address: \t" + node["hostnameLower"])
        elif GETWARNINGS:
            print("not valid: \t\t" + node["hostnameLower"])

# remove duplicates
nodes = list(set(nodes))
# TODO: Remove duplicates responsibly, choose firstseen

nodes.sort(key=lambda x: x.hostname)

for node in nodes:
    lines.append(LINE_TPL.format(name=node.hostname, type="AAAA", data=node.address))

# get a serial number
serial = int(time.time())

f = open(ZONEFILE, "w")
f.write(ZONE_TPL.format(
    domainname=DOMAIN,
    hostmastermail=(HOSTMASTERMAIL.replace("@",".")),
    serial=serial,
    ))
f.write('\n'.join(lines) + '\n')
f.close()


# print("----------------------------------")
# f = open(ZONEFILE, "r")
# print(f.read())
# f.close()
# print("----------------------------------")