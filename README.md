# Freifunk: `meshviewer.json` to zonefile

`generateZonefile.py` is a script intended to run regularly as cron and generate a zonefile for 
a subdomain which contains all the Freifunk Router of a Freifunk community so that they are 
accesible with a name.

It uses a http request to get a meshviewer.json, extracts all the valid hostnames 
and outputs a zonefile for a "node domain".

## Installation

- clone this repository
- create a copy of the `config.example.py` with the name `config.py`
- run it with `python3 generateZonefile.py`


## Limitations
### Hostname Limitations:
+ must only contain letters a-z, numbers, german umlauts (äöü)
+ must not start or end with a dash (-)

### not valid are:
- spaces ( )
- underscores (_)
- the german eszett (ß) - due to python rewriting ß with ss ([Issue 17305: IDNA2008 encoding is missing](https://bugs.python.org/issue17305))
- any other character


## Example Script

It is probably better to run the following two parts separate:

#### Generate Files
```bash
#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd $DIR

python3 generateZonefile.py > nodes.ffrn.de.log

```

#### reload zone
```bash
#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd $DIR

cp nodes.ffrn.de.zone /etc/bind/zones/
/usr/sbin/rndc reload nodes.ffrn.de > /dev/null
```