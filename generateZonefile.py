#!/usr/bin/python3
import urllib.request
import json
import re
import datetime
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

# get current serial number and increment using yyyymmddXX as format
cdate = datetime.datetime.now().strftime('%Y%m%d')
serial = cdate + "00"
try:
    fn = open(ZONEFILE, "r")
    sn = re.findall('\s*([0-9]{8,12})\s*;\s*Serial\s*', fn.read())
    if len(sn) > 0:
        serial = sn[0]
    fn.close()
except FileNotFoundError:
    pass
if cdate == serial[:8] and serial[8:].isdigit():
    serial = serial[:8] + '{:02d}'.format(int(serial[8:])+1)[:2]
# TODO: more than 100 renews aren't possibly (overflow): therefore it should only run all 15 minutes 25H * (60 Min /15) = 100
# TODO: with the following it simple doesn't renew more then once every 15 Minutes:
# serial = datetime.datetime.now().strftime('%Y%m%d') + str(int((datetime.datetime.today().hour*60+datetime.datetime.today().minute)/15))

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