#!/usr/bin/python3

ZONE_TPL = """; {domainname}
@ 100 IN SOA ns.ffrn.de. {hostmastermail} (
     {serial:010d}  ; Serial
     120         ; Refresh
     60          ; Retry
     240         ; Expire
     120  )      ; Minimum

@                                        IN NS      ns.ffrn.de.

next                                     IN CNAME   nextnode.ffrn.de.
"""
LINE_TPL = """{name:<40} IN {type:<7} {data}"""

DOMAIN = "nodes.ffrn.de"

# hostnames which aren't allowed (for example next-node)
NOTALLOWED = ["next"]

# dots in the part before the @ need to be escaped: . becomes \.
HOSTMASTERMAIL = "hostmaster@ffrn.de"

# url from where to download the meshviewer.json
MESHVIEWERJSON_URL = "https://map.ffrn.de/data/meshviewer.json"

# local path, only used if MESHVIEWERJSONURL is empty
MESHVIEWERJSON_LOCAL = "/var/www/meshviewer/build/data/meshviewer.json"

GETWARNINGS = True