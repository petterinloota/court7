from hopetools.userdata import UserData
import re
from hopetools.hopeglob import Global as glo

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
        if user_type == 'group':
            ou = self.configObj.getValue('groupou')
        else:
            ou = self.configObj.getUserOu(user_type)
        rdnattr= self.configObj.getValue('rdnattr')
        rdnvalue = entryObj.getSingleValue(rdnattr)
        dn = rdnattr + "=" + rdnvalue + "," + ou
        # print  "NEW DN: " + dn
        return dn

    def prepareGroupEntry(self, dataObj):

        # A dict to help build the "body" of the object
        user_attr_list = ['gidnumber', 'description', 'cn']
        attrs = {}
        attrs['objectclass'] = ['top','posixgroup']

        for item in user_attr_list:
            if dataObj.getSingle(item):
                attrs[item] = dataObj.getSingle(item)

        gidnumber = dataObj.getSingle('gidnumber')
        memberattr = self.configObj.getValue('groupmemberattr')

        glo.debugOut("Group member attribute: " + memberattr)

        if dataObj.getList(memberattr):
            attrs[memberattr] = dataObj.getList(memberattr)

        if self.configObj.getValue('sambasidgroupbase'):
            attrs['objectclass'].append('sambagroupmapping')
            attrs['sambagrouptype'] = '2'
            sambasid = self.configObj.getValue('sambasidgroupbase') + '-' + gidnumber
            glo.debugOut("Samba SID: " + sambasid)
            attrs['sambaSID'] = sambasid

        return EntryData({'attrMap':attrs})


    def prepareUserEntry(self, dataObj):
        attrs = {}
        attrs['objectclass'] = ['top','person','inetorgperson', 'posixaccount']
        user_attr_list = ['givenname', 'sn', 'uidnumber','gidnumber', 'homedirectory']

        obj_list = self.configObj.getValue('user_objlist')
        if obj_list != None:
        # if isinstance(obj_list, list):
            attrs['objectclass'] = obj_list

        for item in user_attr_list:
            if dataObj.getSingle(item):
                attrs[item] = dataObj.getSingle(item)

        #attrs['sn'] = dataObj.getSingle('sn')
        #attrs['givenname'] = dataObj.getSingle('givenname')
        alias = dataObj.getSingle('givenname') + "." + dataObj.getSingle("sn")
        alias = alias.lower()

        # Build CN for the entry from givenname and sn ---
        if dataObj.hasAttr('cn') and not self.configObj.hasAttr('sambasiduserbase'):
            uid_cn_value = dataObj.getSingle("cn")
        else:
            uid_cn_value = alias

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
            for k,v in userattr_default_map.items():
                if k not in attrs:
                    attrs[k] = v

        attrs["cn"] = uid_cn_value
        if self.configObj.getValue('sambasiduserbase'):
            attrs['objectclass'].append('sambasamaccount')
            attrs["uid"] = uid_cn_value
            attrs["homedirectory"] = '/home/' + alias
            if dataObj.getSingle('uidnumber'):
                uidnumber = dataObj.getSingle('uidnumber')
            else:
                uidnumber = '7001'
            attrs['uidnumber'] = uidnumber
            attrs['gidnumber'] = '100'
            attrs['loginshell'] = '/bin/bash'
            sambasid = self.configObj.getValue('sambasiduserbase') + '-' + uidnumber
            print ("Samba SID: "+  sambasid)
            attrs['sambaSID'] = sambasid
            attrs['sambapwdlastset'] = '1458628195'
            attrs['sambapasswordhistory'] = '0000000000000000000000000000000000000000000000000000000000000000'
            attrs['sambaacctflags'] = '[U          ]'
            attrs['sambantpassword'] = 'B3E331E65756DF5C0FA120F9A4CC793F'


        print ("ATTRS: ", attrs)

        return EntryData({'attrMap':attrs})





'''
============================================================================
Actual Data Object
============================================================================
'''

class EntryData(object):

    def recognizeType(self):
        self.user_type = 'unknown'
        # Try to recognize the user type - staff, student
        type_check_list = []
        for v in self.getValueList('memberof'):
            type_check_list.append(v)
        if self.dn != None:
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


    def __init__(self, argMap={}):
        self.valueMap = {}
        self.attrList = []
        self.dn = None

        if 'searchEntry' in argMap:
            resultData = argMap['searchEntry']
            try:
                self.dn = resultData[0][0]
                self.valueMap = {}
                for k, v in resultData[0][1].items():
                    self.valueMap[k.lower()] = v
            except:
                print ("Error in Object Initialization ...")

        if 'attrMap' in argMap:
            self.valueMap = {}
            map = argMap['attrMap']

            # In this data class, values of attributes are allways lists
            for key in map:
                if isinstance(map[key], list):
                    self.valueMap[key] = map[key]
                else:
                    self.valueMap[key] = [map[key]]
            self.attrList = self.valueMap.keys()
            if 'dn' in self.valueMap:
                self.dn = self.valueMap['dn']

        if 'dn' in argMap:
            self.dn = argMap['dn']

        self.attrList = self.valueMap.keys()
        self.recognizeType()

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