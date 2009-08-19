"""
    PythonLib

    This is the home of the class definitions for the core of the Proteus API.
Because most of the Proteus logic exists as methods inside the Proteus data
types, this is actually the core of most of Proteus as a whole.

"""

#THE PROTEUS API CORE MANTRA
#---------------------------
#    1. All Bruters take PDT instance references at init.
#    2. PDT's take values (python primitives) at init, except 'length calculator' PDTs which
#       instead take a PDT instance reference.


#TODO:
#  1. figure out how to have an imported module "be" an object instance.
#       For example: how to get dataflow .py's to actually be Dataflow
#                    class instances. I think this is possible with some
#                   magic in __init__.py. like maybe by "shaping" the 
#                   the imported module by passing it through Dataflow.__init__
#                   or something. 
#
import os
import sys
import struct
import time
import pprint
from threading import Thread
import ConfigParser as CP
import pygtk
import socket
import urllib
import getopt
#import gtk
import md5

from random import Random
from binascii import hexlify
from cmd import Cmd
#from lib.transports import *
#from lib.protocols import *

def prepr(bytes):
    """
        Proteus's repr(). It forces display as escaped bytes *even*
        when the value is within printable ascii range (unlike repr()).

        EG: \\xde\\xad\\xbe\\xef

    """
    retstr = ""
    if issubclass(bytes.__class_, str):
        for byte in bytes:
            retstr+='\\x'+hexlify(byte)
        return retstr
    else: #we cant handle those types so just default to the normal repr()
        print "Proteus error. The custom Proteus repr() can not handle %s" %\
            bytes.__class__
        repr(bytes)

class BasePDT:
    """ 
        This is the base class from which all PDT's (Proteus Data Types) extend.
    It defines the skeletal structure that *all* PDT's should have. Thus any
    and all PDT's *must* extend from this base class.

    """
    def __init__(self):
        self._data = [] # a list of packed bytes.
                        # basic pdt's never use more than the
                        # first element in this list. Everything after
                        # the first element are values for future iterations
        self.permutations = 1 #for naming consistency 'permutations' is a
                                    #synonym only in this class
        self._parent = None #placeholder for reference to parent
        self.step_index = 0
        self.endian = "NA" #Native endianness...(obviously only used by
                            #numeric PDT's

    def __len__(self):
        """
            Hook so that len() returns the correct length at the 
        present iteration we are on.
        """
        return len(self._data[self.step_index])

    def get_bytes(self):
        """
            Retrieve data from the PDT. Internally all PDT data
        is stored as packed bytes. This method receives those
        bytes as they are, raw bytes.
        """
        return self._data[self.step_index]

    def step(self):
        """
            While PDT's are "one-dimensional" or "scalar" and always return the
        same value, the more complex datatypes that extend from BasePDT like 
        Bruters return different values depending on which iteration the whole
        Dataflow is on. This method steps forward the iteration count.
        """
        pass

    def set_iter_count(self, iter):
        """
            This like .step() goes mostly unused here but does get used in
        Bruters which extend from PDTs.

        """
        pass

    def get_parent(self):
        """
            Return a reference to our parent object. (most likely to be a
        Dataflow.
        """
        return self._parent

    def push(self, data):
        """
            A small function to push data into the ._data list.
        (save keystrokes :-)
        """
        self._data.append(data)

    def pack(self, pack_char, data):
        """
            A pack function to wrap struct.pack(). We do this to make
        it accomodate an "endianness" argument.
        """
        if self.endian=="BE":
            pack_char = ">"+pack_char
        if self.endian == "LE":
            pack_char = "<"+pack_char
        if self.endian == "NA": #use native
            pack_char = "="+pack_char
        
        return(struct.pack(pack_char, data))

    def unpack(self, pack_char, data):
        """
            A unpack function to wrap struct.unpack(). We do this to make
        it accomodate an "endianness" argument.
        """
        if self.endian=="BE":
            pack_char = ">"+pack_char
        if self.endian == "LE":
            pack_char = "<"+pack_char
        if self.endian == "NA": #use native
            pack_char = "="+pack_char
        
        return(struct.unpack(pack_char, data))

