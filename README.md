# <img align="center" src="img/a.png" height="64">&nbsp;&nbsp;tls-scan
[![Releases](https://img.shields.io/github/release/ArtiomL/tls-scan.svg)](https://github.com/ArtiomL/tls-scan/releases)
[![Commits](https://img.shields.io/github/commits-since/ArtiomL/tls-scan/v0.0.1.svg?label=commits%20since)](https://github.com/ArtiomL/tls-scan/commits/master)
[![Maintenance](https://img.shields.io/maintenance/yes/2016.svg)](https://github.com/ArtiomL/tls-scan/graphs/code-frequency)
[![Issues](https://img.shields.io/github/issues/ArtiomL/tls-scan.svg)](https://github.com/ArtiomL/tls-scan/issues)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

<br>
## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Logging](#logging)
- [Help](#--help)
- [License](LICENSE)

<br>
## Description

Automated TLS/SSL server tests for multiple hosts using the SSL Labs [API](https://github.com/ssllabs/ssllabs-scan/blob/stable/ssllabs-api-docs.md).

<br>
## Installation
```shell
git clone https://github.com/ArtiomL/tls-scan.git
```

<br>
## Logging
All logging is **disabled** by default. Please use the `-l {0,1,2,3}` argument to set the required verbosity.<br>
Alternatively, this is controlled by the `intLogLevel` variable of the [log](/lib/log.py) library:
```python
# Log level to /var/log/messages (or stdout)
intLogLevel = 0
```
If run interactively, **_stdout_** is used for log messages, otherwise `/var/log/messages` will be used.

<br>
## --help
```
usage: tls.py [-h] [-f CFILE] [-l {0,1,2,3}] [-v] [HOST [HOST ...]]

Automated TLS/SSL Server Tests for Multiple Hosts

positional arguments:
  HOST          list of hosts to scan (overrides config file)

optional arguments:
  -h, --help    show this help message and exit
  -f CFILE      config file location
  -l {0,1,2,3}  set log level (default: 0)
  -v            show program's version number and exit

https://github.com/ArtiomL/tls-scan
```
