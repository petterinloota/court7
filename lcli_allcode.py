import ldaptools.connect
import ldap
from pycurl import E_LDAP_SEARCH_FAILED, E_LDAP_INVALID_URL
from ldapurl import LDAP_SCOPE_SUBTREE

print "Do LDAP"

#hldap = ldaptools.ldaptools.ldaptools(None)

print "Do LDAP ... init"
#hldap.doinit()

print "Do LDAP ... search"
#hldap.search()


def search():
    #try:
    host = 'localhost'
    binddn = 'cn=admin,dc=ad7,dc=local'
    bindpw = 'Open2016'
    basedn = 'dc=ad7,dc=local'
    searchscope = LDAP_SCOPE_SUBTREE

    conn = ldap.initialize('ldap://localhost:389')
    conn.simple_bind(binddn,bindpw)

    filter = 'cn=*'
    # retrieveAttributes = ['cn', 'sn', 'givennames']
    retrieveAttributes = None

    ldap_result_id = conn.search(basedn, searchscope, filter, retrieveAttributes)
    result_set = []

    while 1:
        result_type, result_data = conn.result(ldap_result_id, 0) # Second parameter is "all" ... 0 means take on result at a time ...
        if (result_data == []):
            break
        else:
            dn = result_data[0][0]
            value_map = result_data[0][1]
            print "DN: " + dn
            keys = value_map.keys()
            for key in keys:
                values = value_map[key]
                print key + ":" + ', '.join(values)

            ## here you don't have to append to a list
            ## you could do whatever you want with the individual entry
            ## The appending to list is just for illustration.
            '''
            if result_type == ldaptools.RES_SEARCH_ENTRY:
                result_set.append(result_data)
            '''
    print "Search result: "
    print result_set

    '''
    except E_LDAP_SEARCH_FAILED:
        print "Error in search "
    except E_LDAP_INVALID_URL:
        print "invalid URL"
    except:
        print "other error with search ..."
    '''


search()