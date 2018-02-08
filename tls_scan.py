#!/usr/bin/env python
# tls-scan - Automated TLS/SSL Server Tests for Multiple Hosts
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v1.1.0, 08/02/2018

import argparse
import atexit
import email.mime.text as email
import json
import lib.cfg as cfg
import lib.log as log
import lib.reapi as reapi
import os
import re
import slackclient
import smtplib
import sys
import time

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '1.1.0'

# Config file
strCFile = 'tls_scan.json'

# Log prefix
log.strLogID = '[-v%s-161220-] %s - ' % (__version__, os.path.basename(sys.argv[0]))

# SSL Labs REST API
objSLA = reapi.clsSLA()

# Mail headers
strMFrom = 'tls-scan v%s' % __version__
strMSubj = 'TLS/SSL Scan Report'

# Slack icon
strSIcon = 'https://raw.githubusercontent.com/ArtiomL/tls-scan/master/img/a.png'

# Exit codes
class clsExCodes(object):
	def __init__(self):
		self.cfile = 10
		self.nosrv = 8

objExCodes = clsExCodes()

# Final grades list
lstGrades = []
# Hosts result count
intRCount = 0


def funResult(amStatus):
	# Add grades to list or print assessment JSON
	global lstGrades, intRCount
	if isinstance(amStatus, list):
		for i in amStatus:
			log.funLog(1, i)
		lstGrades.extend(amStatus)
		intRCount += 1
	elif isinstance(amStatus, dict):
		print json.dumps(amStatus, indent = 4)


def funScan(lstHosts, boolCache):
	# Initiate the scan
	strHLen = str(len(lstHosts))
	for i, strHost in enumerate(lstHosts):
		if not boolCache and not objSLA.funAnalyze(strHost):
			# If cached reports aren't allowed (default) - but a new assessment has failed to start
			continue
		funResult(objSLA.funOpStatus(strHost))
		log.funLog(2, '[%s/%s] Done.' % (str(i + 1), strHLen))


def funConScan(lstHosts, boolCache):
	# Concurrent scan
	strHLen = str(len(lstHosts))
	# Split the hosts list into groups of the concurrency size (2D list)
	lstMatrix = [lstHosts[i:i + objSLA.intConc] for i in range(0, len(lstHosts), objSLA.intConc)]
	# Initiate the scan
	for g, lstGroup in enumerate(lstMatrix):
		# New assessment
		if not boolCache:
			for i, strHost in enumerate(lstGroup):
				log.funLog(2, '[%s/%s] Starting...' % (str(g * objSLA.intConc + i +1), strHLen))
				objSLA.funAnalyze(strHost)
				time.sleep(objSLA.intCool)
		# Check status
		intReady = 0
		while intReady < len(lstGroup):
			# Completed assessments counter
			intReady = 0
			time.sleep(objSLA.intPoll)
			for i, strHost in enumerate(lstGroup):
				if strHost.endswith('#'):
					intReady += 1
					continue
				# Non-blocking operation status
				amStatus = objSLA.funOpStatus(strHost, True)
				if amStatus:
					# Mark host as completed
					log.funLog(2, '[%s/%s] Done.' % (str(g * objSLA.intConc + i +1), strHLen))
					lstGroup[i] += '#'
					intReady += 1
					funResult(amStatus)


