"""

    RUXXER TYPES:
    ------------
    This is where all RuXXer datatypes are defined.
    These are types specific to the Ruxxer object model
    they arent the types as defined specifically for the grammar
    they are the types for Ruxxer's object model within the Ruxxer-API
    The types defined in here are linked to to the Grammar in grammar.py


    There are two primary types defined here in this Object Model.
    
"""

# A NOTE ON CODING STYLE:
#
# -->  The "_" attributes of an class ideally are values that never get
#      modified by anyone else reaching in from the outside.
#      Ideally they are modified, changed, or accessed only by exposed functions... 
#       

from binascii import hexlify
import struct

class Primitive:
    """

    This class defines the core functionality of the 
    Ruxxer "Primitive" class.
    
    The idea of a "Ruxxer" Object is really an abstraction that occurs
    up in the language it doesnt actually happen here in the object model.
    Here in the API, "Ruxxers" are just rebranded Primitives.
    
    Classes that extend from Primitive must implement their own
    setval() and getval() routines.

    """
    # SET LOGIC AND MUTATIONS:
    # ------------------------
    # A note on the Set Logic that powers the Graph Traversal and
    # Mutations....
    # Obviously the Algorithms that power generation of the Mutations
    # of Primitives are different for each different Mutator Mode 
    # so to keep it clean, all the methods that are specific to the
    # to a given Mutation Mode get appended with name of the mode that
    # they are for. For instance, for "linear" we append:
    #   _linear to all member functions that touch logic specfic to that
    #   traversal mode. 
     
    def __init__(self, value=None):
        self.env_ref = None #
        self._values = [] # the set that holds the actual value(s).
                           # if the Primitive gets Ruxxed then this gets
                           # "expanded" to have wihat appears to be multiple
                           # values.
        self._cardinality = 1
        self._values.append(value)
        self._state_index = self._si = 0

        #------
        self._packop = "" #a place to preserve the packing opcode
                             #used by struct.pack() and .unpack()

    def __len__(self):
        """
        The customized length calculation routine.
        KEEP IN MIND this is for the length of the value contained
        by this primitive, NOT the Cardinality of a Ruxxed Primitive.
        """
        return len(self._values[self._si])

    def __repr__(self):
        """
        The customized function for how to go about representing 
        the data that this object contains.
        """ 
        disp_buf = "" #Place to build buffer we ultimately return
        if type(self._values[self._si]) is not str:
            raise "Value stored within Primitive is NOT PACKED!!!!"

        for byte in self._values[self._si]:
            disp_buf+='\\x'+hexlify(byte)
        return disp_buf

    def _set_state_index(self, arg):
        """
            Set the state of the internal State Index.
            *** USE WITH CARE!!! ***
        """
        if type(arg) is not int:
            raise "State Index must only be set to an integer."
        else:
            self._state_index = arg  
        
    def calc_cardinal(self):
        """
        Get and return the cardinality of the of the _values set.
        This should obviously always be 1 on NONRuxxed Primitives. 
        """
        cardinality = len(self._values)
        if cardinality < 1:
            raise "ERROR: Cardinality somehow less than one."
        else:
            return (len(self._values))

    def expand(self):
        """
        This method (along with the "select" method) is the core of the 
        solution to the "Resourse Problem" see the section "Resource Problem"
        for a thorough description of the problem/solution
        in docs/DESIGN_NOTES.TXT
    
        The core idea here is to support the "first pass" that precalculates
        the cardinality of a Ruxxed Primitive.
        """
        pass
            
    def select(self):
        """
        So which item to select from the _values set? Calculate this value
        based on the internal state and return it.
        This is core functionality for the solution to the "Resource Problem".    
        """
        pass
   
    def isRuxxed(self):
        """
            Return boolean if this Primitive has been Ruxxed or not.
        """
        if(self.calc_cardinal() > 1):
            return True
        else:
            return False
    
    def setval(self, value):
        """
        This function will probably ultimately get overloaded in classes that
        extend from the Primitive class.

        """
        try:
            self._values[self._si] = struct.pack(self._packop, value)
        except struct.error:
            print "Error while packing."

    def getval(self):
        """
        This function will probably ultimately get overloaded in classes that
        extend from Primitive.

        """
        return (self._values[self._si]) 

    def getval_unp(self):
        """
            This method just gets the value in an unpacked form,
        should we have to do some stuff interally with python.
        """
        return (struct.unpack(self._packop, self._values[self._si])[0]) 