class Bruter(BasePDT):
    """
        This is the base class of for Bruters. All Bruters must extend from
    this. New Bruters will have to overload 
    """
    def __init__(self):
        BasePDT.__init__(self)

    def _add_permutation(self, to_add):
        """
            This method is an internally used method that adds an additional
        "permutation" or variation to this Bruters list of permutations.

        Remember:
            One permutation is returned for each iteration.
        """
        self._data.append(to_add)
        self.permutations = len(self._data)

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
            Ask parent what the product of the permutations of all my rightmost
        peers is.
        """
        parent = self.get_parent()
        right_perms = parent._get_childs_rightpeer_perms(self)
#        print "%s has %d permutations to the right" % (repr(self), right_perms)
        if parent._get_childs_rightpeer_count(self) == 0:
            return 0

        return (right_perms)

    def get_iter_count(self):
        """
            Found out which iteration we are on, by asking our parent which
        iteration they are on.
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
            element = iter_count / self.get_rightpeer_perms() % self.permutations
        return element

    def step(self):
        """
            For every step we calculate which element we should select from
            our permutations.
        """
        self.step_index = self.calc_permutation_selection() 
#        print "%s (%d,%d)" % (repr(self), self.get_parent().iter_count, self.step_index)

    def set_iter_count(self, iter):
        self.iter_count = self.step_index = int(iter)

class UnsignedBytePDT(BasePDT):
    """
        A Unsigned Byte. 

    Width: 8 bits, 1byte
    Range: 0 to 255
    Defaults to 0x99 if not specified. 
    """
    def __init__(self, data=0x99, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('B', data))

class SignedBytePDT(BasePDT):
    """
        A Signed Byte. 
    
    Width: 8 bits, 1 byte
    Range: -128 to 127
    Defaults to 0x01 if not specified. 
    """
    def __init__(self, data=0x01, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('b', data))

BytePDT = UnsignedBytePDT #this needs to be changed to SignedBytePDT
                          #when dataflows have been corrected

UBytePDT = UnsignedBytePDT

class UnsignedShortPDT(BasePDT):
    """
        Unsigned Short. 

    Width: 16 bites, 2 bytes 
    Range: 0 to 65,535
    Defaults to 0x9999 if not specified. 
    """
    def __init__(self, data=0x9999, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('H', data))

UShortPDT = UnsignedShortPDT

class SignedShortPDT(BasePDT):
    """
        Signed Short 

    Width: 16 bites, 2 bytes
    Range: -32,768 to 32,767
    Defaults to 0x0001 if not specified. 
    """
    def __init__(self, data=0x0001, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('h', data))

ShortPDT = SignedShortPDT

class UnsignedLongPDT(BasePDT):
    """
        Unsigned Long Integer. 
    
    Width: 32 bits, 4 bytes 
    Range:
    Defaults to 0x99999999 if not specified.
    """
    def __init__(self, data=0x99999999, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('L', data))

ULongPDT = UnsignedLongPDT

class SignedLongPDT(BasePDT):
    """
        Signed Long Integer. 

    Width: 32 bits, 4 bytes 
    Range:
    Defaults to 0x00000001 if not specified.
    """
    def __init__(self, data=0x00000001, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('l', data))

LongPDT = SignedLongPDT

class UnsignedDoublePDT(BasePDT):
    """
        Unsigned Long Long Integer. 
  
    Width: 64 bits, 8 bytes
    Range:
    Defaults to 0x9999999999999999 if not specified.
    """
    def __init__(self, data=0x9999999999999999, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('Q', data))

UDoublePDT = UnsignedDoublePDT

class SignedDoublePDT(BasePDT):
    """
        Signed Long Long Integer. 

    Width: 64 bits, 8 bytes
    Range:
    Defaults to 0x0000000000000001 if not specified.
    """
    def __init__(self, data=0x0000000000000001, endian="NA"):
        BasePDT.__init__(self)
        self.endian = endian
        self.push(self.pack('q', data))

DoublePDT = SignedDoublePDT

