from hopetools.userdata import UserData
import re

class EntryData:
    def __init__(self):
        self.dn = ''
        self.attrList = []
        self.valueMap = {}
        self.suffix = "dc=ad7,dc=local"
        self.usersOU = "ou=users,"+self.suffix
        self.userSubOUMap = {}
        self.userSubOUMap["staff"] = "ou=staff,"+self.usersOU
        self.userSubOUMap["students"] = "ou=students,"+self.usersOU

    # resultData is now data as it is when returned by python-ldap search result operation
    def __init__(self, resultData):
        try:
            self.dn = resultData[0][0]
            self.valueMap = resultData[0][1]
            self.attrList = self.valueMap.keys()
        except:
            print "Error in Object Initialization ..."

    def getSingleValue(self, attr):
        retVal = None
        if attr in self.valueMap.keys():
            valueList = self.valueMap[attr]
            retVal = valueList[0]
        return retVal

    def getValueList(self, attr):
        retVal = None
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