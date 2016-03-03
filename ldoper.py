#!/usr/bin/python

import argparse
import sys

from hopetools import jsontools as jtools
from hopetools.formatdata import FormatData
from hopetools.userdata import UserData
from ldaptools.connect import ldapconn

formatObj = FormatData(None)

def collectSearchResults(ld):
    result=ld.shiftResult()
    while (result != None):
        formatObj.addDataObject(result.getUserDataObject())
        result=ld.shiftResult()


parser = argparse.ArgumentParser(description='Slurp some JSON data and parse it into Python dictionary')
parser.add_argument("-m", "--mode", default="report",  help="define the mode of operation: report, add, modify")
parser.add_argument("-s", "--search", default="objectclass=*",  help="define the search filter")
parser.add_argument("-b", "--base", default="",  help="define the LDAP search base dn")
parser.add_argument("-f", "--file", default=None, help="file to read the input data from")
parser.add_argument("-v", "--verbose", default=0, help="verbosity level - from 1 to 9")

mapList=[]
inputText = ""

args = parser.parse_args()
mode = args.mode

sys.stderr.write("Operation mode: " + mode + "\n")

# ld = ldapconn(None)
ld = ldapconn({'file': '/etc/hope/ldap.conf'})
ld.doinit()

if mode == 'add':

    if args.file is not None:
        file = open(args.file, "r")
        inputText = file.read()
    else:
        for line in sys.stdin:
            inputText += line

    print "Parse JSON text to Python data ------------"

    jsonData = jtools.JsonData(inputText)
    mapList = jsonData.mapList
    mapList = jsonData.getMapList()

    for item in mapList:
        qualMap = {}
        try:
            dataObj = UserData(item)
            qualMap = dataObj.getQualifierMap()
            print "Try to add to LDAP: ", qualMap
            ld.addUser(dataObj)
        except:
            print "ADD failed for ... ", qualMap

elif mode == 'report':
    sys.stderr.write("LDAP search  using filter: " + args.search + "\n")
    ld.search(args.search)
    collectSearchResults(ld)
    print formatObj.getJson()

else:
    print "No mode defined ..."