class RandomPDT(Random, BasePDT):
    """
        A base Random Class for all "radomized" PDT's to extend from.
    It is important that they all extend from this type because in Proteus
    there has to be pseudo-randomness for replicability sake, so we must
    seed with the same values.
    """
    def __init__(self):
        BasePDT.__init__(self)
        Random.__init__(self, "Between the thought and the act falls the shadow.")
        
class RandBytePDT(RandomPDT):
    """
        A random Unsigned Byte PDT.
    """
    def __init__(self, endian="NA"):
        RandomPDT.__init__(self)
        self.endian = endian
        self.push(self.pack('B', self.randint(0, 0xff)))

class RandShortPDT(RandomPDT):
    """
        A random Unsigned Short PDT.
    """
    def __init__(self, endian="NA"):
        RandomPDT.__init__(self)
        self.endian = endian
        self.push(self.pack('H', self.randint(0, 0xffff)))

class RandLongPDT(RandomPDT):
    """
        A random Unsigned Long PDT.
    """
    def __init__(self, endian="NA"):
        RandomPDT.__init__(self)
        self.endian = endian
        self.push(self.pack('L', self.randint(0, 0xffffffff)))

class RandDoublePDT(RandomPDT):
    """
        A random Unsigned Double PDT.
    """
    def __init__(self, endian="NA"):
        RandomPDT.__init__(self)
        self.endian = endian
        tmpDouble = self.getrandbits(20)
        self.push(self.pack('Q', tmpDouble))

class FileReaderPDT(BasePDT):
    """
        A Special PDT who's initial value is set by reading in the contents
    of a file on the filesystem. This PDT is the basis of any "blind" file
    fuzzer.
    
    Usage:
        some_string = FileReaderPDT("./infile.bin")

    """
    def __init__(self, filename):
        BasePDT.__init__(self)
        try:
            #statinfo = os.stat(filename)
            # Note: not able to parse absolute paths on Windows
            # Because the : in the path messes it up
            tmp_h = os.open(filename, 0777)
            data = tmp_h.read()
        except OSError, e:
            raise "FileReaderPDT Error: Unable to read file: ", filename
        os.close(tmp_h)
        self.push(data)
        #del(os)

class GarbageBytesPDT(RandomPDT):
    """
        A special PDT that accepts a desired length as argument and generates
    a pseudorandom string of "garbage" bytes to the length requested.

    Usage:
        some_string = GarbageBytesPDT(128)
    
    """
    def __init__(self, length):
        RandomPDT.__init__(self)
        count = 1
        retstr = ""
        if length <= 0:
            raise "GarbageBytesPDT Error: Length argument must be greater than zero."
        while count <= length:
            retstr += self.pack('B', self.randint(0, 0xff))
            count+=1
        self.push(retstr)

class GarbageASCIIBytesPDT(RandomPDT):
    """
        Very similar to the GarbageBytesPDT except that this one only generates
    byte values that are within the printable ASCII range.

    Usage:
        some_string = GarbageASCIIBytesPDT(128)

    """        
    def __init__(self, length):
        RandomPDT.__init__(self)
        count = 1
        retstr = ""
        if length <= 0:
            raise "GarbageBytesPDT Error: Length argument must be greater than zero."
        while count <= length:
            retstr += self.pack('B', self.randint(0x21, 0x7e))
            count+=1
        self.push(retstr)


class StringPDT(BasePDT):
    """
        A string datatype. Defaults to 'str1' if not specified.
    """
    def __init__(self, data='str1'):
        BasePDT.__init__(self)
        self.push(data)

class EmailPDT(BasePDT):
    """
        An email datatype
        Pass in a local-name, hostname, and top-level domain name
    """
    def __init__(self, lName='email', hName='mcafee', dName='com'):
        BasePDT.__init__(self)
        self.localName = StringPDT(lName)
        self.hostName = StringPDT(hName)
        self.domainName = StringPDT(dName)
        self.push(lName + '@' + hName + '.' + dName)

