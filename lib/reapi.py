#!/usr/bin/env python
# tls-scan - lib: REST API
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.3, 13/11/2016

import json
import log
import requests
import time

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.0.3'

# SSL Labs REST API
class clsSAPI(object):
	def __init__(self):
		# API entry point
		self.strAPIE = 'https://api.ssllabs.com/api/v2/'
		# API call: analyze
		self.strAnalyze = 'analyze?publish=off&all=done&host='
		# Parameter to initiate a new assessment
		self.strAnStNew = '&startNew=on'
		# API HTTPS session
		self.objHS = requests.session()
		# Add Content-Type to HTTP headers and modify User-Agent
		self.objHS.headers.update({ 'Content-Type': 'application/json', 'User-Agent': 'tls-scan v%s' % __version__ })
		# Return full assessment JSON (only grades by default)
		self.boolJSON = False

	def funAnalyze(self, strHost):
		# Initiate a new assessment for a host
		intSleep = 0
		while True:
			try:
				objHResp = self.objHS.get(self.strAPIE + self.strAnalyze + strHost + self.strAnStNew)
				if objHResp.status_code == 429:
					# Request rate too high
					intSleep += 1
					time.sleep(intSleep)
				elif objHResp.status_code == 200:
					log.funLog(1, 'New assessment started for %s: %s' % (strHost, json.loads(objHResp.content)['statusMessage']))
					return True

			except Exception as e:
				log.funLog(2, repr(e), 'err')

	def funGrades(self, diOper):
		# Parse endpoints to get the grades
		lstGrades = []
		for diEP in diOper['endpoints']:
			strStaMess = diEP['statusMessage']
			strGrade = 'X'
			if strStaMess == 'Ready':
				strGrade = diEP['grade']
			lstGrades.append('%s %s, %s, %s' % (strGrade, diOper['host'], diEP['ipAddress'], strStaMess))
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
					return ['X %s, %s' % (strHost, diOper['statusMessage'])]

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
