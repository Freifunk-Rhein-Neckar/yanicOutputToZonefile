# Freifunk: `meshviewer.json` to zonefile

`generateZonefile.py` is a script intended to run regularly as cron and generate a zonefile for 
a subdomain which contains all the Freifunk Router of a Freifunk community so that they are 
accesible with a name.

It uses a http request to get a meshviewer.json, extracts all the valid hostnames 
and outputs a zonefile for a "node domain".


### Hostname Limitations:
+ must only contain letters a-z (or A-Z) and numbers
+ must not start or end with a dashs (-)

### so not valid are:
- spaces ( )
- underscores (_)
- german umlauts (äÖöüÜ) _(maybe in the future)_
- german eszett (ß) _(maybe in the future)_
- ...

