#!/bin/sh
# tls-scan - Docker Wrapper Script
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v1.0.0, 06/11/2018

if [[ ! -z "$REPO" ]]; then
	git clone "https://github.com/$REPO.git"
	cd $(echo "$REPO" | cut -d"/" -f2)
fi

exec /bin/sh
