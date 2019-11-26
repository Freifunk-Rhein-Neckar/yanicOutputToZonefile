#!/usr/bin/python3

ZONE_TPL = """; {domainname}
@ 100 IN SOA ns.ffrn.de. {hostmastermail} (
     {serial:010d}  ; Serial
     120         ; Refresh
     60          ; Retry
     240         ; Expire
     120  )      ; Minimum

@                                        IN NS      ns.ffrn.de.

next                                     IN AAAA    2a01:4f8:171:fcff::ffff
"""
LINE_TPL = """{name:<40} IN {type:<7} {data}"""

DOMAIN = "nodes.ffrn.de"

# hostnames which aren't allowed (for example next-node)
NOTALLOWED = ["next"]

# dots in the part before the @ need to be escaped: . becomes \.
HOSTMASTERMAIL = "hostmaster@nodes.ffrn.de"

MESHVIEWERJSON = "https://map.ffrn.de/data/meshviewer.json"

GETWARNINGS = True