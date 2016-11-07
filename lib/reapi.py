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
		strStatus = 'IN_PROGRESS'
		lstMessages = []
		while strStatus == 'IN_PROGRESS':
			try:
				diOper = json.loads(self.objHS.get(strURL).content)
				strStatus = diOper['status']
				i = 0
				for diEP in diOper['endpoints']:
					if strStatus == 'READY':
						strIPAddr = diEP['ipAddress']
						strGrade = diEP['grade']
						log.funLog(1, '%s, IP: %s, %s' % (strHost, strIPAddr, strGrade))
					else:
						try:
							strDetMess = diEP['statusDetailsMessage']
							strIPAddr = diEP['ipAddress']
							if strDetMess != lstMessages[i]:
								lstMessages[i] = strDetMess
								log.funLog(3, '%s, IP: %s, %s' % (strHost, strIPAddr, lstMessages[i]))
							i += 1
						except IndexError as e:
							lstMessages.append(strDetMess)
						except KeyError as e:
							pass
			except Exception as e:
				log.funLog(2, repr(e), 'err')
		log.funLog(1, strStatus)
		return strStatus
