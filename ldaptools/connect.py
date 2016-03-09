import ldap
from ldapurl import LDAP_SCOPE_SUBTREE
from .entrydata import EntryData # I suppose you can use the DOT here ... means the module is in the same package?
# from pycurl import E_LDAP_SEARCH_FAILED, E_LDAP_INVALID_URL
import ldap.modlist as modlist
import ldaptools.entrydata
from ldaptools.entrydata import EntryManager
from hopetools.config import ConfigData
import types
import sys
from  .ldapconfig import LdapConfig

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
            self.conn = ldap.initialize('ldap://'+self.getConfValue('host')+':389')
            self.conn.simple_bind(self.getConfValue('binddn'),self.getConfValue('bindpw'))

        except:
            print "Error in connection initialization. Host " + self.getConfValue("host")

    def check_arg(self, key, argmap, default):
        if key in argmap:
            if argmap[key] != None and argmap[key] != '':
                return argmap[key]

        return default

    def search(self, **kwargs):

        filter = 'objectclass=*'
        if 'filter' in kwargs:
            filter = kwargs['filter']

        base = self.check_arg('base', kwargs, self.getConfValue('basedn'))

        self.ldap_result_id = self.conn.search(base, self.getConfValue('searchscope'),
                                               filter, self.getConfValue('retrieveAttributes'))

    def searchAll(self):
        return self.search(filter='objectclass=*')

    def shiftResult(self):
        retVal = None
        result_type, result_data = self.conn.result(self.ldap_result_id, 0)

        # print "RESULT TYPE: ", result_type

        if result_type == 100:
            if (result_data != []):
                retVal = EntryData({'searchEntry': result_data}) # Instantiate general LDAP Entry Data object

        return retVal

    def addUser(self,dataObj):

        dataObj.printOut()

        newEntry = self.entryManager.prepareUserEntry(dataObj)
        attrs = newEntry.valueMap

        # The dn of our new entry/object
        user_type = dataObj.getSingle('user_type')
        if user_type == None:
            user_type = dataObj.getSingle('__user_type')


        dn = self.entryManager.newDN(user_type, newEntry)
        # dn="cn=" + attrs['cn'] +  "," + user_ou

        print "NEW  DN: " + dn

        # Convert our dict to nice syntax for the add-function using modlist-module
        ldif = modlist.addModlist(attrs)

        # Do the actual synchronous add-operation to the ldapserver
        self.conn.add_s(dn,ldif)

        # Its nice to the server to disconnect and free resources when done
        #l.unbind_s()
