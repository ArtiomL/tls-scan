#!/usr/bin/env python
# tls-scan - Automated TLS/SSL Server Tests for Multiple Hosts
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.1.3, 23/11/2016

import argparse
import json
import lib.cfg as cfg
import lib.log as log
import lib.reapi as reapi
import re
import smtplib
import sys

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.1.3'

# Config file
strCFile = 'tls_scan.json'

# SSL Labs REST API
objSLA = reapi.clsSLA()

# Exit codes
class clsExCodes(object):
	def __init__(self):
		self.cfile = 10
		self.nosrv = 8

objExCodes = clsExCodes()

# Final grades list
lstGrades = []

# Mail headers
strMHead = ""

def funResult(amStatus):
	global lstGrades
	if isinstance(amStatus, list):
		for i in amStatus:
			log.funLog(1, i)
		lstGrades.extend(amStatus)
	elif isinstance(amStatus, dict):
		print json.dumps(amStatus, indent = 4)


def funArgParser():
	objArgParser = argparse.ArgumentParser(
		description = 'Automated TLS/SSL Server Tests for Multiple Hosts',
		epilog = 'https://github.com/ArtiomL/tls-scan')
	objArgParser.add_argument('-c', help ='deliver cached assessment reports if available', action = 'store_true', dest = 'cache')
	objArgParser.add_argument('-f', help ='config file location', dest = 'cfile')
	objArgParser.add_argument('-j', help ='return assessment JSONs (default: grades only), disables -m', action = 'store_true', dest = 'json')
	objArgParser.add_argument('-l', help ='set log level (default: 0)', choices = [0, 1, 2, 3], type = int, dest = 'log')
	objArgParser.add_argument('-m', help ='send report by mail', action = 'store_true', dest = 'mail')
	objArgParser.add_argument('-v', action ='version', version = '%(prog)s v' + __version__)
	objArgParser.add_argument('HOST', help = 'list of hosts to scan (overrides config file)', nargs = '*')
	return objArgParser.parse_args()


def main():
	global objSLA, strCFile, lstGrades, strMHead
	objArgs = funArgParser()

	# If run interactively, stdout is used for log messages (unless -j is set)
	if sys.stdout.isatty() and not objArgs.json:
		log.strLogMethod = 'stdout'

	# Set log level
	if objArgs.log:
		log.intLogLevel = objArgs.log

	# Full assessment JSON argument
	objSLA.boolJSON = objArgs.json

	# Config file location
	if objArgs.cfile:
		strCFile = objArgs.cfile

	# Read config file
	diCfg = cfg.funReadCfg(strCFile)
	try:
		lstHosts = diCfg['hosts']
	except Exception as e:
		log.funLog(1, 'Invalid config file: %s' % strCFile, 'err')
		log.funLog(2, repr(e), 'err')
		sys.exit(objExCodes.cfile)


	# List of hosts to scan (override)
	if objArgs.HOST:
		lstHosts = objArgs.HOST

	if not objSLA.funInfo():
		log.funLog(1, 'SSL Labs unavailable or maximum concurrent assessments exceeded.', 'err')
		sys.exit(objExCodes.nosrv)


	for i in lstHosts:
		if not objSLA.funValid(i):
			log.funLog(1, 'Invalid hostname: %s' % i, 'err')
			continue
		if not objArgs.cache and not objSLA.funAnalyze(i):
			continue
		funResult(objSLA.funOpStatus(i))

	strReport = '\r\n'.join(sorted(lstGrades, reverse = True))

	if objArgs.mail and not objArgs.json:
		try:
			objMail = smtplib.SMTP(diCfg['server'])
			objMail.ehlo()
			objMail.starttls()
			objMail.login(diCfg['user'], diCfg['pass'].decode('base64'))
			lstTo = re.split(r',|;', diCfg['to'].replace(' ', ''))
			strMHead = 'From: tls-scan v%s<%s>\nSubject: TLS/SSL Scan Report\n\nTotal Hosts Submitted: %s\n' % (__version__, diCfg['from'], str(len(lstHosts)))
			objMail.sendmail(diCfg['from'], lstTo, strMHead + strReport)
			objMail.quit()
		except Exception as e:
			log.funLog(2, repr(e), 'err')
	else:
		print strReport


if __name__ == '__main__':
	main()