def funArgParser():
	objArgParser = argparse.ArgumentParser(
		description = 'Automated TLS/SSL Server Tests for Multiple Hosts',
		epilog = 'https://github.com/ArtiomL/tls-scan')
	objArgParser.add_argument('-c', help ='deliver cached assessment reports if available', action = 'store_true', dest = 'cache')
	objArgParser.add_argument('-f', help ='config file location', dest = 'cfile')
	objArgParser.add_argument('-i', help ='show IP addresses (default: first 8 chars of their SHA-256)', action = 'store_true', dest = 'ips')
	objArgParser.add_argument('-j', help ='return assessment JSONs (default: grades), disables -m and -k', action = 'store_true', dest = 'json')
	objArgParser.add_argument('-k', help ='send report to a Slack channel', action = 'store_true', dest = 'slack')
	objArgParser.add_argument('-l', help ='set log level (default: 0)', choices = [0, 1, 2, 3], type = int, dest = 'log')
	objArgParser.add_argument('-m', help ='send report by mail', action = 'store_true', dest = 'mail')
	objArgParser.add_argument('-s', help ='number of simultaneous assessments (default: 1)', choices = range(2, 11), metavar = '[2-10]', type = int, dest = 'conc')
	objArgParser.add_argument('-t', help ='ignore server certificate mismatch', action = 'store_true', dest = 'im')
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

	# Ignore server certificate mismatch
	objSLA.boolIM = objArgs.im

	# Show real IP addresses argument
	objSLA.boolIPs = objArgs.ips

	# Full assessment JSON argument
	objSLA.boolJSON = objArgs.json

	# Config file location
	if objArgs.cfile:
		strCFile = objArgs.cfile

	# Concurrency
	if objArgs.conc:
		objSLA.intConc = objArgs.conc

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

	# Hosts list cleanup (remove invalid domains)
	lstHClean = [strHost for strHost in lstHosts if objSLA.funValid(strHost)]
	if len(lstHosts) > len(lstHClean):
		log.funLog(1, 'Ignoring invalid hostname(s): %s' % ', '.join(list(set(lstHosts) - set(lstHClean))), 'err')
	lstHosts = lstHClean

	# Check SSL Labs availability
	if not objSLA.funInfo(True):
		log.funLog(1, 'SSL Labs unavailable or maximum concurrent assessments exceeded.', 'err')
		sys.exit(objExCodes.nosrv)

	log.funLog(1, 'Scanning %s host(s)... [Cache: %s, Concurrency: %s]' % (str(len(lstHosts)), bool(objArgs.cache), str(objSLA.intConc)))

	# Scan
	if objSLA.intConc > 1:
		# Concurrency
		funConScan(lstHosts, objArgs.cache)
	else:
		funScan(lstHosts, objArgs.cache)

	# Sort the grades in reverse and add line breaks
	strReport = '\r\n'.join(sorted(lstGrades, reverse = True))

	# Send the report to a Slack channel
	if objArgs.slack and not objArgs.json:
		log.funLog(1, 'Slacking the report...')
		try:
			objSlack = slackclient.SlackClient(diCfg['token'].decode('base64'))
			objSlack.api_call('chat.postMessage', username = strMFrom, channel = diCfg['channel'], text = '```\n%s\n```' % strReport, icon_url = strSIcon)
		except Exception as e:
			log.funLog(2, repr(e), 'err')

	# Mail the report
	if objArgs.mail and not objArgs.json:
		# Format MIME message
		objMIME = email.MIMEText('Total Hosts: [%s/%s], Concurrency: %s\r\n%s' % (str(intRCount), str(len(lstHosts)), str(objSLA.intConc), strReport))
		log.funLog(1, 'Mailing the report...')
		try:
			objMIME['From'] = '%s <%s>' % (strMFrom, diCfg['from'])
			# Remove spaces and split recipients into a list delimited by , or ;
			lstTo = re.split(r',|;', diCfg['to'].replace(' ', ''))
			objMIME['To'] = ', '.join(lstTo)
			objMIME['Subject'] = strMSubj
			# Connect to SMTP server
			objMail = smtplib.SMTP(diCfg['server'])
			# Identification
			objMail.ehlo()
			# Encryption
			objMail.starttls()
			# Authentication
			objMail.login(diCfg['user'], diCfg['pass'].decode('base64'))
			# Send mail
			objMail.sendmail(diCfg['from'], lstTo, objMIME.as_string())
			log.funLog(1, 'Success!')
			# Terminate the SMTP session and close the connection
			objMail.quit()
		except Exception as e:
			log.funLog(2, repr(e), 'err')
	else:
		print strReport


def funBadExit(type, value, traceback):
	log.funLog(2, 'Unhandled Exception: %s, %s, %s' % (type, value, traceback))

sys.excepthook = funBadExit


@atexit.register
def funExit():
	log.funLog(1, 'Exiting...')


if __name__ == '__main__':
	main()
