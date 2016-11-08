#!/usr/bin/env python
# tls-scan - lib: REST API
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.1, 07/11/2016

import json
import requests
import log

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.0.1'

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

	def funAnalyze(self, strHost):
		# Initiate a new assessment for a host
		try:
			objHResp = self.objHS.get(self.strAPIE + self.strAnalyze + strHost + self.strAnStNew)
			if objHResp.status_code == 200:
				return json.loads(objHResp.content)['statusMessage']
		except Exception as e:
			log.funLog(2, repr(e), 'err')

	def funOpStatus(self, strHost):
		# Check operation status
		strURL = self.strAPIE + self.strAnalyze + strHost
		try:
			diOper = json.loads(self.objHS.get(strURL).content)
			strStatus = diOper['status']
			if strStatus == 'ERROR':
				return ['X %s, %s' % (strHost, diOper['statusMessage'])]

			lstMessages = [None] * len(diOper['endpoints'])
			log.funLog(2, 'Total number of endpoints: %s' % len(lstMessages))
		except Exception as e:
			log.funLog(2, repr(e), 'err')
		while strStatus == 'IN_PROGRESS':
			try:
				diOper = json.loads(self.objHS.get(strURL).content)
				strStatus = diOper['status']
				i = 0
				for diEP in diOper['endpoints']:
					strStaMess = diEP['statusMessage']
					if strStatus == 'READY':
						strGrade = 'X'
						if strStaMess == 'Ready':
							strGrade = diEP['grade']
						lstMessages[i] = '%s %s, %s, %s' % (strGrade, strHost, diEP['ipAddress'], strStaMess)
						i += 1
					else:
						if strStaMess == 'In progress':
							strDetMess = diEP['statusDetailsMessage']
							if strDetMess != lstMessages[i]:
								lstMessages[i] = strDetMess
								log.funLog(3, '%s, IP: %s, %s' % (strHost, diEP['ipAddress'], lstMessages[i]))
							i += 1
			except Exception as e:
				log.funLog(2, repr(e), 'err')
		return lstMessages
