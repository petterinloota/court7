

class GenericData(object):
    def __init__(self, inputMap):
        self.dataMap = {}

        if inputMap != None:
            for attr in inputMap.keys():
                myList = []
                if (isinstance(inputMap[attr], list)):
                    myList = inputMap[attr]
                else:
                    myList.append(inputMap[attr])
                self.dataMap[attr] = myList

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
        myList = []
        if (isinstance(value, list)):
            myList = value
        else:
            myList.append(value)
        self.dataMap[attr] = myList

    def printOut(self):
        for attr in self.dataMap.keys():
            if isinstance(self.getList(attr), list):
                print ("   " + attr + ": " , self.getList(attr))
            else:
                print ("   " + attr + ": ???")



