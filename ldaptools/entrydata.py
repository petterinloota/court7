from hopetools.userdata import UserData
import re
import sys
import types

'''
============================================================================
Manager Object to Produce Data Objects
============================================================================
'''

class EntryManager(object):

    def __init__(self, conf):
        self.configObj = conf
        pass

    def entryFactory(self):
        return EntryData()

    def newDN(self, user_type, entryObj):
        ou = self.configObj.getUserOu(user_type)
        rdnattr= self.configObj.getValue('rdnattr')
        rdnvalue = entryObj.getSingleValue(rdnattr)
        dn = rdnattr + "=" + rdnvalue + "," + ou
        # print  "NEW DN: " + dn
        return dn

    def prepareUserEntry(self, dataObj):
        # A dict to help build the "body" of the object
        attrs = {}
        attrs['objectclass'] = ['top','person','inetorgperson', 'posixaccount']

        attrs['sn'] = dataObj.getSingle('sn')
        attrs['givenname'] = dataObj.getSingle('givenname')
        alias = dataObj.getSingle('givenname') + "." + dataObj.getSingle("sn")
        alias = alias.lower()

        # Build CN for the entry from givenname and sn ---
        if dataObj.hasAttr('cn'):
            attrs["cn"] = dataObj.getSingle("cn")
        else:
            attrs["cn"] = alias

        # Decide the RDN value according to config  and data input
        # - force_rdn - can be used to force set a value to rdn attribute
        # - overriden_rdn - config param can be used to calculate allways the rdn attribute value
        rdnattr = self.configObj.getValue('rdnattr')
        if rdnattr != None:
            if dataObj.hasAttr('force_rdn'):
                attrs[rdnattr] =  dataObj.getSingle(rdnattr)
            elif self.configObj.getValue('override_rdn'):
                attrs[rdnattr] = alias

        if dataObj.hasAttr('userpassword'):
            attrs["userpassword"] = dataObj.getSingle("userpassword")
        else:
            attrs["userpassword"] = 'Notset2016'

        if dataObj.hasAttr('displayname'):
            attrs["displayname"] = dataObj.getSingle("displayname")
        else:
            attrs["displayname"] = dataObj.getSingle('givenname') + " " + dataObj.getSingle("sn")

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
            maildomain = self.configObj.getMailDomain(dataObj.getSingle('user_type'))
            attrs["mail"] = alias + "@" + maildomain

        ok_attrlist = self.configObj.getValue('user_attrlist')
        if ok_attrlist != None:
            for a in ok_attrlist:
                if dataObj.hasAttr(a):
                    attrs[a] = dataObj.getSingle(a)

        userattr_default_map = self.configObj.getValue('userattr_default_map')
        if userattr_default_map != None:
            for k,v in userattr_default_map.iteritems():
                if k not in attrs:
                    attrs[k] = v

        print "ATTRS: ", attrs

        return EntryData({'attrMap':attrs})

'''
============================================================================
Actual Data Object
============================================================================
'''

class EntryData(object):

    def __init__(self, argMap={}):
        # sys.stderr.write("Init Entry data ... result raw: \n")
        # print resultData
        # sys.stderr.write(resultData)
        self.valueMap = {}
        self.attrList = []
        self.dn = None

        if 'searchEntry' in argMap:
            resultData = argMap['searchEntry']
            try:
            #for i in [1]:
                self.user_type = 'unknown'
                self.dn = resultData[0][0]
                self.valueMap = {}
                for k, v in resultData[0][1].iteritems():
                    self.valueMap[k.lower()] = v

                # Try to recognize the user type - staff, student
                type_check_list = []
                for v in self.getValueList('memberof'):
                    type_check_list.append(v)
                type_check_list.append(self.dn)
                for v in type_check_list:
                    if re.search(r'(staff|teacher|itc|assist|director|principal|developm|finance|consult|librar|facili|human|resour|build|admin)', v, re.IGNORECASE):
                        self.user_type = 'staff'
                        break
                    if self.user_type == 'unknown':
                        if re.search(r'student|lab', v, re.IGNORECASE):
                            self.user_type = 'student'

                if self.user_type != 'unknown':
                    #print "USER TYPE RECOGNIZED: ", self.user_type
                    self.valueMap['__user_type'] = [self.user_type]

                self.attrList = self.valueMap.keys()

            except:
                print "Error in Object Initialization ..."
        elif 'attrMap' in argMap:
            self.valueMap = {}
            map = argMap['attrMap']

            # In this data class, values of attributes are allways lists
            for key in map:
                if isinstance(map[key], types.ListType):
                    self.valueMap[key] = map[key]
                else:
                    self.valueMap[key] = [map[key]]
            self.attrList = self.valueMap.keys()
            if 'dn' in self.valueMap:
                self.dn = self.valueMap['dn']

    def getSingleValue(self, attr):
        retVal = None
        if attr in self.valueMap.keys():
            valueList = self.valueMap[attr]
            retVal = valueList[0]
        return retVal

    def getValueList(self, attr):
        retVal = []
        if attr in self.valueMap.keys():
            retVal = self.valueMap[attr]
        return retVal

    def getUserDataObject(self):
        # Here transform the data to a ordinary user data object
        self.userDataObj = UserData(None)

        for attr in self.attrList:
            # Objectclasses don't belong to STANDARD user object
            if (attr.lower() != 'objectclass'):
                self.userDataObj.setValue(attr.lower(), self.getValueList(attr))

        # Try to guess the user type from the DN ...
        if re.search(r'staff', self.dn, re.IGNORECASE):
            self.userDataObj.setValue('user_type', 'staff')
        elif re.search(r'student', self.dn, re.IGNORECASE):
            self.userDataObj.setValue('user_type', 'student')

        return self.userDataObj

'''
# This package takes care of transforming data from LDAP data to STANDARD USER data and vica versa
# Use Case 1:
1) Execute LDAP search: result will be  ldaptools.EntryData objects
2) Instantiate hopetools.ldapuserdata to convert the EntryData to a STANDARD UserData object.
3) Print UserData object contents in JSON format

Use Case2:
1) Have a


'''