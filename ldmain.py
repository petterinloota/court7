import sys
import re

from hopetools import jsontools as jtools
from hopetools.formatdata import FormatData
from hopetools.userdata import UserData
from ldaptools.connect import ldapconn
from hopetools.hopeglob import Global
from hopetools.genericdata import GenericData

"""
ldmain.py

This is the central logic for LDAP operations.
It does not contain straight interface out - that is handled in:
- ldcli.py - CLI
- ldrest.py

The implemented modes of operations are:
- fetch
- add
... and in backlog:
- compare
- modify
- disable
- remove

"""

class LdoperMain(object):


    def __init__(self, **kwargs):
        self.configObj = GenericData(None)
        self.formatObj = FormatData(None)
        self.resultStack = []
        self.setConfig(**kwargs)

        self.ld2 = ldapconn({'file': self.configObj.getSingle('config')})
        self.ld2.doinit()
        self.ld = ldapconn({'file': self.configObj.getSingle('config')})
        self.ld.doinit()

        self.globals = None
        if Global.testing():
            self.globals = 'TESTING'

    def setConfig(self, **kwargs):
        for key in kwargs.keys():
            self.configObj.setValue(key, kwargs[key])

    def addByList(self, mapList):
        if Global.testing():
            self.globals = 'TESTING'

        for item in mapList:
            qualMap = {}
            try:
                dataObj = UserData(item)
                qualMap = dataObj.getQualifierMap()
                print "Try to add to LDAP: ", qualMap

                if self.configObj.getSingle('group_operation'):
                    self.ld.addGroup(dataObj)
                else:
                    self.ld.addUser(dataObj)
                self.resultStack.append({'method': 'addByRawJson','operation':'add', 'result': 'OK', 'data': qualMap, 'globals': self.globals });
            except:
                self.resultStack.append({'method': 'addByRawJson','operation':'add', 'result': 'FAIL', 'data': qualMap, 'globals': self.globals});

        return self.resultStack

    def addByJson(self, jsonData):
        mapList = jsonData.mapList
        mapList = jsonData.getMapList()
        return self.addByList(mapList)

    def addByRawJson(self, inputText):
        return self.addByJson(jtools.JsonData(inputText))

    def deb(self):
        print self.configObj.getAttrList()
        print self.configObj.printOut()

    def collectSearchResults(self):
        result=self.ld.shiftResult()
        while (result != None):
            data_obj = result.getUserDataObject()
            if self.configObj.getSingle('memberuid_parse'):
                self.ld2.groupParse(data_obj)

            self.formatObj.addDataObject(data_obj)
            result=self.ld.shiftResult()

    def fetch(self):
        self.ld.search(filter=self.configObj.getSingle('search'), base=self.configObj.getSingle('base'))
        self.collectSearchResults()
        return self.formatObj