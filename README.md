# <img align="center" src="img/a.png" height="64">&nbsp;&nbsp;tls-scan
[![Releases](https://img.shields.io/github/release/ArtiomL/tls-scan.svg)](https://github.com/ArtiomL/tls-scan/releases)
[![Commits](https://img.shields.io/github/commits-since/ArtiomL/tls-scan/v1.0.6.svg?label=commits%20since)](https://github.com/ArtiomL/tls-scan/commits/master)
[![Maintenance](https://img.shields.io/maintenance/yes/2017.svg)](https://github.com/ArtiomL/tls-scan/graphs/code-frequency)
[![Issues](https://img.shields.io/github/issues/ArtiomL/tls-scan.svg)](https://github.com/ArtiomL/tls-scan/issues)
[![Build Status](https://img.shields.io/travis/ArtiomL/tls-scan.svg)](https://travis-ci.org/ArtiomL/tls-scan)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

&nbsp;&nbsp;

## Table of Contents
- [Description](#description)
- [Installation](#installation)
	- [Dependencies](#dependencies)
	- [Git](#git)
	- [tls_scan.json](#tls_scanjson)
	- [tls_scan.py](#tls_scanpy)
- [Logging](#logging)
- [Help](#--help)
- [License](LICENSE)

&nbsp;&nbsp;

## Description

Automated TLS/SSL server tests for multiple hosts using the [SSL Labs](https://www.ssllabs.com/ssltest/) REST [API](https://github.com/ssllabs/ssllabs-scan/blob/stable/ssllabs-api-docs.md).

The code in this repository allows you to scan a list of public TLS/SSL web servers for certificate issues, protocol and cipher suite support, crypto vulnerabilities [etc](https://github.com/ssllabs/research/wiki/SSL-Server-Rating-Guide).

Running (*up to* **_10_**) concurrent assessments is supported (`-s`), but please keep down the number of concurrent assessments to a minimum. If you're not in a hurry, test only one hostname at a time (default).

The grade report can then be sent by mail (`-m`) or written to **_stdout_**:

```
[A+] artioml.net, 0e411f05, Ready (121 sec.)
```

Endpoint IP addresses are obfuscated with the first 8 chars of their SHA-256 hash by default (`-i` to show).

Printing full assessment JSONs is also supported (`-j`).

&nbsp;&nbsp;

## Installation
### Dependencies
[Requests](http://docs.python-requests.org/en/master/user/install/#install) HTTP library:
```shell
pip install requests
```
### Git
```shell
git clone https://github.com/ArtiomL/tls-scan.git
```
or [download](https://github.com/ArtiomL/tls-scan/archive/master.zip).

### [tls_scan.json](tls_scan.json)
To be able to send the report by mail (`-m`) [tls_scan.py](tls_scan.py) must be provided with SMTP credentials. The same [config file](tls_scan.json) is used to specify a list of hosts to scan:
```json
{
	"server": "smtp.gmail.com:587",
	"user": "marla@gmail.com",
	"pass": "d293TXVjaEZha2Ux",
	"from": "marla@gmail.com",
	"to": "tyler@gmail.com; chloe@gmail.com",
	"hosts": [
		"example.com",
		"example.net",
		"example.org"
	]
}
```
Schema:

| Attribute  | Value           |
| :--------- |:--------------- |
| server     | SMTP server host:port |
| user       | username |
| pass       | password ([base64-encoded](https://github.com/ArtiomL/tls-scan/issues/17#issuecomment-286020627)) |
| from       | from-address string ([RFC 822](https://tools.ietf.org/html/rfc822.html)) |
| to         | to-address(es) - delimit with `;` |
| hosts      | list of hosts to scan |

&nbsp;&nbsp;

The config file path is controlled by the `-f` command line argument or the `strCFile` global variable (in [tls_scan.py](tls_scan.py)):
```python
# Config file
strCFile = 'tls_scan.json'
```
### [tls_scan.py](tls_scan.py)
This is the actual scan / report logic.
&nbsp;&nbsp;

Run this program with command-line [arguments](#--help) relevant to your use case. For example:
```shell
chmod u+x tls_scan.py
./tls_scan.py -f tls_scan.json -i -l2 -m -s3
```
Using cron (or a similar time-based job scheduler) to perform recurring, periodic scans is recommended.

&nbsp;&nbsp;

## Logging
All logging is **disabled** by default. Please use the `-l {0,1,2,3}` argument to set the required verbosity.
&nbsp;&nbsp;

Alternatively, this is controlled by the `intLogLevel` variable of the [log](/lib/log.py) library:
```python
# Log level to /var/log/messages (or stdout)
intLogLevel = 0
```
If run interactively, **_stdout_** is used for log messages (unless `-j` is set), otherwise `/var/log/messages` will be used.

&nbsp;&nbsp;

## --help
```
./tls_scan.py --help
usage: tls_scan.py [-h] [-c] [-f CFILE] [-i] [-j] [-l {0,1,2,3}] [-m]
                   [-s [2-10]] [-t] [-v]
                   [HOST [HOST ...]]

Automated TLS/SSL Server Tests for Multiple Hosts

positional arguments:
  HOST          list of hosts to scan (overrides config file)

optional arguments:
  -h, --help    show this help message and exit
  -c            deliver cached assessment reports if available
  -f CFILE      config file location
  -i            show IP addresses (default: first 8 chars of their SHA-256)
  -j            return assessment JSONs (default: grades only), disables -m
  -l {0,1,2,3}  set log level (default: 0)
  -m            send report by mail
  -s [2-10]     number of simultaneous assessments (default: 1)
  -t            ignore server certificate mismatch
  -v            show program's version number and exit

https://github.com/ArtiomL/tls-scan
```
