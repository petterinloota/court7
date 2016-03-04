import simplejson as json

class FormatData:

    def __init__(self, obj):
        self.list = []
        if obj != None:
            self.addDataObject(obj)

    def addDataObject(self,obj):
        # print "adding object"
        if ('objectsid' in obj.dataMap.keys()):
            obj.dataMap.pop('objectsid')
        if ('objectguid' in obj.dataMap.keys()):
            obj.dataMap.pop('objectguid')
        self.list.append(obj.dataMap)

    def getJson(self):
        #print "LIST as raw: "
        #print self.list
        #print "-------------"
        self.json = json.dumps(self.list)
        return self.json

    def printOut(self):
        print self.list
