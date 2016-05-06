#!/usr/bin/python

import argparse
import sys
import re
from hopetools.hopeglob import Global
from ldmain import LdoperMain

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
parser.add_argument("-s", "--search", default="objectclass=*",  help="define the search filter, default: objectclass=*")
parser.add_argument("-b", "--base", default=None,  help="define the LDAP search base DN")
parser.add_argument("-f", "--file", default=None, help="file to read the input data from; optionally stdin can be used")
parser.add_argument("-c", "--config", default='/etc/hope/ldap.conf', help="file to read the LDAP configuratin from")
parser.add_argument("-v", "--verbose", default=0, help="verbosity level - 0(default) or 1")
parser.add_argument("-T", "--test", default=0, help="Test only (default) or 1")
parser.add_argument("-o", "--options", default="", help="Options: [memberuid|posix_group]")
# ---------------------------------------------------------------

inputText = ""

# ---------------------------------------------------------------
def printReport(ld, mode):
    result=ld.shiftResult()
    while (result != None):
        print  "----------------------------------"
        print "DN: ", result.dn, "--- User Type: ", result.user_type
        print  "----------------------------------"

        nice_list = ['cn', 'displayname', 'mail', 'sn', 'givenname', 'samaccountname', 'memberof', 'userpassword']
        nice_list = ['displayname', 'mail','samaccountname']
        if mode == 'fullreport':
            nice_list = result.attrList

        # print result.valueMap
        for id in nice_list:
            if id != None:
                print id, ":", result.getValueList(id)
        result=ld.shiftResult()
# ---------------------------------------------------------------

args = parser.parse_args()

ldoper = LdoperMain(mode=args.mode, search=args.search, base=args.base, config=args.config)

sys.stderr.write("Operation mode: " + args.mode + "\n")
if args.test:
    sys.stderr.write("TESTING ONLY")
    Global.testing(True)
    ldoper.setConfig(testing=True)

if re.search('memberuid', args.options, re.IGNORECASE):
    Global.debugOut("Parse Group member DN list to memberUid values")
    ldoper.setConfig(memberuid_parse=True)

if re.search('group', args.options, re.IGNORECASE):
    Global.debugOut("Group Operation")
    ldoper.setConfig(group_operation=True)

# ldoper.deb()

if args.mode == 'add':
    if args.file is not None:
        file = open(args.file, "r")
        inputText = file.read()
    else:
        for line in sys.stdin:
            inputText += line

    print "Parse JSON text to Python data ------------"

    result = ldoper.addByRawJson(inputText)
    print "RESULT: ", result

elif args.mode == 'raw':
    sys.stderr.write("LDAP search  using filter: " + args.search + "\n")
    formatObj = ldoper.fetch()
    # print formatObj.printOut()
    print formatObj.getJson()

elif args.mode == 'report' or args.mode == 'fullreport':
    sys.stderr.write("LDAP search  using filter: " + args.search + "\n")
    ldoper.ld.search(filter=args.search, base=args.base)
    printReport(ld, args.mode)

else:
    print "No mode defined ..."
