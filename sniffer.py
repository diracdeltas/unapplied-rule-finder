#!/usr/bin/env python

import subprocess

def sniffedUrls(interface="wlan0"):
    p = subprocess.Popen(["tshark", "-i", interface, "-p", "port", "80", "-T", "fields", "-e", "http.request.method", "-e", "http.request.full_uri"], stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline().strip()
        if line: yield line.split()[1]
