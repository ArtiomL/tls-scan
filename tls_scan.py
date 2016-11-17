#!/usr/bin/env python
# tls-scan - Automated TLS/SSL Server Tests for Multiple Hosts
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.7, 17/11/2016

import argparse
import json
import lib.cfg as cfg
import lib.log as log
import lib.reapi as reapi
import re
import sys

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.0.7'

# Config file
strCFile = 'tls_scan.json'

# SSL Labs REST API
objSLA = reapi.clsSLA()

# Exit codes
class clsExCodes(object):
	def __init__(self):
		self.error = 1

objExCodes = clsExCodes()


def funDomain(strHost):
	return bool(re.compile(
				r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
				r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
				r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
				r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
			).match(strHost))


def funArgParser():
	objArgParser = argparse.ArgumentParser(
		description = 'Automated TLS/SSL Server Tests for Multiple Hosts',
		epilog = 'https://github.com/ArtiomL/tls-scan')
	objArgParser.add_argument('-f', help ='config file location', dest = 'cfile')
	objArgParser.add_argument('-l', help ='set log level (default: 0)', choices = [0, 1, 2, 3], type = int, dest = 'log')
	objArgParser.add_argument('-v', action ='version', version = '%(prog)s v' + __version__)
	objArgParser.add_argument('HOST', help = 'list of hosts to scan (overrides config file)', nargs = '*')
	return objArgParser.parse_args()


def main():
	global objSLA, strCFile
	objArgs = funArgParser()

	# If run interactively, stdout is used for log messages
	if sys.stdout.isatty():
		log.strLogMethod = 'stdout'

	# Set log level
	if objArgs.log:
		log.intLogLevel = objArgs.log

	# Config file location
	if objArgs.cfile:
		strCFile = objArgs.cfile

	if objArgs.HOST:
		lstHosts = objArgs.HOST


if __name__ == '__main__':
	main()