class Structure:
    """

    This class defines the core functionality of the 
    Ruxxer "Structure" class.

    """
    def __init__(self):
        self.env_ref = None #This attribute stores a reference to the 
                            #environment class
        self._values = {}
        self._parent = None #Only root Structures should end up having this
                            #remain unset.

    def push(self, *args):
        """

        This method is used to add objects into a Structure.
        
        Usage:
            a_struct.push(some_primitive) 

        """
        #eventually this should proabably take a "name" argument or something
        #to be the key value in the dictionary. 
        for arg in args:
            if isinstance(arg, (Structure, Primitive)): # check if its 
                                                        # something we can deal
                                                        # with
                self._values[arg] = arg #push it into our dictionary
                if isinstance(arg, (Structure)):
                    if self._values.get(arg)._parent is None:
                        self._values.get(arg)._parent = self #Set child's parent attrib.
                    else:
                        raise "Structure instance is already attached to another Strucure." 
            else:
                raise "Structures can only contain Primitives and Structures!!!"

    def __len__(self):
        """
        Calculate the length of this structure, which is a cumulative sum
        of all the lengths of the Primitives and Structures it contains.
        """
        cum_len = 0
        #"child" is just used here to imply the relationship
        #the objects have to the parent Structure
        for child in self._values.keys():
            cum_len+=len(child)
        return cum_len             
        
    def __repr__(self):
        """
        The customized function for how to go about representing 
        the data that this object contains.
        """ 
        outbuf = "" #The buffer we use to build a string representing the 
                    #structure
        for val in self._values.values():
            outbuf += repr(val)
        return outbuf

    def getval(self):
        """
        Get the actual concatenated bytes. dont try to represent 
        the data specifically as a string.
        """
        for val in self._values.values():
            outbuf += val.getval()
        return outbuf
 
class Environment:
    """
    This class serves simply as a clean place to store environmental
    information. The two most algorithmically relevant bits of info
    stored here:

        --> Mutation Modes.
        --> Number of Runs to perform.

    Each primitive and structure gets a reference to this Environment
    class. They rely on information to perform the Graph Traversal
    during Mutation.

    The Environment object is used mostly to hold values needed by
    the Session object.    
    """
    def __init__(self):
        self._runs = 1
        self._mmode = "linear"
        self._supported_mmodes = ("linear","interleaved","random",
                                    "linear-rightmost", "linear-leftmost")

    def set_runs(self, arg):
        """

        Set the number of times a single session will execute.

        """
        if type(arg) is int: 
            self._runs = arg 

    def get_runs(self):
        """
        Return the number of runs currently set. 
        """ 
        return(self._runs)

    def set_mode(self, new_mode):
        """
        Set the Mutator Mode.
        """
        if new_mode.lower() not in self._supported_mmodes:
            raise "Unsupported Mutator Mode."
        else:
            self._supported_mmodes = new_mode.lower()
 
    def get_mode(self):
        """
        Return the current Mutator Mode.
        """
        return(self._mmode)

class SessionCore:
    """

    This class contains all the logic for the the execution of a session.
    All the pieces come together in here...this is where the session begins and
    ends.
    """
    pass

#--------------- The API's Abstracted classes follow ------------       

class Int(Primitive):
    """
    A Ruxxer 32 bit integer.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop="i"

class UInt(Primitive):
    """
    A Ruxxer Unsigned Integer.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop="I"

class Short(Primitive):  
    """
    A Ruxxer Short.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop="h"

class UShort(Primitive):  
    """
    A Ruxxer Unsigned Short.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "H"

class Long(Primitive):  
    """
    A Ruxxer LongInt
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "l"

class ULong(Primitive):  
    """
    A Ruxxer Unsinged LongInt
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "L"

class Float(Primitive):  
    """
    A Ruxxer Float.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "f"

class Double(Primitive):  
    """
    A Ruxxer Double.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "d"

class String(Primitive):
    """
    A Ruxxer String
    """
    def __init__(self):
        Primitive.__init__(self)
        struct._packop = "s"

    def getval(self, value):
        """
            Custom overload, struct.pack('s', ..) doesnt work correctly.
        """
        return self._values[self._si]
        
    def setval(self, value):
        """
            Custom overload, struct.unpack('s', ...) doesnt work correctly.
        """
        self._values[self._si] = value

class Char(Primitive):
    """
    A Ruxxer Character.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "c"

class Byte(Primitive):
    """
    A Ruxxer Byte.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "b"

class UByte(Primitive):
    """
    A Ruxxer Unsigned Byte.
    """
    def __init__(self):
        Primitive.__init__(self)
        self._packop = "B"

#--------------- LENGTH CALCULATORS ----------------
#   Length calculator primitives allow us to have fields
#   that work like a "sizeof()" as specific field in a protocol.
# --------------------------------------------------

class Int_lc(Int):
    """
    A Length Calculator stored as an Integer.
    """
    def __init__(self, ref):
        Int.__init__(self)
        self._lctarget = ref #A reference to the object that this class
                           #serves as a length calculator to. 
    def getval(self):
        """
        Get the length of the object that this serves  as a length calculator for. Pack
        this value according to what type we are, and return this value. 
        """
        retval = struct.pack(self._packop, len(self._lctarget))
        return retval
    
    def getval_unp(self):
        """
        Just like "getval()" but do it unpacked.
        Get the length of the object that this serves as a length calculator
        for and just return the value back unpacked.
        """
        return len(self._lctarget) 
    
    def setval(self):
        """
        
        """
        #We dont want any accidents with inheriting the setvalue from in
        #Primitive.
        pass 

