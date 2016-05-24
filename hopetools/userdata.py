import types
from hopetools.genericdata import GenericData

class UserData(GenericData):
    def __init__(self, inputMap):
        self.qualifierList = ['dn', 'mail', 'cn', 'displayname', 'sn']
        super(UserData,self).__init__(inputMap)


    def getQualifierMap(self):
        for best in self.qualifierList:
            # print ("BEST: "+ best)
            if self.hasAttr(best):
                return {best: self.getSingle(best)}
        return {'n/a': 'n/a'}


