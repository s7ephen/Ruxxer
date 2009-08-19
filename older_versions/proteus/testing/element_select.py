#!/usr/bin/env python2.4
#
#
#ALGORITHM:
#-----------
# This is testing the direct selection of elements based on a simple algorithm
# Its really hard for me to explain but basically here is an example of it
# working, this seems to work for every combination I throw at it.
#
#   M = [1,2,3]
#   N = ['A', 'B', 'C']
#   O = ['a']
#   
#   def getvalue2(val):
#       origval = val
#       x = val / (len(N) * len(O)) % len(M)
#       y = val / (len(O)) % len(N)
#       z = val % len(O)
#       print "%d: [%d,%d,%d]" % (origval, x, y, z)
#   
#   for i in range(0, 9): #hand calculated permutations
#       getvalue2(i)
#   
# OBJECT MODEL:
# -------------
# 1. "Primitives" are 'leaves', and can return only one value when asked. they
#       are effective 'scalar'.
# 2. "Bruters" are 'complex leaves' in that for each iteration through the tree
#       they return a different value each time.
# 3. "Dataflows" are 'branches'. They can contain any number of Bruters,
#       Dataflows, or Primitives.
#
# GOAL:
# -----
#   To traverse the tree getting all the possible permutations of that tree
#   with no repetitions. Also if run again, the same order of permutations has 
#   to be returned.
#
#
import struct

class Dataflow:
    """

        Dataflow class.

    """
    def __init__(self):
        self._stages = []
        self._parent = None
        self.permutations = 0
        self.iter_count = 0

    def calculate_permutations(self):
        my_perms = []
        permutations = 1 
        for stage in self._stages:
            my_perms.append(stage.permutations)
        for perm in my_perms:
            permutations *= perm
        return permutations

    def add_stage(self, to_add):
        to_add._parent = self #give our child a reference to us
        self._stages.append(to_add)
        self.permutations = self.calculate_permutations()
 
    def step(self):
        self.iter_count += 1
        for stage in self._stages:
            stage.step()

    def _print_tree(self, start_obj, padding):
        print padding[:-1] + "+-" + "Dataflow" + " (" + repr(start_obj.permutations) + " permutations)" + ":" + repr(start_obj.get_bytes())
        padding += ' ' # add a space
        count = 0
        if start_obj.__class__ is Dataflow:
            for stage in start_obj._stages:
                count += 1
                print padding + "|"
                if stage.__class__ is Dataflow:
                    if count==len(stage._stages):
                        self._print_tree(stage, padding)
                    else:
                        self._print_tree(stage, padding + "|")

                elif stage.__class__ is Bruter:
#                    print  "%s+-Bruter (%d permutations) (%d peers to the right) (%d right peer permutations) %d" % (padding, stage.permutations, stage.get_rightpeer_count(), stage.get_rightpeer_perms(), stage.step_index)
                    print  "%s+-Bruter (%d permutations): %s" % (padding, stage.permutations, repr(stage.get_bytes()))
#                    print  "%s+-Bruter (%d permutations) on element: %d" % (padding, stage.permutations, stage.step_index)
                else:
                    print  "%s+-Primitive: %s" % (padding, repr(stage.get_bytes()))
        else:
            raise "You must provide a top level Dataflow object."

    def _get_childs_rightpeer_count(self, child):
        """
            Find child in _stages and tell it how many peers it has
            to the right of it.
    
            NOTE! this algorithm doesnt allow for copies of the same instance in
                 _stages . this MUST BE FIGURED OUT!
        """
        child_index = 0
        for stage in self._stages:
            if stage == child:
                break
            child_index += 1
        #for now assume the child is actually in there.
        return ((len(self._stages)-1) - child_index)

    def _get_childs_rightpeer_perms(self, child):
        """
            Find child in _stages and calculate all the permutations
            to the right of it.
        """
        child_index = 0
        right_perms = 1
        for stage in self._stages:
            if stage == child:
                break
            child_index += 1
        #for now assume the child is actually in there.
        for stage in self._stages[(child_index+1):]: #we *dont* want to also
                                                     #include childs
                                                     # permutation count in this
                                                     # calculation
            right_perms *= stage.permutations
        return (right_perms)

    def flatten(self, lis):
        """
            Flatten a list of objects. used recursively to return pdt contents
        to the caller.
        """
        ret_list = []
        for val in lis:
            if val.__class__ is list:
                ret_list.extend(self.flatten(val))
            else:
                ret_list.append(lis)
                break
        return ret_list

    def get_bytes(self):
        """
            Check all potential children for data, concatentate, and return
        as *my* data.

        """
        bytes = []
        for stage in self._stages:
            if stage.__class__ is Dataflow:
                bytes.extend(stage.get_bytes()) #this looks right, but seems like
                                                #should be an append
            else:
                bytes.append(stage.get_bytes())
        return "".join(bytes)

    def execute(self):
        while self.iter_count < self.permutations:
            print "\n"
            print " -- ITERATION %d --" % (self.iter_count + 1) #+1 just for
                                                                #readability
            self._print_tree(self, " ")
            self.step()

