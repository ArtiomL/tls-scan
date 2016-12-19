#!/usr/bin/env python
# tls-scan - lib: REST API
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v1.0.3, 20/12/2016

import hashlib
import json
import log
import re
import requests
import time

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '1.0.3'

# SSL Labs REST API
class clsSLA(object):
	def __init__(self):
		# API entry point
		self.strAPIE = 'https://api.ssllabs.com/api/v2/'
		# API call: info
		self.strInfo = 'info'
		# API call: analyze
		self.strAnalyze = 'analyze?publish=off&all=done&host='
		# Parameter to initiate a new assessment
		self.strAnStNew = '&startNew=on'
		# API HTTPS session
		self.objHS = requests.session()
		# Add Content-Type to HTTP headers and modify User-Agent
		self.objHS.headers.update({ 'Content-Type': 'application/json', 'User-Agent': 'tls-scan v%s' % __version__ })
		# Concurrency = number of simultaneous assessments
		self.intConc = 1
		# Cool-off period after each new assessment (in sec.)
		self.intCool = 1
		# Polling interval (in sec.)
		self.intPoll = 5
		# Show IP addresses in reports
		self.boolIPs = False
		# Return full assessment JSON (only grades by default)
		self.boolJSON = False

	def funInfo(self, boolConTune = False):
		# Check availability of SSL Labs servers, adjust concurrency and cool-off period
		try:
			objHResp = json.loads(self.objHS.get(self.strAPIE + self.strInfo).content)
			self.intCool = objHResp['newAssessmentCoolOff'] / 1000
			log.funLog(2, 'Cool-off period after each new assessment: %s sec.' % str(self.intCool))
			intDelta = objHResp['maxAssessments'] - objHResp['currentAssessments']
			if boolConTune and self.intConc > intDelta:
				# Trim concurrency on init
				self.intConc = intDelta
			return True if intDelta > 0 else False

		except Exception as e:
			log.funLog(2, repr(e), 'err')

	def funAnalyze(self, strHost):
		# Initiate a new assessment for a host
		while True:
			try:
				objHResp = self.objHS.get(self.strAPIE + self.strAnalyze + strHost + self.strAnStNew)
				if objHResp.status_code in [429, 503, 529]:
					# 429 - client request rate too high or too many new assessments too fast
					# 503 - the service is not available (e.g. down for maintenance)
					# 529 - the service is overloaded
					log.funLog(2, 'Request rate too high or service unavailable [%s]! Sleeping for %s sec.' % (str(objHResp.status_code), str(self.intCool)))
					# Update cool-off period
					self.funInfo()
					time.sleep(self.intCool)
				elif objHResp.status_code == 200:
					log.funLog(1, 'New assessment started for %s: %s' % (strHost, json.loads(objHResp.content)['status']))
					return True

				else:
					log.funLog(1, 'New assessment failed for %s [%s]' % (strHost, str(objHResp.status_code)))
					return False

			except Exception as e:
				log.funLog(2, repr(e), 'err')
				break

	def funGrades(self, diOper):
		# Parse endpoints to get the grades
		lstGrades = []
		for diEP in diOper['endpoints']:
			strStaMess = diEP['statusMessage']
			strGrade = 'X'
			if strStaMess == 'Ready':
				strGrade = diEP['grade']
			# Show actual endpoint IP address or the first 8 chars of its SHA-256 hash
			strIP = diEP['ipAddress'] if self.boolIPs else hashlib.sha256(diEP['ipAddress']).hexdigest()[:8]
			lstGrades.append('[%s] %s, %s, %s (%s sec.)' % (strGrade, diOper['host'], strIP, strStaMess, str(diEP['duration'] / 1000)))
		return lstGrades

	def funOpStatus(self, strHost, boolAsync = False):
		# Check operation status
		# boolAsync = True: non-blocking, gets current status and exits (returns results only on 'ERROR' or 'READY')
		# boolAsync = False: blocking, loops while 'IN_PROGRESS', exits (with results) only on 'ERROR' or 'READY'
		strStatus = 'DNS'
		strURL = self.strAPIE + self.strAnalyze + strHost
		while strStatus == 'DNS':
			# Initial status
			try:
				diOper = json.loads(self.objHS.get(strURL).content)
				strStatus = diOper['status']
				log.funLog(3, 'Transaction status: %s' % strStatus)
				if strStatus == 'ERROR':
					return ['[X] %s, %s' % (strHost, diOper['statusMessage'])]

			except Exception as e:
				log.funLog(2, repr(e), 'err')
		if not boolAsync:
			# Log container for per-endpoint messages
			lstMessages = [None] * len(diOper['endpoints'])
			log.funLog(2, 'Total number of endpoints: %s' % str(len(lstMessages)))
			while strStatus == 'IN_PROGRESS':
				try:
					if log.intLogLevel >= 3:
						for i, diEP in enumerate(diOper['endpoints']):
							if diEP['statusMessage'] == 'In progress':
								strDetMess = diEP['statusDetailsMessage']
								if strDetMess != lstMessages[i]:
									lstMessages[i] = strDetMess
									# Show actual endpoint IP address or the first 8 chars of its SHA-256 hash
									strIP = diEP['ipAddress'] if self.boolIPs else hashlib.sha256(diEP['ipAddress']).hexdigest()[:8]
									log.funLog(3, '%s, IP: %s, %s' % (strHost, strIP, lstMessages[i]))
					else:
						time.sleep(self.intPoll)
					diOper = json.loads(self.objHS.get(strURL).content)
					strStatus = diOper['status']
				except Exception as e:
					log.funLog(2, repr(e), 'err')
		if strStatus == 'READY':
			log.funLog(1, 'Assessment complete for: %s' % strHost)
			return diOper if self.boolJSON else self.funGrades(diOper)

	@staticmethod
	def funValid(strHost):
		# Validate hostname
		return bool(re.compile(
				r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
				r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
				r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
				r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
			).match(strHost))
