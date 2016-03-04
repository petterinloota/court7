from ldaptools.connect import ldapconn
from hopetools.userdata import UserData
from hopetools.formatdata import FormatData

formatObj = FormatData(None)

def reportResult(ld):
    result=ld.shiftResult()

    while (result != None):
        print "Entry DN: " + result.dn
        # print result.getValueList('cn')

        for attr in ['cn', 'sn']:
            value = result.getSingleValue(attr)
            if value != None:
                print ("   " + attr + ": " + value )

        #print result.getSingleValue('sn')
        print "   -----------"
        userObj = result.getUserDataObject()
        userObj.printOut()
        formatObj.addDataObject(userObj)

        result=ld.shiftResult()



# ------------------------------------------------

print "Do LDAP - 1"

ld = ldapconn({'file': '/etc/hope/ldap.conf'})
ld.doinit()

ld.search("cn=first.last1")
reportResult(ld)

print "======================"
print "Do LDAP - 2"

ld.searchAll()
reportResult(ld)


print "\n---------------\nResulting JSON: "
print formatObj.getJson()
print "----------------"