class UInt_lc(Primitive):
    """
    A Length Calculator stored as an Unsigned Integer.
    """
    def __init__(self, ref):
        UInt.__init__(self)
        self._lctarget = ref #A reference to the object that this class
                           #serves as a length calculator to. 
    def getval(self):
        """
        Get the length of the object that this serves  as a length calculator for. Pack
        this value according to what type we are, and return this value. 
        """
        retval = struct.pack(self._packop, len(self._lctarget))
        return retval
    
    def getval_unp(self):
        """
        Get the length of the object that this serves as a length calculator
        for and just return the value back unpacked.
        """
        return len(self._lctarget) 
    
    def setval(self):
        """
        
        """
        #We dont want any accidents with inheriting the setvalue from in
        #Primitive.
        pass 

class Short_lc(Primitive):  
    """
    A Length Calculator stored as a Short.
    """
    def __init__(self, ref):
        Short.__init__(self)
        self._lctarget = ref #A reference to the object that this class
                           #serves as a length calculator to. 
    def getval(self):
        """
        Get the length of the object that this serves  as a length calculator for. Pack
        this value according to what type we are, and return this value. 
        """
        retval = struct.pack(self._packop, len(self._lctarget))
        return retval
    
    def getval_unp(self):
        """
        Get the length of the object that this serves as a length calculator
        for and just return the value back unpacked.
        """
        return len(self._lctarget) 
    
    def setval(self):
        """
        
        """
        #We dont want any accidents with inheriting the setvalue from in
        #the Primitive class.
        pass 

class UShort_lc(Primitive):  
    """
    A Length Calculator stored as an Unsigned Short.
    """
    def __init__(self, ref):
        UShort.__init__(self)
        self._lctarget = ref #A reference to the object that this class
                           #serves as a length calculator to. 
    def getval(self):
        """
        Get the length of the object that this serves  as a length calculator for. Pack
        this value according to what type we are, and return this value. 
        """
        retval = struct.pack(self._packop, len(self._lctarget))
        return retval
    
    def getval_unp(self):
        """
        Get the length of the object that this serves as a length calculator
        for and just return the value back unpacked.
        """
        return len(self._lctarget) 
    
    def setval(self):
        """
        
        """
        #We dont want any accidents with inheriting the setvalue from in
        #Primitive.
        pass 

class Long_lc(Primitive):  
    """
    A Length Calculator stored as a LongInt
    """
    def __init__(self, ref):
        Long.__init__(self)
        self._lctarget = ref #A reference to the object that this class
                           #serves as a length calculator to. 
    def getval(self):
        """
        Get the length of the object that this serves  as a length calculator for. Pack
        this value according to what type we are, and return this value. 
        """
        retval = struct.pack(self._packop, len(self._lctarget))
        return retval
    
    def getval_unp(self):
        """
        Get the length of the object that this serves as a length calculator
        for and just return the value back unpacked.
        """
        return len(self._lctarget) 
    
    def setval(self):
        """
        
        """
        #We dont want any accidents with inheriting the setvalue from in
        #Primitive.
        pass 

class ULong_lc(Primitive):  
    """
    A Length Calculator stored as an Unsigned Long.
    """
    def __init__(self, ref):
        ULong.__init__(self)
        self._lctarget = ref #A reference to the object that this class
                           #serves as a length calculator to. 
    def getval(self):
        """
        Get the length of the object that this serves  as a length calculator for. Pack
        this value according to what type we are, and return this value. 
        """
        retval = struct.pack(self._packop, len(self._lctarget))
        return retval
    
    def getval_unp(self):
        """
        Get the length of the object that this serves as a length calculator
        for and just return the value back unpacked.
        """
        return len(self._lctarget) 
    
    def setval(self):
        """
        
        """
        #We dont want any accidents with inheriting the setvalue from in
        #Primitive.
        pass 

class Float_lc(Primitive):  
    """
    A Length Calculator stored as a Float...somehow.
    """
    def __init__(self, ref):
        Float.__init__(self)
        self._lctarget = ref #A reference to the object that this class
                           #serves as a length calculator to. 
    def getval(self):
        """
        Get the length of the object that this serves  as a length calculator for. Pack
        this value according to what type we are, and return this value. 
        """
        retval = struct.pack(self._packop, len(self._lctarget))
        return retval
    
    def getval_unp(self):
        """
        Get the length of the object that this serves as a length calculator
        for and just return the value back unpacked.
        """
        return len(self._lctarget) 
    
    def setval(self):
        """
        
        """
        #We dont want any accidents with inheriting the setvalue from in
        #Primitive.
        pass 


