#!/usr/bin/env python2.4
# This is testing the 'rolling pointer' method of tree traversal.
# We have a tree composed of three types of nodes.
#
# 1. "Primitives" are 'leaves', and can return only one value when asked. they
#       are effective 'scalar'.
# 2. "Bruters" are 'complex leaves' in that for each iteration through the tree
#       they return a different value each time.
# 3. "Dataflows" are 'branches'. They can contain any number of Bruters,
#       Dataflows, or Primitives.
#
# GOAL:
#   To traverse the tree getting all the possible permutations of that tree
#   with no repetitions. Also if run again, the same order of permutations has 
#   to be returned.

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
        if to_add.__class__ is Dataflow:
            to_add._parent = self #give our child a reference to us
        self._stages.append(to_add)
        self.permutations = self.calculate_permutations()
 
    def step(self):
        self.iter_count += 1
        for stage in self._stages:
            stage.step()

    def _print_tree(self, start_obj, padding):
        print padding[:-1] + "+-" + "Dataflow" + " (" + repr(start_obj.permutations) + " permutations)"
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
                else:
                    print  "%s+-%s (%d permutations)" % (padding, repr(stage.get_bytes()), stage.permutations)
        else:
            raise "You must provide a top level Dataflow object."

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
        bytes = data = []
        for stage in self._stages:
            if stage.__class__ is Dataflow:
                print "found dataflow"
                bytes.extend(stage.get_bytes()) #this looks right, but seems like
                                                #should be an append
        #check to see if our list contains lists
        for stage in bytes:
            if stage.__class__ is list:
                return(bytes)
        return "".join(self.flatten(bytes))

        
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
       self._data.append(value)
       self.permutations = 1

    def __len__(self):
        return len(self._data[0])

    def get_bytes(self):
        return self._data[0]

    def step(self):
        pass

class Bruter(Primitive):
    """
        Bruter class
    """
    def __init__(self):
        Primitive.__init__(self, value = None)
        self.step_index = 0

    def __len__(self):
        return len(self._data[self.step_index])

    def add_data(self, to_add):
        self._data.append(to_add)
        self.permutations = len(self._data)

    def get_bytes(self):
        return self._data[self.step_index]

    def step(self):
        """ 
            Increment the step index, but not past the end of our array
            it must cycle back to the beginning.
        """
        if self.step_index == (len(self._data) - 1):
            self.step_index = 0 #cycle back
        else:
            self.step_index += 1

# -----------------------------------------------
#   EVERYTHING ABOVE WILL BE DEFINED IN THE "API"
#   EVERYTHING BELOW IS THE DEVELOPER USING IT.
# ------------------------------------------------
if __name__ == '__main__':
    a_prim = Primitive(0x7777)
    b_prim = Primitive(0x8888)
    c_prim = Primitive(0x9999)

    a_brute = Bruter(); a_brute.add_data(0x1111); a_brute.add_data(0x2222)
    a_brute.add_data(0x3333)
#    b_brute = Bruter(); b_brute.add_data(0x4444); b_brute.add_data(0x5555)

    a_dflow = Dataflow()
    b_dflow = Dataflow()
    c_dflow = Dataflow()

    c_dflow.add_stage(a_prim)
    c_dflow.add_stage(b_prim)
#    c_dflow.add_stage(b_brute)

    b_dflow.add_stage(c_dflow)
    b_dflow.add_stage(a_brute)

    a_dflow.add_stage(b_dflow)
    a_dflow.add_stage(c_prim)
    
    a_dflow.execute()

    print "\n\n\n !!! NOTE: !!!\n\t 1. all the inherited permutations from child Dataflow to parent."
    print "\t 2. With each iteration, different values are returned for each multi-permutation object."
