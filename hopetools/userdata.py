import types
from hopetools.genericdata import GenericData

class UserData(GenericData):
    def __init__(self, inputMap):
        super(UserData,self).__init__(inputMap)
        self.qualifierList = ['dn', 'mail', 'cn', 'displayname', 'sn']

    def getQualifierMap(self):
        for best in self.qualifierList:
            if self.hasAttr(best):
                return {best: self.getSingle(best)}
        return {'n/a': 'n/a'}


