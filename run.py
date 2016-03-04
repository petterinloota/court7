#!/usr/bin/python

import gear_class
import gear_file
from gear_pkg.gpkg1 import gclass1
import argparse

print("The adventure with Python begins ... \n")

def myfunc(x):
    print("func print with argument: "+x)

myfunc("test")

list=["one", "two", "three"]
dict={"one": "moi", "two": "pi", "three": "bei"}

print "Try a simple list ---------------- "
for y in list:
    print y

print "\nTry a directory -----------------"
for z in dict.keys():
    print z + ":" + dict[z]

print "\nTry a ordinary module -----------------"

print ("Use my module to fetch a value: " + gear_file.foo())

print "\nTry a module with a class definition -----------------"

obj1 = gear_class.class1()
print "Value from object: " + obj1.v1

print "\nTry a package with a class definition -----------------"

obj2 = gclass1()
print "Printing a value from a class inside a package: " + obj2.v1





