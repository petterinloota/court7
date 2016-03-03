from hopetools.config import ConfigData

cdata = ConfigData()
# cdata.printOut()

print "LORD: ", cdata.getValue("lord")
print "LIST: ", cdata.getValue("foolist"), type(cdata.getValue("foolist"))
print "MAP: ", cdata.getValue("foomap"), type(cdata.getValue("foomap"))