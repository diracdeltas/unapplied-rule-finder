#!/usr/bin/env/python

import subprocess
import os
import threading
from collections import OrderedDict

def clean_url(url):
    """Remove whitespace, ignore page anchors"""
    parts = url.strip().split('#')
    return parts[0]

class Firefox:

    def __init__(self, profiledir=None):
        if profiledir is None:
            self.profile = 'default'
        else:
            profiledir = profiledir.rstrip('/')
            fpath, fext = os.path.splitext(profiledir)
            self.profile = fext.lstrip('.')
        self.p = subprocess.Popen(['firefox', '-no-remote', '-P', self.profile], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        self.flagged_urls = OrderedDict()
        self.lock = threading.Lock()

    def log_process(self):
        """generator that returns stdout line by line as long as p is running"""
        while True:
            ret = self.p.poll()
            if ret is None:
                yield self.p.stdout.readline()
            else:
                break

    def get_urls(self):
        url_flag = 0
        for line in self.log_process():
            if 'Redirection loop' in line:
                url_flag = 1
            else:
                if url_flag == 1:
                    self.lock.acquire()
                    self.flagged_urls[clean_url(line)] = 1
                    if len(self.flagged_urls) > 500:
                        self.flagged_urls.popitem(last=False)
                    self.lock.release()
                url_flag = 0

    def found_redirect(self, url):
        url = clean_url(url)
        self.lock.acquire()
        if url in self.flagged_urls.keys():
            found = True
        else:
            found = False
        self.lock.release()
        return found

