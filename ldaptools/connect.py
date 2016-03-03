import ldap
from ldapurl import LDAP_SCOPE_SUBTREE
from .entrydata import EntryData # I suppose you can use the DOT here ... means the module is in the same package?
# from pycurl import E_LDAP_SEARCH_FAILED, E_LDAP_INVALID_URL
import ldap.modlist as modlist
import ldaptools.entrydata
from hopetools.config import ConfigData
import types

class ldapconn:
    def __init__(self, argmap=None):
        if not isinstance(argmap, types.DictType):
            argmap = {}
        
        self.host = 'localhost'
        self.binddn = 'cn=admin'
        self.bindpw = 'password'
        self.basedn = 'dc=local'
        
        self.searchscope = LDAP_SCOPE_SUBTREE
        self.retrieveAttributes = None
        # retrieveAttributes = ['cn', 'sn', 'givennames']

        self.usersOU = "ou=users,"+self. basedn
        self.userSubOUMap = {}
        self.userSubOUMap["staff"] = "ou=staff,"+self.usersOU
        self.userSubOUMap["students"] = "ou=students,"+self.usersOU

        self.mailDomain = {}
        self.mailDomain["staff"] = "example.com"
        self.mailDomain["students"] = "students.example.com"

        if 'file' in argmap:
            conf = ConfigData(argmap['file'])
            # conf.printOut()
            conflist = ['host', 'binddn', 'bindpw', 'basedn', 'maildefdomain']
            for key in conflist:
                if conf.hasAttr(key):
                    setattr(self, key, conf.getValue(key))
            # Set the mail subdomains ...
            for key in ['staff', 'students']:
                if conf.hasAttr('maildomain' + key):
                    self.mailDomain['maildomain' + key] = conf.getValue('maildomain' + key)

    def doinit(self):
        try:
            #self.conn = ldap.open(self.host)
            self.conn = ldap.initialize('ldap://'+self.host+':389')
            self.conn.simple_bind(self.binddn,self.bindpw)

        except:
            print "Error in connection initialization. Host " + self.host

    def search(self, filter):
        self.ldap_result_id = self.conn.search(self.basedn, self.searchscope, filter, self.retrieveAttributes)

    def searchAll(self):
        return self.search('objectclass=*')
        filter = 'cn=*'

    def shiftResult(self):
        retVal = None
        try:
            result_type, result_data = self.conn.result(self.ldap_result_id, 0)
            if (result_data != []):
                retVal = EntryData(result_data) # Instantiate general LDAP Entry Data object
        except:
            print "virhe"

        return retVal

    def prepareUserEntry(self, dataObj):
        # A dict to help build the "body" of the object
        attrs = {}
        attrs['objectclass'] = ['top','person','inetorgperson']

        attrs['sn'] = dataObj.getSingle('sn')
        attrs['givenname'] = dataObj.getSingle('givenname')
        alias = dataObj.getSingle('givenname') + "." + dataObj.getSingle("sn")
        alias = alias.lower()

        # Build CN for the entry from givenname and sn ---
        if dataObj.hasAttr('cn'):
            attrs["cn"] = dataObj.getSingle("cn")
        else:
            attrs["cn"] = alias

        if dataObj.hasAttr('userpassword'):
            attrs["userpassword"] = dataObj.getSingle("userpassword")
        else:
            attrs["userpassword"] = 'Notset2016'

        if dataObj.hasAttr('description'):
            attrs["description"] = dataObj.getSingle("description")
        else:
            if dataObj.hasAttr('class'):
                attrs["description"] = dataObj.getSingle("class")
            else:
                attrs["description"] = 'Inner circle'

        if dataObj.hasAttr('mail'):
            attrs["mail"] = dataObj.getSingle("mail")
        else:
            if dataObj.hasAttr("user_type"):
                if dataObj.getSingle('user_type') == "staff":
                    attrs["mail"] = alias + "@" + self.mailDomain['staff']
                else:
                    attrs["mail"] = alias + "@" + self.mailDomain['students']

        return attrs

    def addUser(self,dataObj):

        dataObj.printOut()

        # Select BASE DN for the new entry ---
        base = self.userSubOUMap['students']
        if dataObj.hasAttr("user_type"):
            if dataObj.getSingle('user_type') == "staff":
                base = self.userSubOUMap['staff']

        attrs = self.prepareUserEntry(dataObj)

        # The dn of our new entry/object
        dn="cn=" + attrs['cn'] +  "," + base

        print "NEW  DN: " + dn

        # Convert our dict to nice syntax for the add-function using modlist-module
        ldif = modlist.addModlist(attrs)

        # Do the actual synchronous add-operation to the ldapserver
        self.conn.add_s(dn,ldif)

        # Its nice to the server to disconnect and free resources when done
        #l.unbind_s()
