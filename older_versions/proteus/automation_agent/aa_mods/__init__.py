__modules__ = []
import os, inspect

#Load all files into *our* namespace
for file in os.listdir(__path__[0]):
    path = os.path.join(__path__[0], file)
    modname = inspect.getmodulename(file)
    if modname != '__init__':
        if modname and modname not in __modules__:
            __modules__.append(modname)
            print "Loading %s" % modname
__all__ = __modules__

