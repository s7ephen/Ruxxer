#!/usr/bin/env python2.4
"""
    Cartesian Product of Sets (Experimental)
    
    Given a simple object model that will for the basis 
    of a graph (tree of data). This file is intended to explore
    the different approaches to obtaining the results known
    as the Cartesian Product.


    The object model contains three fundamental types:

        --> Primitives
        --> Structures
        --> Complex Primitives

    DEFINITIONS:
    ------------
    --> PRIMITIVES contain single values.

    --> COMPLEX PRIMITIVES can contain any number of single values and returns
    a different one each time the value is accessed.

    --> STRUCTURES can contain any number of Primitives, Complex Primitives, or 
    Structures

    In the vernacular of the accompanying diagram:
        PRIMITIVES are LEAF NODES
            and
        COMPLEX PRIMITIVES (liek the ones pictured) contain multiple LEAF NODES
            and
        STRUCTURES are BRANCH NODES

"""

class Primitive:
    """
        Primitive (LEAF NODE)

    """
    def __init__(self, value):
        self.__parent = None #this value isnt really used in Primitives
                             #we just include it for readability sake.
        self.__value = value #note "value" not "valueS"
        
    def __len__(self):
        return len(self.__value)

    def __repr__(self):
        return repr(self.__value)

class ComplexPrimive:
    """
        Complex Primitive 

            Contain multiple LEAF NODES.
    """
    def __init__(self):
        self.__parent = None #this value isnt really used in ComplexPrimitives
                             #we just include it for readability sake.
        self.__values = {}   #note "valueS not value"

    def __len__(self):
        len_count = 0
        for val in self.__values.values():
            len_count+=len(val)

    def __repr__(self):
        print repr(self.__values)

class Structure:
    """
        Structures (BRANCH NODES)
            
        contain any number of PRIMITIVES, COMPLEX PRIMITIVES, or STRUCTURES.
    """
    def __init__(self):
        self.__parent = None #This value *IS* used in Structures
        self.__values = {}   #note "valueS not value" 

    def push(self, *args):
        """
                "Push" as we use it here is a bit of misnomer, although
            structures can behave like stacks, they are actually dictionaries,
            and keep the values by array.
        """
        pass
 
    def __len__(self):
        pass
    
    def __repr__(self):
        print repr(self.__values)
