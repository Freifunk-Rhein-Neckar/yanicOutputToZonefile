# Freifunk: `meshviewer.json` to zonefile

`generateZonefile.py` is a script intended to run regularly as cron and generate a zonefile for 
a subdomain which contains all the Freifunk Router of a Freifunk community so that they are 
accesible with a name.

It uses a http request to get a meshviewer.json, extracts all the valid hostnames 
and outputs a zonefile for a "node domain".


### Hostname Limitations:
+ must only contain letters a-z, numbers, german umlauts (äöü)
+ must not start or end with a dash (-)

### not valid are:
- spaces ( )
- underscores (_)
- the german eszett (ß) - due to python rewriting ß with ss ([Issue 17305: IDNA2008 encoding is missing](https://bugs.python.org/issue17305))
- any other character

