#!/usr/bin/env python
# tls-scan - Automated TLS/SSL Server Tests for Multiple Hosts
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.3, 14/11/2016

import argparse
import atexit
import json
import lib.cfg as cfg
import lib.log as log
import lib.reapi as reapi
import os
import signal
import sys

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



	# eMonitor mode
	try:
		# Remove IPv6/IPv4 compatibility prefix (LTM passes addresses in IPv6 format)
		strRIP = objArgs.IP.strip(':f')
		# Verify first positional argument is a valid (peer) IP address
		socket.inet_pton(socket.AF_INET, strRIP)
	except (AttributeError, socket.error) as e:
		funLog(0, 'No valid peer IP! (use --help)', 'err')
		funLog(2, repr(e), 'err')
		sys.exit(objExCodes.rip)

	# Verify second positional argument is a valid TCP port, set to 443 if not
	strRPort = str(objArgs.PORT)
	if not 0 < objArgs.PORT <= 65535:
		funLog(1, 'No valid peer TCP port, using 443.', 'warning')
		strRPort = '443'

	# PID file
	strPFile = '_'.join(['/var/run/', os.path.basename(sys.argv[0]), strRIP, strRPort + '.pid'])
	# PID
	strPID = str(os.getpid())

	funLog(2, 'PIDFile: %s, PID: %s' % (strPFile, strPID))

	# Kill the last instance of this monitor if hung
	if os.path.isfile(strPFile):
		try:
			os.kill(int(file(strPFile, 'r').read()), signal.SIGKILL)
			funLog(1, 'Killed the last hung instance of this monitor.', 'warning')
		except OSError:
			pass

	# Record current PID
	file(strPFile, 'w').write(str(os.getpid()))

	# Health monitor
	try:
		objHResp = requests.head(''.join(['https://', strRIP, ':', strRPort]), verify = False)
		if objHResp.status_code == 200:
			os.remove(strPFile)
			# Any standard output stops the script from running. Clean up any temporary files before the standard output operation
			funLog(2, 'Peer: %s is up.' % strRIP)
			print 'UP'
			sys.exit()

	except requests.exceptions.RequestException as e:
		funLog(2, repr(e), 'err')

	# Peer down, ARM action required
	funLog(1, 'Peer down, ARM action required.', 'warning')
	funRunAuth()

	if funCurState([funLocIP(strRIP), strRIP]) == 'Standby':
		funLog(1, 'We\'re Standby in ARM, Active peer down. Trying to failover...', 'warning')
		funFailover()

	sys.exit(1)


@atexit.register
def funExit():
	try:
		os.remove(strPFile)
		funLog(2, 'PIDFile: %s removed on exit.' % strPFile)
	except OSError:
		pass
	funLog(1, 'Exiting...')


if __name__ == '__main__':
	main()
