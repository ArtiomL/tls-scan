#!/usr/bin/env python
# tls-scan - lib: Config File R/W
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v1.0.1, 25/08/2018

import json
import lib.log as log
import os

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '1.0.1'

def funReadCfg(strCFile):
	# Read external config file
	if not os.path.isfile(strCFile):
		log.funLog(1, 'Config file: %s is missing.' % strCFile, 'err')
		return {}

	try:
		# Open the config file
		with open(strCFile, 'r') as f:
			return json.load(f)

	except Exception as e:
		log.funLog(2, repr(e), 'err')
		return {}
