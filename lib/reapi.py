#!/usr/bin/env python
# tls-scan - lib: REST API
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.3, 12/11/2016

import json
import log
import requests

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
		# 
		self.boolJSON = False

	def funAnalyze(self, strHost):
		# Initiate a new assessment for a host
		try:
			objHResp = self.objHS.get(self.strAPIE + self.strAnalyze + strHost + self.strAnStNew)
			if objHResp.status_code == 200:
				return json.loads(objHResp.content)['statusMessage']

		except Exception as e:
			log.funLog(2, repr(e), 'err')

	def funGrades(self, diOper):
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
			try:
				diOper = json.loads(self.objHS.get(strURL).content)
				strStatus = diOper['status']
				log.funLog(3, 'Transaction status: %s' % strStatus)
				if strStatus == 'READY':
					# Cached result (from 'DNS' to 'READY')
					return diOper if self.boolJSON else self.funGrades(diOper)

				elif strStatus == 'ERROR':
					return ['X %s, %s' % (strHost, diOper['statusMessage'])]

			except Exception as e:
				log.funLog(2, repr(e), 'err')
		lstMessages = [None] * len(diOper['endpoints'])
		log.funLog(2, 'Total number of endpoints: %s' % len(lstMessages))
		while strStatus == 'IN_PROGRESS':
			try:
				diOper = json.loads(self.objHS.get(strURL).content)
				strStatus = diOper['status']
				for i, diEP in enumerate(diOper['endpoints']):
					strStaMess = diEP['statusMessage']
					if strStatus == 'READY':
						strGrade = 'X'
						if strStaMess == 'Ready':
							strGrade = diEP['grade']
						lstMessages[i] = '%s %s, %s, %s' % (strGrade, strHost, diEP['ipAddress'], strStaMess)
					else:
						if strStaMess == 'In progress':
							strDetMess = diEP['statusDetailsMessage']
							if strDetMess != lstMessages[i]:
								lstMessages[i] = strDetMess
								log.funLog(3, '%s, IP: %s, %s' % (strHost, diEP['ipAddress'], lstMessages[i]))
			except Exception as e:
				log.funLog(2, repr(e), 'err')
		return lstMessages
