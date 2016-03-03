#!/usr/bin/python

import argparse
import sys

from hopetools import jsontools as jtools
from hopetools.userdata import UserData

parser = argparse.ArgumentParser(description='Slurp some JSON data and parse it into Python dictionary')
parser.add_argument("-v", "--verbosity", help="increase output verbosity")

parser.add_argument("-m", "--mode", default="report",  help="define the mode of operation: report, add, modify")
parser.add_argument("-f", "--file", default=None, help="file to read the input data from")

args = parser.parse_args()
if args.verbosity:
    print "verbosity turned on"

inputText = ""

if args.file is not None:
    file = open(args.file, "r")
    inputText = file.read()
else:
    for line in sys.stdin:
        inputText += line

mode = args.mode
print "Operation mode: " + mode

print "Parse JSON text to Python data ------------"

mapList=[]

''''
for line in inputText.split("\n"):
    if (len(line) > 0):
        parsed_json = json.loads(line)
        mapList.append(parsed_json)
'''

jsonData = jtools.JsonData(inputText)
mapList = jsonData.mapList

for item in mapList:
    dataObj = UserData(item)
    # print item.keys()
    print dataObj.getAttrList()

    #if "cn" in item.keys():
     #   print "CN:" + item["cn"]

    if dataObj.hasAttr("cn"):
        print "CN: " + dataObj.getSingle("cn")

    if "role" in item.keys():
        #print "ROLE:" + item["role"]
        print "ROLE list:   " + " >>> ".join(dataObj.getList("role"))
        print "ROLE single: " + dataObj.getSingle("role")


