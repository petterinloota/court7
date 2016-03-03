import simplejson as json
import types
import sys

class JsonData:
    def __init__(self,inputText):
        self.mapList = []
        self.parseDataToMapList(inputText)

    def parseDataToMapList(self,inputText):
        success = True
        try:
            loadedData = json.loads(inputText)
            # print "the text was JSON OK", type(loadedData)
            if isinstance(loadedData, types.DictType):
                self.mapList.append(loadedData)
            else:
                self.mapList = loadedData
        except:
            sys.stderr.write("The text was NOT JSON OK:: " + inputText + "\n")
            success = False

        # Try still another approach ... file with a json string in each line
        if not success:
            for line in inputText.split("\n"):
                if (len(line) > 0):
                    parsed_json = json.loads(line)
                    self.mapList.append(parsed_json)

        return self.mapList

    def printOut():
        for item in self.mapList:
            print item.keys()
            if "cn" in item.keys():
                print "CN:" + item["cn"]

    def getMapList(self):
        #return []
        return self.mapList
