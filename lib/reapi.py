#!/usr/bin/env python
# tls-scan - lib: REST API
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.6, 18/11/2016

import json
import log
import requests
import time

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.0.6'

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
		# Cool-off period after each new assessment (in sec.)
		self.intSleep = 1
		# Return full assessment JSON (only grades by default)
		self.boolJSON = False

	def funInfo(self):
		# Check availability of SSL Labs servers
		try:
			objHResp = json.loads(self.objHS.get(self.strAPIE + self.strInfo).content)
			self.intSleep = objHResp['newAssessmentCoolOff'] / 1000
			log.funLog(2, 'Cool-off period after each new assessment: %s sec.' % self.intSleep)
			return True if objHResp['currentAssessments'] < objHResp['maxAssessments'] else False

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
					log.funLog(2, 'Request rate too high or service unavailable [%s]! Sleeping for %s sec.' % (str(objHResp.status_code), str(self.intSleep)))
					time.sleep(self.intSleep)
					# Update cool-off period
					self.funInfo()
				elif objHResp.status_code == 200:
					log.funLog(1, 'New assessment started for %s: %s' % (strHost, json.loads(objHResp.content)['status']))
					return True

				else:
					log.funLog(2, 'New assessment failed for %s [%s]' % (strHost, str(objHResp.status_code)))
					return False

			except Exception as e:
				log.funLog(2, repr(e), 'err')
				break

	@staticmethod
	def funGrades(diOper):
		# Parse endpoints to get the grades
		lstGrades = []
		for diEP in diOper['endpoints']:
			strStaMess = diEP['statusMessage']
			strGrade = 'X'
			if strStaMess == 'Ready':
				strGrade = diEP['grade']
			lstGrades.append('[%s] %s, %s, %s' % (strGrade, diOper['host'], diEP['ipAddress'], strStaMess))
		return lstGrades

	def funOpStatus(self, strHost):
		# Check operation status
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
		# Log container for per-endpoint messages
		lstMessages = [None] * len(diOper['endpoints'])
		log.funLog(2, 'Total number of endpoints: %s' % len(lstMessages))
		while strStatus == 'IN_PROGRESS':
			try:
				for i, diEP in enumerate(diOper['endpoints']):
					if diEP['statusMessage'] == 'In progress':
						strDetMess = diEP['statusDetailsMessage']
						if strDetMess != lstMessages[i]:
							lstMessages[i] = strDetMess
							log.funLog(3, '%s, IP: %s, %s' % (strHost, diEP['ipAddress'], lstMessages[i]))
				diOper = json.loads(self.objHS.get(strURL).content)
				strStatus = diOper['status']
			except Exception as e:
				log.funLog(2, repr(e), 'err')
		if strStatus == 'READY':
			return diOper if self.boolJSON else self.funGrades(diOper)

	@staticmethod
	def funDomain(strHost):
		# Validate domain name
		return bool(re.compile(
				r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
				r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
				r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
				r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
			).match(strHost))
