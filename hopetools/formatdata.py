import simplejson as json

class FormatData:

    def __init__(self, obj):
        self.list = []
        if obj != None:
            self.list.append(obj.dataMap)

    def addDataObject(self,obj):
        self.list.append(obj.dataMap)

    def getJson(self):
        #print "LIST as raw: "
        #print self.list
        #print "-------------"
        self.json = json.dumps(self.list)
        return self.json

    def printOut(self):
        pass