#!/usr/bin/env python

import subprocess

def sniffedUrls(interface="wlan0"):
    p = subprocess.Popen(["tshark", "-i", interface, "-p", "port", "80", "-T", "fields", "-e", "http.request.method", "-e", "http.request.full_uri", "-e", "http.user_agent"], stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline().strip()
        if line:
            agent = line.split()[2:]
            if any(map(lambda x: 'Firefox' in x, agent)):
                yield line.split()[1]
