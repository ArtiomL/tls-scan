# tls-scan - Dockerfile
# https://github.com/ArtiomL/tls-scan
# Artiom Lichtenstein
# v1.0.1, 06/11/2018

FROM alpine

LABEL maintainer="Artiom Lichtenstein" version="1.0.1"

# Core dependencies
RUN apk add --update --no-cache bash bind-tools git python3 && \
	pip3 install --no-cache-dir --upgrade pip && \
	pip3 install --no-cache-dir requests slackclient && \
	pip3 uninstall -y pip setuptools && \
	rm -rf /var/cache/apk/*

# tls-scan
COPY / /opt/tls-scan/
WORKDIR /opt/tls-scan/

# System account and permissions
RUN adduser -u 1001 -D user
RUN chown -RL user: /opt/tls-scan/

# Environment variables
ENV PATH="/opt/tls-scan:${PATH}"

# UID to use when running the image and for CMD
USER 1001

# Run
CMD ["scripts/start.sh"]
