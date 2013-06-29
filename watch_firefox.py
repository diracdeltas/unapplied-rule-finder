#!/usr/bin/env/python

import subprocess
import os

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
        self.flagged_urls = []

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
                        self.flagged_urls.append(line)
                url_flag = 0

    def found_redirect(self, url):
        if url in self.flagged_urls:
            found = True
        else:
            found = False
        return found

    def clear_urls(self):
        del self.flagged_urls[:]
