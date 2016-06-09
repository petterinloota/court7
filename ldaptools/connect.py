import re
import ldap3
# from ldapurl import LDAP_SCOPE_SUBTREE
from .entrydata import EntryData # I suppose you can use the DOT here ... means the module is in the same package?
# from pycurl import E_LDAP_SEARCH_FAILED, E_LDAP_INVALID_URL

import ldaptools.entrydata
from ldaptools.entrydata import EntryManager
from hopetools.config import ConfigData
import types
import sys
# from ldapurl import LDAP_SCOPE_BASE

from  .ldapconfig import LdapConfig
from hopetools.hopeglob import Global as glo

SEARCH_SCOPE_BASE_OBJECT = 0
SEARCH_SCOPE_SINGLE_LEVEL = 1
SEARCH_SCOPE_WHOLE_SUBTREE = 2

class ldapconn(object):
    def __init__(self, argmap=None):

        file = '/etc/hope.conf'
        if 'file' in argmap.keys():
            file = argmap['file']

        self.confObj = LdapConfig(file)
        self.entryManager = EntryManager(self.confObj) # EntryManager needs to be aware of configuration as well

    def getConfValue(self,attr):
        return self.confObj.getValue(attr)

    def doinit(self):
        try:
            #self.conn = ldap.open(self.host)

            #OLD - self.conn = ldap.initialize('ldap://'+self.getConfValue('host')+':389')
            #OLD - self.conn.simple_bind(self.getConfValue('binddn'),self.getConfValue('bindpw'))

            self.conn = ldap3.Connection(ldap3.Server(self.getConfValue('host'),port=389),
                user = self.getConfValue('binddn'),password = self.getConfValue('bindpw'),auto_bind=True)
            # print ('LDAP CONN: ', self.conn)

        except:
            print ("Error in connection initialization. Host " + self.getConfValue("host"))

    def check_arg(self, key, argmap, default):
        if key in argmap:
            if argmap[key] != None and argmap[key] != '':
                return argmap[key]

        return default

    def search(self, **kwargs):
        filter = '(objectclass=*)'
        if 'filter' in kwargs:
            filter = kwargs['filter']
        # print('FILTER: ', filter)

        base = self.check_arg('base', kwargs, self.getConfValue('searchbase'))
        # print("Base: ",base)

        myAttrs = self.getConfValue('retrieveAttributes')
        if myAttrs == None:
            myAttrs = '*'

        self.conn.search(base, filter, self.getConfValue('searchscope'), attributes=myAttrs)
        self.response = self.conn.response

    def searchAll(self):
        return self.search(filter='(objectclass=*)')

    def shiftResult(self):

        if (len(self.response) > 0 ):
            entry =  self.response.pop()
        else:
            return None

        if 'dn' in entry:
            # print('ENTRY: ', entry['dn'], entry['attributes'])
            # print("DN: ", entry['dn'])

            retVal = EntryData({'attrMap': entry['attributes'], 'dn': entry['dn']}) # Instantiate general LDAP Entry Data object

            return retVal

        return None

    def addGroup(self, dataObj):
        dataObj.printOut()

        newEntry = self.entryManager.prepareGroupEntry(dataObj)
        attrs = newEntry.valueMap

        dn = self.entryManager.newDN('group', newEntry)
        # dn="cn=" + attrs['cn'] +  "," + user_ou

        glo.debugOut("NEW DN: " + dn)

        # Convert our dict to nice syntax for the add-function using modlist-module
        ldif = modlist.addModlist(attrs)

        if (glo.testing()):
            glo.debugOut("ADD LDAP ENTRY - TESTING ONLY ...")
        else:
            glo.debugOut("ADD ENTRY ...")
            # Do the actual synchronous add-operation to the ldapserver
            self.conn.add_s(dn,ldif)
            self.conn.add_s()

        # Its nice to the server to disconnect and free resources when done
        #l.unbind_s()

    def addAdGroup(self,dataObj):

        # glo.debugOut("ADD AD GROUP !!!")

        dataObj.printOut()

        newEntry = self.entryManager.prepareGroupEntry(dataObj)
        attrs = newEntry.valueMap

        dn = self.entryManager.newDN('group', newEntry)
        # dn="cn=" + attrs['cn'] +  "," + user_ou

        glo.debugOut("NEW DN: " + dn)

        # Convert our dict to nice syntax for the add-function using modlist-module
        # OLD -  ldif = modlist.addModlist(attrs)

        objList = newEntry.getValueList('objectclass')
        attrMap = newEntry.valueMap

        if 'objectclass' in attrMap: del attrMap['objectclass']

        # glo.debugOut("Group TYPE: " + self.getConfValue('grouptype'))
        dnList = []
        if re.search('ad', self.getConfValue('grouptype'), re.IGNORECASE):
            memberList = dataObj.getList('memberuid')
            # print("Member LIST: ",memberList)
            if len(memberList) > 0:
                dnList = self.findMemberDnList(memberList)
                # print("Members: ", dnList)

            if len(dnList) > 0:
                attrMap['member'] = dnList
            else:
                if 'member' in attrMap: del attrMap['member']

            if 'memberuid' in attrMap: del attrMap['memberuid']


        dn_exists = self.dnIfExists(newEntry)

        if dn_exists:
            glo.debugOut("EXISTS already: " + dn)
        else:
            if (glo.testing()):
                glo.debugOut("ADD LDAP ENTRY - TESTING ONLY ...")
            else:
                glo.debugOut("ADD ENTRY ...")
                # Do the actual synchronous add-operation to the ldapserver
                self.conn.add(dn, object_class=objList, attributes=attrMap)

                print ('ADD RESULT: ', self.conn.result)

            # Its nice to the server to disconnect and free resources when done
            #l.unbind_s()


    def dnIfExists(self, newEntry):
        # Search for the entry to find out if it already exists ...
        search_attr = self.getConfValue('rdnattr')
        search_val = newEntry.getSingleValue(search_attr)
        search_filter = "(" + search_attr + "=" + search_val + ")"
        # glo.debugOut("Check Exists FILTER: "+ search_filter)

        self.search(filter=search_filter)

        entryObj = self.shiftResult()
        if entryObj != None:
            return entryObj.dn

        return None



    def addUser(self,dataObj):

        # dataObj.printOut()

        newEntry = self.entryManager.prepareUserEntry(dataObj)
        attrs = newEntry.valueMap

        # The dn of our new entry/object
        user_type = dataObj.getSingle('user_type')
        if user_type == None:
            user_type = dataObj.getSingle('__user_type')

        dn = self.entryManager.newDN(user_type, newEntry)
        # dn="cn=" + attrs['cn'] +  "," + user_ou

        glo.debugOut("NEW DN: " + dn)

        # Convert our dict to nice syntax for the add-function using modlist-module
        # OLD -  ldif = modlist.addModlist(attrs)

        objList = newEntry.getValueList('objectclass')
        attrMap = newEntry.valueMap
        #attrMap['objectclass'] = None

        if 'objectclass' in attrMap: del attrMap['objectclass']

        dn_exists = self.dnIfExists(newEntry)

        if dn_exists:
            glo.debugOut("EXISTS already: " + dn)
        else:
            if (glo.testing()):
                glo.debugOut("ADD LDAP ENTRY - TESTING ONLY ...")
            else:
                glo.debugOut("ADD ENTRY ...")
                # Do the actual synchronous add-operation to the ldapserver
                self.conn.add(dn, object_class=objList, attributes=attrMap)

                print ('ADD RESULT: ', self.conn.result)

            # Its nice to the server to disconnect and free resources when done
            #l.unbind_s()

    def findUidByDN(self, dn):
        # glo.debugOut("findUidByDN: "+dn)
        self.ldap_result_id = self.conn.search(dn, '(objectclass=*)', SEARCH_SCOPE_BASE_OBJECT, attributes=['uid', 'samaccountname', 'cn'])
        self.response = self.conn.response

        entryObj = self.shiftResult()
        uid = ''
        if entryObj != None:
            uid = entryObj.getUserDataObject().getSingle('uid')
            if uid == None:
                uid = entryObj.getUserDataObject().getSingle('samaccountname')
        return uid

    def findDNByUId(self, uid):
        # glo.debugOut("findDNByUId: "+uid)
        self.ldap_result_id = self.conn.search(self.getConfValue('searchbase'),"(samaccountname="+uid+")", SEARCH_SCOPE_WHOLE_SUBTREE, attributes=['uid', 'samaccountname', 'cn'])
        self.response = self.conn.response

        entryObj = self.shiftResult()
        dn = ''
        if entryObj != None:
            dn = entryObj.dn

        return dn

    def findMemberUids(self, memberList):
        uidList = []
        for mem in memberList:
            uid = self.findUidByDN(mem)
            # glo.debugOut("UID found: "+uid)
            if len(uid) > 0:
                uidList.append(uid)
        return uidList

    def findMemberDnList(self, memberList):
        dnList = []
        for mem in memberList:
            dn = self.findDNByUId(mem)
            # glo.debugOut("DN found: " + dn)
            if len(dn) > 0:
                dnList.append(dn)
        return dnList

    def groupParse(self, dataObj):
        if (dataObj.hasAttr('member')):
            uidList = self.findMemberUids(dataObj.getList('member'))
            dataObj.setValue('memberuid', uidList)