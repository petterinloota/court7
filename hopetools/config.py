import simplejson as json

class ConfigData:
    def __init__(self, configFile):
        self.dataMap = {}

        file = open(configFile, "r")
        inputText = file.read()
        # print inputText
        loadedData = json.loads(inputText)
        # print type(loadedData)
        self.dataMap = loadedData

    def getValue(self, key):
        if key in self.dataMap:
            return self.dataMap[key]
        return None

    def hasAttr(self,attr):
        if attr in self.dataMap:
            return True
        return False

    def printOut(self):
        print self.dataMap



'''
The Config file have to be in JSON format.
Newlines can be used for clarity.
Example:

{
"lord": "Jesus",
"testldap": {"binddn":"dn","bindpw":"salasana"},
"foo": "foovalue",
"foolist": ["foovalue1","foovalue2"],
"foomap": {"foo1":"foo1_value","foo2":"foo2_value", "foo3": ["foo3listval1","foo3listval2"]}
}

'''