class RepeaterStringPDT(StringPDT):
    """
        A Repeater String Type
        
        EXAMPLE USAGE:
            RepeaterString("CHEESE", 200)
       
        This PDT takes a string and a repeat count as arguments.
    It will generate a string with the seed string ('CHEESE') appended to 
    itself "count" (200) times.

    """
    def __init__(self, data="TEST", count=5):
        StringPDT.__init__(self, data*count)


class ZlibDataPDT(StringPDT):
    """
        A String of GZIP encoded data.

        EXAMPLE USAGE:
            ZlibDataPDT("CHEESE")

        This PDT will take a string of bytes as an argument and store
    it as a normal StringPDT would, but simply zlib encode the data first.
    """
    def __init__(self, data="CHEESE"):
        data = data.encode('zlib') 
        StringPDT.__init__(self, data)

class Base64DataPDT(StringPDT):
    """
        A String of Base64 encoded data.

        EXAMPLE USAGE:
            Base64DataPDT("CHEESE")

        This PDT will take a string of bytes as an argument and store
    it as a normal StringPDT would, but simply gzip encode the data first.
    """
    def __init__(self, data="CHEESE"):
        data = data.encode('base64') 
        StringPDT.__init__(self, data)

class URLEncodedDataPDT(StringPDT):
    """
        A String of URLEncoded encoded data.

        EXAMPLE USAGE:
            URLEncodedDataPDT("CHEESE")

        This PDT will take a string of bytes as an argument and store
    it as a normal StringPDT would, but simply URL encode the data first.
    """
    def __init__(self, data="CHEESE"):
        data = urllib.quote(data) 
        StringPDT.__init__(self, data)

class ByteLenPDT(BytePDT):
    """
        A Length Calculator.
        Pass in a PDT and this will return its length as a byte.
    """
    def __init__(self, pdt):
        BytePDT.__init__(self, len(pdt))

class ShortLenPDT(ShortPDT):
    """
        A Length Calculator.
        Pass in a PDT and this will return its length as a Short
    """
    def __init__(self, pdt):
        ShortPDT.__init__(self, len(pdt))

class LongLenPDT(LongPDT):
    """
        A Length Calculator.
        Pass in a PDT and this will return its length as a Long
    """
    def __init__(self, pdt):
        LongPDT.__init__(self, len(pdt))

class DoubleLenPDT(DoublePDT):
    """
        A Length Calculator.
        Pass in a PDT and this will return its length as a Double
    """
    def __init__(self, pdt):
        DoublePDT.__init__(self, len(pdt))

class Dataflow:
    """
        Dataflows are the core to the Proteus object model. They are the 
    core structure that allows for PDT's to be constructed into structures.
    Although the 'session' files are also called dataflows this is simply
    because the 'top level' dataflow that the user defines is actually what is 
    "executed".

    """
    def __init__(self, name):
        self._transport = None #The actual instance of the Transport
        self._transport_co = None #The "class object" of the Transport, for
                                  #storage until runtime
        self._transport_args = None #arguments the user wanted for the Transport
        self._stages = [] 
        self._parent = None
        self._name = name # Dataflows must have a name assigned.
        self.permutations = 0 # A placeholder for what will be an permutation 
                               # count
        self.iter_count = 0
        self._start_time = None #this get sets at .execute() time.
        self._load_time = None #this gets set in the root dataflow at load time.
        self.PEC = None# Contains a reference to the instance of ProteusEnvConf
                 # This only gets set in the root Dataflow
                 # It exists here simply because we dont want to rely on it
                 # being anywhere else (like the CLI). We *do* however rely
                 # on someone else setting this value for us. currently the CLI

    def __del__(self):
        del(self._transport) 
        #some other stuff should probably happen here.

    def __len__(self):
        """
            This is a count of the total bytelength of the packed data in this
        Dataflow, *not* the number of stages in this dataflow. To get the 
        number of stages use get_stagecount().
        """
        count = 0
        for stage in self._stages:
            count+=len(stage)
        return count


    def add_stage(self, *additions):
        """
            Add data to the Dataflow. PDT's, Bruters, and other Dataflows can
        all be added.

        EXAMPLE USAGE:

            some_dataflow.add_stage(StringPDT("cheese is good"))
            
        or add multiple at a time:
        
            some_dataflow.add_stage(StringPDT("cheese is good"), \
                LongPDT(0xDeadBeef))

        """
        #If the object being added is a Dataflow, we
        #   1. tell him that we are his parent, then add him
        #       so that in effect every child dataflow has a link to his parent
        #   2. we update our permutation count to reflect that of our children

        for addition in additions:  
            if issubclass(addition.__class__, (BasePDT, Dataflow, Bruter)):
                if addition not in self._stages: #uniqueness is PARAMOUNT!!!
                    addition._parent = self
                    self._stages.append(addition)
                    self.permutations = self.calculate_permutations()
                else:
                    raise "%s already exists in %s" % (repr(addition), repr(self))
            else:
                raise "You can only add PDTs, Bruters, and other Dataflows to Dataflow objects!"

    def step(self):
        if self.iter_count+2 > self.permutations: #skip adding
            pass
