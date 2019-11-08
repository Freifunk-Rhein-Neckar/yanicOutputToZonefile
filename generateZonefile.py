#!/usr/bin/python3
import urllib.request
import json
import re
import time
from config import ZONE_TPL, LINE_TPL, DOMAIN, HOSTMASTERMAIL, MESHVIEWERJSON, GETWARNINGS

IPv6regex = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"

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
                    if address[:2] != "fe" and address[-4:] !="::53" and re.match(IPv6regex,address):
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

# sort by hostname and after that firstseen. Purpose is to keep only the first apperance of a hostname
nodes.sort(key=lambda x: (x.hostname, x.firstseen))

# remove duplicates from the list
nodes = list(set(nodes))

# sort again, since set doesn't keep the order
nodes.sort(key=lambda x: (x.hostname))

for node in nodes:
    lines.append(LINE_TPL.format(name=node.hostname, type="AAAA", data=node.address))

# get a serial number
serial = int(time.time())

f = open(DOMAIN+".zone", "w")
f.write(ZONE_TPL.format(
    domainname=DOMAIN,
    hostmastermail=(HOSTMASTERMAIL.replace("@",".")+"."),
    serial=serial,
    ))
f.write('\n'.join(lines) + '\n')
f.close()