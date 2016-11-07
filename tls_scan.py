#!/usr/bin/env python
# tls-scan - Automated TLS/SSL Server Tests for Multiple Hosts
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v0.0.0, 07/11/2016

import argparse
import atexit
import datetime
import json
import os
import requests
import signal
import socket
import subprocess
import sys
import time

__author__ = 'Artiom Lichtenstein'
__license__ = 'MIT'
__version__ = '0.0.0'

# PID file
strPFile = ''

# Log level to /var/log/messages (or stdout)
intLogLevel = 0
strLogMethod = 'log'
strLogID = '[-v%s-161107-] %s - ' % (__version__, os.path.basename(sys.argv[0]))

# Logger command
strLogger = 'logger -p local0.'