#            raise "A dataflow attempted to step past amount of its permutations."
        self.iter_count += 1
#        if self.isRoot(): #then we are the root Dataflow so step the transport.
#            if self._transport != None: #then the transport is instantiated.
#                self._transport.step()
#            else:
#                raise "Dataflow ERROR: Root Dataflow can not step() Transport."

        for stage in self._stages: #recurse downward.
            stage.step()

    def isRoot(self):
        """
            Check if we have a parent. If not then we are technically a root
        Dataflow.
            
            Note:
                It could also be that we dont have children and are just a
            dangling Dataflow.

        """
        if self._parent == None:
            return True
        else:
            return False

    def set_iter_count(self, iter):
        """
            Used in fastforwarding. Recursively step()s until an iteration is
        reached.
        
            Usage:
                set_iter_count(1)  <-- first iteration.

        """
        if iter > self.permutations > 0:
            retval = False
            raise "Can not set Dataflow %s to iteration %d for it only has %d" %\
                (self.__class__, iter, self.permutations)

        if iter == 0:
            self.iter_count = 0
            return True

        while self.iter_count != iter:
            self.step()
#            self.set_iter_count(iter)
        retval = True
#        self.iter_count = iter
#        for stage in self._stages:
#            stage.set_iter_count(iter)
        return retval

    def calculate_permutations(self):
        my_perms = []
        permutations = 1
        for stage in self._stages:
            my_perms.append(stage.permutations)
        for perm in my_perms:
            permutations *= perm
        return permutations
            
    def get_stagecount(self):
        return len(self._stages)

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

    def get_parent(self):
        """
            Return a reference to my parent.
        """
        return self._parent

    def bind_transport(self, transport, *args):
        """
            Associate a transport with the instance of the Dataflow object.
        """
        #Instantiation of the transport doesnt *actually* happen here, just
        #gets stored as classobj. It happens in self.execute(), so its closer to runtime
        self._transport_co = transport
        self._transport_args = args
        
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
        data.

        """
        bytes = []
        for stage in self._stages:
            if stage.__class__ is Dataflow:
                bytes.extend(stage.get_bytes()) #this looks right, but seems like
                                                #should be an append
            else:
                bytes.append(stage.get_bytes())
        return "".join(bytes)

    def _set_start_time(self):
        self._start_time=time.time()
        for stage in self._stages:
            if issubclass(stage.__class__, Dataflow):
                stage._start_time = time.time()

    def _prepare_transport(self):
        """
            This method is simply a helper function to organize the process
        of setting up the Transport for use by the Dataflow its bound to.
        """
        setattr(self._transport_co, "_parent",self)
        if len(self._transport_args) == 0:
    #       Now we must check the configuration for this Dataflow and see if there
    #       are any sections in it that match the Transport we are currently dealing
    #       with. If so, then we set those values inside the class object so that 
    #       the Transport can make use of them as early as his __init__()
            transport_name = self._transport_co.__name__.upper()
            if self.PEC.config.has_section(transport_name):
                #proceed getting and settng values
                for option in self.PEC.config.options(transport_name):
                    value = self.PEC.config.get(transport_name, option)
                    if hasattr(self._transport_co, option): #set the attribute
                        print "%s already has attribute %s ...skipping." % \
                            (transport_name, option)
                    else:
                        setattr(self._transport_co, option, value)
            else:
                raise "Transport Configuration Error. Section %s not found in Proteus self.config." % \
                    transport_name
        else: #the Dataflow developer specified Transport args, so use them
            pass

#       OK now that everything has been set in the class instance its safe to
#       instantiate!
        self._transport = self._transport_co(*self._transport_args)
        self.send = self._transport.send
        self.recv = self._transport.recv
        self.reset = self._transport.reset

    def execute(self):
        """
            This method begins everything. This method should only get called
        on the "root" or "MASTER" dataflow.

        """
        self._set_start_time()
        self._prepare_transport()

class ProteusEnvConf:
    """
        This class is simply a storage location for all Proteus configuration
    information and environmental information that might be needed during
    execution. It gets instantiated and used inside of the master Dataflow, but
    exists outside the Dataflow class definition simply for code cleanliness
    reasons.

    """
    def __init__(self):
        self.user = os.getenv("USER") # The user running proteus
        self.os_type = os.name # The OS name: 'posix', 'nt', 'os2', 'mac',
                                    # 'ce' or 'riscos'
        self.pwd = os.curdir #current working directory
        self.environ = os.environ # a dictionary of the process
                                        # environment
        self.sep = os.sep # The path separator for this filesystem
        self.linesep = os.linesep # The line separator for this filesystem
        self.extsep = os.extsep #The extension separator for this FS 
        
        self.config_file = self.check_config() #the check must preceed
                                                # get_config()
        self.config = self.get_config() # The Config object from the config file
        self.output_dir = self.config.get("GENERAL", "output_dir")

    def get_config(self):
        """
            Read the Proteus Config file and return the config object
        """
        self.config = CP.ConfigParser()
        if self.config_file is False:
            raise "Could not fine a suitable config file!!!"

        self.config.read(self.config_file)
        return self.config
 
    def check_config(self):
        """
            Check if a config file exists in:
                /etc/proteus.conf
                ./proteus.conf
            The filename of the first config that exists is returned or else
        'False' is returned.

        """
        # These configuration locations need to be passed in at some point
        # potentially from a configuration file.
        conf_locations = ['/etc/proteus.conf', './proteus.conf']
        for potential_place in conf_locations:
            if os.path.exists(potential_place):
                return potential_place
        return False


class BrowserThread(Thread):
    """
        This is strictly an internally used class because the module "threading"
    requires threads to be defined as classes with a .run() method. i
    So to make it generically usable
    I smash pass in a function reference and an argument reference.
    and that function reference gets called with the arguement in the heart
    of the thread.
    """
    def __init__(self, func, arg):
        Thread.__init__(self)
        self.setDaemon(False)
        self.func = func
        self.arg = arg

    def run(self):
        self.func(self.arg)
         
class ProteusDisplay:
    """
        A class to contain all the display methods for Proteus Dataflows.
        
        This stuff all resides in a class outside of the Dataflow class definition
    simply for code cleanliness.

    """
    def show_gui_posix(self, start_obj):
        """
            Fork a thread to run the GUI Dataflow Browser in.
        """
        import os
        pid = os.fork()
        if pid:
            pass #parent does nothing
        else: #child spawns gtk window
            self._print_tree_gtk(start_obj)
        del(os)

    def show_gui_nt(self, start_obj):
        """
            Fire off a proper thread that the GUI Dataflow Browser will run in.

        Note:
            Currently buggy, GTK and threading arent compatible you will
            have to manually kill python on exit.

        """
        browser = BrowserThread(self._print_tree_gtk, start_obj)
        browser.setDaemon(False)
        browser.start()

    def _print_tree_gtk(self, start_obj):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.main_quit)
        window.connect("destroy", gtk.main_quit)
        window.set_title("Dataflow Viewer :  '%s'" % (start_obj._name))
        window.set_size_request(500, 500)
        # create a TreeStore with one string column to use as the model
        treestore = gtk.TreeStore(str)

        #we assume we are at the top level Dataflow
        p_iter = treestore.append(None, ["%s with %d bytes and %d permutations.\n%.28s...'" % (start_obj.__class__.__name__, len(start_obj), start_obj.permutations, repr(start_obj.get_bytes()))])
        if issubclass(start_obj.__class__, Dataflow):
            self._print_tree_gtk_helper(start_obj, p_iter, treestore)
        else:
            raise "You must provide a top level Dataflow object."

        # create the TreeView using treestore
        treeview = gtk.TreeView(treestore)
        # create the TreeViewColumn to display the data
        tvcolumn = gtk.TreeViewColumn()
        # add tvcolumn to treeview
        treeview.append_column(tvcolumn)
        # create a CellRendererText to render the data
        cell = gtk.CellRendererText()
        # add the cell to the tvcolumn and allow it to expand
        tvcolumn.pack_start(cell, True)
        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        tvcolumn.add_attribute(cell, 'text', 0)
        # make it searchable
        treeview.set_search_column(0)
        # DISAllow sorting on the column
        tvcolumn.set_sort_column_id(1) 
        # DISAllow drag and drop reordering of rows
        treeview.set_reorderable(False)

        #Make headers unclickable, and gone entirely.
        treeview.set_headers_clickable(False)
        treeview.set_headers_visible(False)

        #display window
        window.add(treeview)
        window.show_all()
        gtk.main()

    def _print_tree_gtk_helper(self, start_obj, p_iter, treestore):
            for stage in start_obj._stages:
                if issubclass(stage.__class__, Dataflow):
                    #recurse
                    c_iter = treestore.append(p_iter, ["%s with %d bytes and %d permutations.\n%.28s...'" % (stage.__class__.__name__, len(stage), stage.permutations, repr(stage.get_bytes()))])
                    self._print_tree_gtk_helper(stage, c_iter, treestore)
                elif issubclass(stage.__class__, Bruter):
                    treestore.append(p_iter, ["%s with %d permutations\n%s ...'" % (stage.__class__.__name__, len(stage._data), repr(stage._data[:3]))]) #only first three
                else:
                    treestore.append(p_iter, ["%s with %d bytes\n%.28s ...'" % (stage.__class__.__name__, len(stage), repr(stage.get_bytes()))])   


    def _print_tree(self, start_obj, padding):
        print  "%s+-Dataflow (%d permutations): '%.28s ...'" % (padding[:-1], start_obj.permutations, repr(start_obj.get_bytes()))
#        print padding[:-1] + "+-" + "Dataflow" + " (" + repr(start_obj.permutations) + " permutations)" + ":" + repr(start_obj.get_bytes())
        padding += ' ' # add a space
        count = 0
        if issubclass(start_obj.__class__, Dataflow): 
        #if start_obj.__class__ is Dataflow:
            for stage in start_obj._stages:
                count += 1
                print padding + "|"
                if issubclass(stage.__class__, Dataflow):
                #if stage.__class__ is Dataflow:
                    if count==len(stage._stages):
                        self._print_tree(stage, padding)
                    else:
                        self._print_tree(stage, padding + "|")
                elif issubclass(stage.__class__, Bruter):
#                    print  "%s+-Bruter (%d permutations) (%d peers to the
#                    right) (%d right peer permutations) %d" % (padding,
#                    stage.permutations, stage.get_rightpeer_count(),
#                    stage.get_rightpeer_perms(), stage.step_index)

                     print  "%s+-Bruter (%d/%d permutations): '%.28s ...'" % (padding, stage.step_index+1, stage.permutations, repr(stage.get_bytes()))
#                    print  "%s+-Bruter (%d permutations) on element: %d" %
#                    (padding, stage.permutations, stage.step_index)
                elif issubclass(stage.__class__, BasePDT):
                    print  "%s+-PDT: '%.28s ...'" % (padding, repr(stage.get_bytes()))
        else:
            raise "You must provide a top level Dataflow object."
