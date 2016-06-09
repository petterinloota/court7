#!/usr/bin/python3

import argparse
import sys
import re
from distutils.util import grok_environment_error

from hopetools import jsontools as jtools
from hopetools.formatdata import FormatData
from hopetools.userdata import UserData
from ldaptools.connect import ldapconn
from hopetools.hopeglob import Global

# ---------------------------------------------------------------

description = """
    A General tool to handle LDAP data: get report and add new entries (also to modify in future versions).
    Baseline data format is JSON:
    - reports generated,
    - data used as input,
    - configuration data.

    JSON as both in and out format means the tool can be used for fetching data from LDAP A and then piping the same data in order to insert it into a second LDAP B etc.
    """
parser = argparse.ArgumentParser(description=description)
parser.add_argument("-m", "--mode", default="raw",  help="define the mode of operation: raw, report, add ( ... yet to come: modify)")
parser.add_argument("-s", "--search", default="(objectclass=*)",  help="define the search filter, default: objectclass=*")
parser.add_argument("-b", "--base", default=None,  help="define the LDAP search base DN")
parser.add_argument("-f", "--file", default=None, help="file to read the input data from; optionally stdin can be used")
parser.add_argument("-c", "--config", default='/etc/hope/ldap.conf', help="file to read the LDAP configuratin from")
parser.add_argument("-v", "--verbose", default=0, help="verbosity level - 0(default) or 1")
parser.add_argument("-T", "--test", default=0, help="Test only (default) or 1")
parser.add_argument("-o", "--options", default="", help="Options: [memberuid|posix_group|ad_group]")

# ---------------------------------------------------------------

formatObj = FormatData(None)
mapList=[]
inputText = ""

# ---------------------------------------------------------------

def collectSearchResults(ld, ld2, grp_p):
    result=ld.shiftResult()
    while (result != None):
        data_obj = result.getUserDataObject()
        if grp_p:
            ld2.groupParse(data_obj)

        formatObj.addDataObject(data_obj)
        result=ld.shiftResult()

def printReport(ld, mode):
    result=ld.shiftResult()
    cnt = 0
    while (result != None):
        cnt += 1
        print  ("----------------------------------")
        print ("DN: " + result.dn + "--- User Type: " + result.user_type)
        print  ("----------------------------------")

        nice_list = ['cn', 'displayname', 'mail', 'sn', 'givenname', 'samaccountname', 'memberof', 'userpassword']
        nice_list = ['displayname', 'mail','samaccountname']
        if mode == 'fullreport':
            nice_list = result.attrList

        obj = result.getUserDataObject();
        # print result.valueMap
        for id in nice_list:
            if id != None:
                print (id + ":", obj.getList(id))
        result=ld.shiftResult()
    print("\nFound altogether: ",cnt)
# ---------------------------------------------------------------

args = parser.parse_args()
mode = args.mode
test = args.test
options = args.options
memberuid_parse = False
group_operation = False
ad_group_operation = False

sys.stderr.write("Operation mode: " + mode + "\n")
if test:
    sys.stderr.write("TESTING ONLY")
    Global.testing(True)

# ld = ldapconn(None)
ld2 = ldapconn({'file': args.config})
ld2.doinit()

# ld = ldapconn(None)
ld = ldapconn({'file': args.config})
ld.doinit()


if re.search('memberuid', options, re.IGNORECASE):
    memberuid_parse = True
    Global.debugOut("Parse Group member DN list to memberUid values")

if re.search('group', options, re.IGNORECASE):
    group_operation = True
    Global.debugOut("Group Operation")

if re.search('ad_group', options, re.IGNORECASE):
    ad_group_operation = True
    Global.debugOut("AD Group Operation")

if mode == 'add':

    if args.file is not None:
        file = open(args.file, "r")
        inputText = file.read()
    else:
        for line in sys.stdin:
            inputText += line

    print ("Parse JSON text to Python data ------------")

    jsonData = jtools.JsonData(inputText)
    mapList = jsonData.mapList
    mapList = jsonData.getMapList()

    for item in mapList:
        qualMap = {}
        dataObj = UserData(item)
        qualMap = dataObj.getQualifierMap()
        # print ("Try to add to LDAP: ", qualMap)

        try:
            pass
        except:
            print ("ADD failed for ... ", qualMap)

        if ad_group_operation:
            ld.addAdGroup(dataObj)
        elif group_operation:
            ld.addGroup(dataObj)
        else:
            ld.addUser(dataObj)

        #except:
        #    print ("ADD failed for ... ", qualMap)

elif mode == 'raw':
    sys.stderr.write("LDAP search  using filter: " + args.search + "\n")
    ld.search(filter=args.search, base=args.base)
    collectSearchResults(ld, ld2, memberuid_parse)
    # print formatObj.printOut()
    print (formatObj.getJson())

elif mode == 'report' or mode == 'fullreport':
    sys.stderr.write("LDAP search  using filter: " + args.search + "\n")
    ld.search(filter=args.search, base=args.base)
    printReport(ld, mode)


else:
    print ("No mode defined ...")
