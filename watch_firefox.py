#!/usr/bin/env/python

import subprocess

def log_process(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    while True:
        ret = p.poll()
        if ret is None:
            yield p.stdout.readline()
        else:
            break

for line in log_process(['firefox']):
    if 'Redirection loop' in line:
        print line
