
# from ldapurl import LDAP_SCOPE_SUBTREE

from hopetools.config import ConfigData
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE
class LdapConfig(ConfigData):
    def __init__(self, arg):
        super(LdapConfig,self).__init__(arg)

        # OLD -  self.setValue('searchscope', LDAP_SCOPE_SUBTREE)
        self.setValue('searchscope', SEARCH_SCOPE_WHOLE_SUBTREE)
        self.setValue('retrieveAttributes', None)

    def getMailDomain(self, user_type):
        if self.hasAttr('maildomainmap'):
            map = self.getValue('maildomainmap')
            if user_type in map:
                return map[user_type]
            
        return self.getValue('maildomain')
    
    def getUserOu(self, user_type):
        if self.hasAttr('useroumap'):
            map = self.getValue('useroumap')
            if user_type in map:
                return map[user_type]
            
        return self.getValue('userou')    