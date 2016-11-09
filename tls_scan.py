#!/usr/bin/env python
# tls-scan - Automated TLS/SSL Server Tests for Multiple Hosts
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.1, 08/11/2016

import argparse
import atexit
import datetime
import json
import lib.cfg as cfg
import lib.log as log
import lib.reapi as reapi
import os
import requests
import signal
import socket
import subprocess
import sys
import time

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.0.1'

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
