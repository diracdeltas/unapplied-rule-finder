#!/usr/bin/env python

import sys
import os
import glob
import logging
import threading
import time

from lxml import etree

from rules import Ruleset
from rule_trie import RuleTrie

from sniffer import sniffedUrls

from watch_firefox import Firefox

if os.getuid():
   sys.stderr.write("must be run as root to capture packets\n")
   sys.exit(1)

if len(sys.argv) > 1:
    profiledir = sys.argv[1]
else:
    defaults = glob.glob(os.path.expanduser("~/.mozilla/firefox/*default"))
    if len(defaults) == 1:
        profiledir = defaults[0]
        sys.stderr.write("using default Firefox profile %s\n" % profiledir)
    else:
        sys.stderr.write("must specify a Firefox profile directory\n")
        sys.exit(1)

if len(sys.argv) > 2:
    interface = sys.argv[2]
else:
    interface = "wlan0"
    sys.stderr.write("using default interface wlan0\n")

def alert():
    #os.system("play /usr/share/gnome-games/sounds/crash.ogg")
    os.system("canberra-gtk-play --file /usr/share/sounds/gnome/default/alerts/sonar.ogg") # works on ubuntu

defaultpath = "extensions/https-everywhere@eff.org/chrome/content/rules/default.rulesets"
# ruledir = "./rules"
# xmlFnames = glob.glob(os.path.join(ruledir, "*.xml"))
trie = RuleTrie()

try:
    default_rulesets = file(os.path.join(profiledir, defaultpath))
except:
    sys.stderr.write("cannot read rulesets from Firefox profile directory %s\n" % profiledir)
    sys.exit(1)

count = 0
sys.stderr.write("reading rulesets... ")
for xmlRuleset in etree.parse(default_rulesets).getroot().iterchildren():
    ruleset = Ruleset(xmlRuleset, xmlRuleset.attrib["f"])
    if ruleset.defaultOff:
        logging.debug("Skipping rule '%s', reason: %s", ruleset.name, ruleset.defaultOff)
        continue
    trie.addRuleset(ruleset)
    count += 1

sys.stderr.write("added %d rulesets\n" % count)

def find_unapplied_rules():
    theUrls = sniffedUrls(interface)
    for plainUrl in theUrls:
        try:
            ruleMatch = trie.transformUrl(plainUrl)
            transformedUrl = ruleMatch.url
            if plainUrl == transformedUrl:
                print "OK: %s" % plainUrl
            elif ff.found_redirect(plainUrl):
                print "WARNING: %s redirects back to http" % transformedUrl
            else:
                alert()
                print "BAD: %s should have been transformed to %s" % (plainUrl, transformedUrl)
        except Exception, e:
            sys.stderr.write("%s\n" % e)

# start a Firefox instance with the given profile
ff = Firefox(profiledir)
t1 = threading.Thread(target=ff.get_urls)
t2 = threading.Thread(target=find_unapplied_rules)
t1.start()
t2.start()