class Primitive:
    """

        Primitive class.

    """
    def __init__(self, value):
        self._data = []
        self._data.append(struct.pack("l", value)) #for now use longs.
        self.permutations = 1 #must be 1 for later multiplication
        self._parent = None #umbilical cord ;-), filled in by parent

    def __len__(self):
        return len(self._data[0])

    def get_bytes(self):
        return self._data[0]
    
    def get_parent(self):
        """
            Return a reference to parent.
        """
        return self._parent

    def step(self):
        pass

class Bruter(Primitive):
    """
        Bruter class
    """
    def __init__(self, *values):
        Primitive.__init__(self, values[0])
        if len(values) > 1:
            for value in values[1:]:
                self.add_data(value)
        self.step_index = 0

    def __len__(self):
        return len(self._data[self.step_index])

    def add_data(self, to_add):
        self._data.append(struct.pack('l', to_add))
        self.permutations = len(self._data)

    def get_bytes(self):
        if type(self._data[self.step_index]) is not str:
            return repr(self._data[self.step_index])
        return self._data[self.step_index]

    def get_rightpeer_count(self):
        """
            Ask parent how many peers there are to my right.
        """
        parent = self.get_parent()
        right_count = parent._get_childs_rightpeer_count(self)
#        print "%s has %d peers to the right" % (repr(self), right_count)
        return (right_count)

    def get_rightpeer_perms(self):
        """
            Ask parent what the product of the permutations of all my rightmost peers is.
        """
        parent = self.get_parent()
        right_perms = parent._get_childs_rightpeer_perms(self)
#        print "%s has %d permutations to the right" % (repr(self), right_perms)
        if parent._get_childs_rightpeer_count(self) == 0:
            return 0

        return (right_perms)

    def get_iter_count(self):
        """
            Get parents iter_count, which is actually the iteration
        the entire tree is on.
        """
        return (self.get_parent().iter_count)


    def is_rightmost(self):
        if self.get_rightpeer_count() == 0:
            return True
        else: return False        
            
    def calc_permutation_selection(self):
        """
            Find out which permutation I must return for this iteration.
        """
        parent = self.get_parent()
        iter_count = parent.iter_count
        element = None

        #If we are the rightmost node:
        if self.is_rightmost(): 
            element = iter_count % self.permutations

        #If we are anyone other than the two rightmost
        if not self.is_rightmost():
            element = iter_count / (self.get_rightpeer_perms() % self.permutations)
        
        return element
 
    def step(self):
        """
            For every step we calculate which element we should select from
            our permutations. 
        """
        self.step_index = self.calc_permutation_selection()

# -----------------------------------------------
#   EVERYTHING ABOVE WILL BE DEFINED IN THE "API"
#   EVERYTHING BELOW IS THE DEVELOPER USING IT.
# ------------------------------------------------
if __name__ == '__main__':
    a_dflow = Dataflow()
    b_dflow = Dataflow()
    c_dflow = Dataflow()
    c_dflow.add_stage(Primitive(0x7777))
    c_dflow.add_stage(Primitive(0x8888))
    c_dflow.add_stage(Bruter(0x4444,0x5555))
    c_dflow.add_stage(Primitive(0x7777))

#    b_dflow.add_stage(c_dflow)
    b_dflow.add_stage(Bruter(0x1111,0x2222,0x3333))
    b_dflow.add_stage(Primitive(0x7777))
    b_dflow.add_stage(Bruter(0x4444,0x5555))

    a_dflow.add_stage(b_dflow)
    a_dflow.add_stage(Primitive(0x9999))
    
    a_dflow.execute()
    print "\n\n\n !!! NOTE: !!!\n\t 1. all the inherited permutations from child Dataflow to parent."
    print "\t 2. With each iteration, different values are returned for each multi-permutation object."
