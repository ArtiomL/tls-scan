#!/usr/bin/env python
# tls-scan - Automated TLS/SSL Server Tests for Multiple Hosts
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.3, 14/11/2016

import argparse
import atexit
import datetime
import json
import lib.cfg as cfg
import lib.log as log
import lib.reapi as reapi
import os
import requests
import signal
import socket
import subprocess
import sys
import time

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.0.3'

# PID file
strPFile = ''

# Config file
strCFile = 'tls_scan.json'

# SSL Labs REST API
objSAPI = reapi.clsSAPI()

# Exit codes
class clsExCodes(object):
	def __init__(self):
		self.error = 1

objExCodes = clsExCodes()


def funArgParser():
	objArgParser = argparse.ArgumentParser(
		description = 'Automated TLS/SSL Server Tests for Multiple Hosts',
		epilog = 'https://github.com/ArtiomL/tls-scan')
	objArgParser.add_argument('-c', help ='config file location', dest = 'cfile')
	objArgParser.add_argument('-l', help ='set log level (default: 0)', choices = [0, 1, 2, 3], type = int, dest = 'log')
	objArgParser.add_argument('-v', action ='version', version = '%(prog)s v' + __version__)
	objArgParser.add_argument('HOST', help = 'list of hosts to scan (overrides config file)', nargs = '*')
	return objArgParser.parse_args()


def main():
	global objSAPI, strPFile, strCFile
	objArgs = funArgParser()

	# If run interactively, stdout is used for log messages
	if sys.stdout.isatty():
		log.strLogMethod = 'stdout'
		log.intLogLevel = 1

	# Set log level
	if objArgs.log > 0:
		log.intLogLevel = objArgs.log

	# Config file location
	if objArgs.cfile:
		strCFile = objArgs.cfile

	if objArgs.HOST:
		lstHosts = objArgs.HOST
