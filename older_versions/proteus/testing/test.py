#!/usr/bin/env python2.4
# testing rightmost-peer algorithm
#
# Primative: A primitive data type
# Bruters: A complex primitive. Contains multiple primitives
#           in an array. Returns only one value at a time.
#           which value returned is determined by which iteration
#           the whole tree is on. 
# Dataflow: A 'branching' datatype that can contain
#           Bruters, Primatives, or other Dataflows.
#

class Primative:
    """
        Our Primative.
    """
    def __init__(self):
        self.data = [] #In a Primitive, this array should never exceed one value
                       #It will only exceed one value as a Bruter object 
        self.useful = True
        self.peer_iters = None #all the rightmost peers' iterations
                               #factorialized. this gets set by parent
        self.now_iter = None #current iteration the whole tree is on.
                             #this gets set by parent

    def __len__(self):
        return (len(self.data))

class Bruters(Primative):
    """
        Our Bruter Class.
    """
    def __init__(self):
        Primitive.__init__(self)

class Dataflow:
    def __init__(self):
        self.stages = []

    def add_stage(self, to_add):
        """
            Add a Bruter, Primitive, or Dataflow
        """
        self.stages.append(to_add)

         
