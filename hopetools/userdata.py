import types

class UserData(object):
    def __init__(self, inputMap):
        self.qualifierList = ['dn', 'mail', 'cn', 'displayname', 'sn']
        self.dataMap = {}

        if inputMap != None:
            for attr in inputMap.keys():
                #print "value for " + attr
                #print inputMap[attr]
                #print ""
                list = []
                if (isinstance(inputMap[attr], types.ListType)):
                    list = inputMap[attr]
                else:
                    list.append(inputMap[attr])
                self.dataMap[attr] = list

    def getSingle(self, attr):
        if attr in self.dataMap:
            listOfValues = self.dataMap[attr]
            return listOfValues[0]
        return None

    def getList(self, attr):
        if attr in self.dataMap:
            return self.dataMap[attr]
        return None

    def getAttrList(self):
        return self.dataMap.keys()

    def hasAttr(self,attr):
        if attr in self.dataMap:
            return True
        return False

    def setValue(self, attr, value):
        list = []
        if (isinstance(value, types.ListType)):
            list = value
        else:
            list.append(value)
        self.dataMap[attr] = list

    def printOut(self):
        for attr in self.dataMap.keys():
            print "   " + attr + ": " + ",".join(self.getList(attr))

    def getQualifierMap(self):
        for best in self.qualifierList:
            if self.hasAttr(best):
                return {best: self.getSingle(best)}
        return {'n/a': 'n/a'}


