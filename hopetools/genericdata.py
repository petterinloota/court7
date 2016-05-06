import types

class GenericData(object):
    def __init__(self, inputMap):
        self.dataMap = {}

        if inputMap != None:
            for attr in inputMap.keys():
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
            if isinstance(self.getList(attr), types.ListType):
                print "   " , attr , ": " , self.getList(attr)
            else:
                print "   " , attr , ": ???"



