from lib.rux1_0 import *
import socket
import random

#DEVEL NOTES:
#
# two methods of attempting to implement this:
#   1.  Bruter has a list of PDT  objects and no counter is used.
#       The top level Datasource then walks the entire tree, flattening it
#       effectively building a huges list of all the possible PDT permutations
#       
#   2.  Bruter has a list of PDT objects, but a "next" method and counter are 
#       used to keep track of state. In this way, all PDT combinations dont
#       have to be pregenerated
"""
        Bruters are just "multidimensional" PDT's. They don't remain
    the same value. Instead they take a PDT as input and munge it a certain
    way. An internal array is generated for each possible munged value of 
    the original PDT.
"""

class FormatStringAttack(Bruter, StringPDT):
    """
        FormatStringAttack

        Example Usage:
            FormatStringAttack(<StringPDT>)

        This Bruter takes a string. It will inject various format
        string vectors into the supplied string, as well as return
        format string combinations by themselves.

        ex) FormatStringAttack(StringPDT("TEST"))

        returns:
            "TEST"
            "%s"
            "%sTEST"
            "TE%sST"
            "TEST%s"
            "%x"
            ... etc.
    """

    def __init__(self, objInstance):
        if not issubclass(objInstance.__class__, StringPDT):
            raise "FormatStringAttack requires a StringPDT arg."
        StringPDT.__init__(self, objInstance.get_bytes())
        Bruter.__init__(self)
        self.orig = objInstance.get_bytes()
        self.expand()

    def expand(self):
        self._add_permutation(self.orig)
        formatString = ['%s', '%x', '%n', '%d', '%u']

        for x in formatString:
            self._add_permutation(x)
            self._add_permutation(x + x)
            self._add_permutation(x + self.orig)
            self._add_permutation(self.orig[0:(len(self.orig)/2)]+x+self.orig[(len(self.orig)/2):])
            self._add_permutation(self.orig + x)

class SpecialFilesAttack(Bruter):
    """
        SpecialFilesAttack

        Example Usage:
            SpecialFilesAttack()

        This Bruter returns various Windows special file names. 

        returns:
            "COM1-9"
            "LPT1-9"
            "CON"
            "AUX"
            ... etc.
    """

    def __init__(self):
        Bruter.__init__(self)
        self.expand()

    def expand(self):
        specialFiles = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
                        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
                        'CON', 'COIN$', 'COPOUT$', 'PRN', 'AUX', 'CLOCK$', 'NUL', 'NULL',
                        'COM1.txt', 'LPT1.txt']

        for x in specialFiles:
            self._add_permutation(x)

class DirectoryTraversalAttack(Bruter, StringPDT):
    """
        DirectoryTraversalAttack

        Example Usage:
            DirectoryTraversalAttack(<filename>)

        This Bruter returns permutations that attempt to walk back up a file-system
        directory tree and access a given file at each level. Note: A filename (\cmd.exe)
        or partial path (\Windows\System32\cmd.exe) can be supplied.

        Note: The dataflow output displays double backslashes (ex. ..\\..\\file.ext) however
        the delivered data only has one backslash per directory level (ex. ..\..\file.ext). 

        returns:
            "..<path>"
            "..\..<path>"
            "..\..\..<path>"
            ... etc.
    """

    def __init__(self, objInstance):
        if not issubclass(objInstance.__class__, StringPDT):
            raise "CompletelyCorruptString requires a StringPDT arg."
        StringPDT.__init__(self, objInstance.get_bytes())
        self.orig_str = objInstance.get_bytes()
        Bruter.__init__(self)
        self.expand()

    def expand(self):
        dirStr = "..\\"
        tmpStr = ""

        for x in range(10):
            tmpStr = ''
            for y in range(x):
                tmpStr = tmpStr + dirStr
            tmpStr = tmpStr + self.orig_str
            self._add_permutation(tmpStr)
            
class CompletelyCorruptString(Bruter, StringPDT):
    """
        Completely Corrupt String Bruter

        Example Usage:
            CompletelyCorruptString(<StringPDTtoBrute>, <count>)

        This Bruter takes a string and a count as arguments. It will
        completely corrupt the bytes of the string "count" times with
        random bytes. 


            CompletelyCorruptString(StringPDT("TEST"), 3)

        would give:
          First Iteration: "TEST" <--- untouched.
          Second Iteration: "\\x89\\x44\\x32\\x01"
          Third Iteration: "\\x45\\x12\\x07\\x34"

    """
    def __init__(self, objInstance, corrupt_count=3):
        if not issubclass(objInstance.__class__, StringPDT):
            raise "CompletelyCorruptString requires a StringPDT arg."
        StringPDT.__init__(self, objInstance.get_bytes())
        Bruter.__init__(self)
        self.orig_str = objInstance.get_bytes()
        self._add_permutation(self.orig_str)
        self.corrupt_count = corrupt_count
        self.expand()

    def expand(self):
        i = 1
        while i <= self.corrupt_count:
            self._add_permutation(GarbageBytesPDT(len(self.orig_str)).get_bytes())
            i+=1    

class CompletelyASCIICorruptString(Bruter, StringPDT):
    """
        Completely ASCII Corrupt String Bruter

        Example Usage:
            CompletelyASCIICorruptString(<StringPDTtoBrute>, <count>)

        This Bruter takes a string and a count as arguments. It will
        completely corrupt the bytes of the string "count" times with
        ASCII characters. 


            CompletelyASCIICorruptString(StringPDT("TEST"), 3)

        would give:
          First Iteration: "TEST" <--- untouched.
          Second Iteration: "A*x!"
          Third Iteration: "9_!4"

    """
    def __init__(self, objInstance, corrupt_count=3):
        if objInstance.__class__ is not StringPDT:
            raise "CompletelyASCIICorruptString requires a StringPDT arg."
        StringPDT.__init__(self, objInstance.get_bytes())
        Bruter.__init__(self)
        self.orig_str = objInstance.get_bytes()
        self._add_permutation(self.orig_str)
        self.corrupt_count = corrupt_count
        self.expand()

    def expand(self):
        i = 1
        while i <= self.corrupt_count:
            self._add_permutation(GarbageASCIIBytesPDT(len(self.orig_str)).get_bytes())
            i+=1    

class SlightlyCorruptString(Bruter, StringPDT):
    """
        Slightly Corrupted String Bruter

        Example Usage:
            SlightlyCorruptString(<StringPDTtoBrute>, <len to generate>)

        This Bruter takes a string and a length argument. It generates
        a string of random bytes of the length of the length argument.
        it will then walk through the string byte by byte overwriting
        with substring each time. For example:

            SlightlyCorruptString(StringPDT("Hello World"), 3)

        would give:
          First Iteration: "Hello World" <--- Untouched.
          Second Iteration: "\\x89\\x77\\x05lo World"
          Third Iteration: "H\\x89\\x77\\x05o World"
          Seventh Iteration: "Hello \\x89\\x77\\x05ld"

    """
    def __init__(self, objInstance, length=3):
        if not issubclass(objInstance.__class__, StringPDT):
            raise "SlightlyCorruptString requires a StringPDT arg."
        StringPDT.__init__(self, objInstance.get_bytes())
        Bruter.__init__(self)
        self.orig_str = objInstance.get_bytes()
        self._add_permutation(self.orig_str)
        self.length = length
        self.gbpdt = GarbageBytesPDT(self.length)
        self.corruptor = self.gbpdt.get_bytes() #the actual string
        self.expand()

    def expand(self):
        import copy
        target = self.orig_str
        substr = self.corruptor
        target_list = []
        target_list = list(target)
        i = 0
        while i <= len(target)-len(substr):
            newstr = ""
            tmp = copy.copy(target_list)
            tmp[i:i+len(substr)] = list(substr)
            new_str = "".join(tmp)
            self._add_permutation(new_str)
            i+=1

class SlightlyASCIICorruptString(Bruter, StringPDT):
    """
        Slightly ASCII Corrupt String Bruter

        Example Usage:
            SlightlyASCIICorruptString(<StringPDTtoBrute>, <len to generate>)

        This Bruter takes a string and a length argument. It generates
        a string of ASCII characters of the length of the length argument.
        it will then walk through the string byte by byte overwriting
        with substring each time. For example:

            SlightlyASCIICorruptString(StringPDT("Hello World"), 3)

        would give:
          First Iteration: "Hello World" <--- Untouched.
          Second Iteration: "AAAlo World"
          Third Iteration: "HAAAo World"
          Seventh Iteration: "Hello AAAld"

    """
    def __init__(self, objInstance, length=3):
        if objInstance.__class__ is not StringPDT:
            raise "SlightlyCorruptString requires a StringPDT arg."
        StringPDT.__init__(self, objInstance.get_bytes())
        Bruter.__init__(self)
        self.orig_str = objInstance.get_bytes()
        self._add_permutation(self.orig_str)
        self.length = length
        self.gbpdt = GarbageASCIIBytesPDT(length)
        self.corruptor = self.gbpdt.get_bytes() #the actual string
        self.expand()

    def expand(self):
        import copy
        target = self.orig_str
        substr = self.corruptor
        target_list = []
        target_list = list(target)
        i = 0
        while i <= len(target)-len(substr):
            newstr = ""
            tmp = copy.copy(target_list)
            tmp[i:i+len(substr)] = list(substr)
            new_str = "".join(tmp)
            self._add_permutation(new_str)
            i+=1

class StringSwapCaseBruter(Bruter, StringPDT):
    """
        String Swap Case

        Example Usage:
            StringSwapCaseBruter(<StringPDTtoBrute>)

        This Bruter takes a string pdt argument. It will return two permutations
        the first of which is the original string untouched. The second
        is the string with the cases swapped. For example:

            StringSwapCase(StringPDT("Hello World"))

        would give:
          First Iteration: "Hello World" <--- Untouched.
          Second Iteration: "hELLO wORLD"

    """
    def __init__(self, objInstance):
        if objInstance.__class__ is not StringPDT:
            raise "StringSwapCaseBruter must accept only StringPDT's"
        StringPDT.__init__(self, objInstance.get_bytes())
        Bruter.__init__(self)
        self.orig_str = objInstance.get_bytes()
        self.expand()

    def expand(self):
        tmpstr = self.orig_str
        self._add_permutation(tmpstr)
        self._add_permutation(tmpstr.swapcase())

         
class HttpVersionBruter(Bruter, StringPDT):
    """
        HttpVersionBruter

        Example Usage:
            HttpVersionBruter(<StringPDT("1.0")>)

        This Bruter takes a starting HTTP Version String PDT
        and returns valid HTTP versions for use in HTTP client/server
        requests/responses.

        returns:
            "HTTP/0.9"
            "HTTP/1.0"
            "HTTP/1.1"
    """
    
    def __init__(self, objInstance):
        if objInstance.__class__ is not StringPDT:
            raise "HttpVersionBruter must accept only StringPDT's"
        StringPDT.__init__(self, objInstance.get_bytes())
        Bruter.__init__(self)
        self.expand()

    def expand(self):
        self._add_permutation("HTTP/0.9")
        self._add_permutation("HTTP/1.0")
        self._add_permutation("HTTP/1.1")

class ByteBruter(Bruter, BytePDT, RandomPDT):
    """
        Byte Bruter
        
    """
    def __init__(self, objInstance):
        if objInstance.__class__ is not BytePDT:
            raise "ByteBruter must accept only BytePDT's"
        BytePDT.__init__(self, int(ord(objInstance.get_bytes())))
        Bruter.__init__(self)
        RandomPDT.__init__(self)
        self.expand()

    def expand(self):
        """
            This method will munge a byte and return a random byte between 0-255.
        """
        self._add_permutation(struct.pack('B', self.randint(0, 0xff)))

class ShortBruter(Bruter, ShortPDT, RandomPDT):
    """
        Short Bruter

    """
    def __init__(self, objInstance):
        if objInstance.__class__ is not ShortPDT:
            raise "ShortBruter must accept only ShortPDT's"
        unpackedTuple = struct.unpack('H', objInstance.get_bytes())        
        ShortPDT.__init__(self, unpackedTuple[0])
        Bruter.__init__(self)
        RandomPDT.__init__(self)
        self.expand()

    def expand(self):
        self._add_permutation(struct.pack('H', self.randint(0, 0xffff)))

class LongBruter(Bruter, LongPDT, RandomPDT):
    """
        Long Bruter

    """
    def __init__(self, objInstance):
        if objInstance.__class__ is not LongPDT:
            raise "LongBruter must accept only LongPDT's"
        unpackedTuple = struct.unpack('>l', objInstance.get_bytes())
        LongPDT.__init__(self, unpackedTuple[0])
        Bruter.__init__(self)
        RandomPDT.__init__(self)
        self.expand()

    def expand(self):
        """
            This method will munge a long and return a random long between 0-2147483647.
        """
        self._add_permutation(struct.pack('L', self.randint(0, 0xffffffff)))

class DoubleBruter(Bruter, LongPDT, RandomPDT):
    """
        Double Bruter

    """
    def __init__(self, objInstance):
        if objInstance.__class__ is not DoublePDT:
            raise "DoubleBruter must accept only DoublePDT's"
        unpackedTuple = struct.unpack('Q', objInstance.get_bytes())
        LongPDT.__init__(self, unpackedTuple[0])
        Bruter.__init__(self)
        self.expand()

    def expand(self):
        """
            This method will munge a long and return a random long between 0-2147483647.
        """
        tmpDouble = self.getrandbits(20)
        self.push(self.pack('Q', tmpDouble))

class ByteLenOffByOneBruter(Bruter, ByteLenPDT):
    """
        Byte Length Off-By-One Bruter

    """
    def __init__(self, pdt):
        if pdt.__class__ is not ByteLenPDT:
            raise "ByteLenOffByOneBrute must accept only ByteLenPDT's"
        ByteLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt)

    def expand(self, pdt):
        self._add_permutation(struct.pack('=b', len(pdt)))
        self._add_permutation(struct.pack('=b', (len(pdt)+1)))
        self._add_permutation(struct.pack('=b', (len(pdt)-1)))

class ShortLenOffByOneBruter(Bruter, ShortLenPDT):
    """
        Short Length Off-By-One Bruter

    """
    def __init__(self, pdt):
        if pdt.__class__ is not ShortLenPDT:
            raise "ShortLenOffByOneBrute must accept only ShortLenPDT's"
        ShortLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt)

    def expand(self, pdt):
        self._add_permutation(struct.pack('=h', len(pdt)))
        self._add_permutation(struct.pack('=h', (len(pdt)+1)))
        self._add_permutation(struct.pack('=h', (len(pdt)-1)))

class LongLenOffByOneBruter(Bruter, LongLenPDT):
    """
        Long Length Off-By-One Bruter

    """
    def __init__(self, pdt):
        if pdt.__class__ is not LongLenPDT:
            raise "LongLenOffByOneBrute must accept only LongLenPDT's"
        LongLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt)

    def expand(self, pdt):
        self._add_permutation(struct.pack('=l', len(pdt)))
        self._add_permutation(struct.pack('=l', (len(pdt)+1)))
        self._add_permutation(struct.pack('=l', (len(pdt)-1)))

class DoubleLenOffByOneBruter(Bruter, DoubleLenPDT):
    """
        Double Length Off-By-One Bruter

    """
    def __init__(self, pdt):
        if pdt.__class__ is not DoubleLenPDT:
            raise "DoubleLenOffByOneBrute must accept only DoubleLenPDT's"
        DoubleLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt)

    def expand(self, pdt):
        self._add_permutation(struct.pack('=q', len(pdt)))
        self._add_permutation(struct.pack('=q', (len(pdt)+1)))
        self._add_permutation(struct.pack('=q', (len(pdt)-1)))

class ByteLenOffByNBruter(Bruter, ByteLenPDT):
    """
        Byte Length Off-By-N Bruter

    """
    def __init__(self, pdt, count=3):
        if pdt.__class__ is not ByteLenPDT:
            raise "ByteLenOffByNBruter must accept only ByteLenPDT's"
        ByteLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt, count)

    def expand(self, pdt, count):
        self._add_permutation(struct.pack('=b', len(pdt)))
        for x in range(1, count):
            self._add_permutation(struct.pack('=b', (len(pdt)+x)))
            self._add_permutation(struct.pack('=b', (len(pdt)-x)))

class ShortLenOffByNBruter(Bruter, ShortLenPDT):
    """
        Short Length Off-By-N Bruter

    """
    def __init__(self, pdt, count=3):
        if pdt.__class__ is not ShortLenPDT:
            raise "ShortLenOffByNBruter must accept only ShortLenPDT's"
        ShortLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt, count)

    def expand(self, pdt, count):
        self._add_permutation(struct.pack('=h', len(pdt)))
        for x in range(1, count):
            self._add_permutation(struct.pack('=h', (len(pdt)+x)))
            self._add_permutation(struct.pack('=h', (len(pdt)-x)))

class LongLenOffByNBruter(Bruter, LongLenPDT):
    """
        Long Length Off-By-N Bruter

    """
    def __init__(self, pdt, count=3):
        if pdt.__class__ is not LongLenPDT:
            raise "LongLenOffByNBrute must accept only LongLenPDT's"
        LongLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt, count)

    def expand(self, pdt, count):
        self._add_permutation(struct.pack('=l', len(pdt)))
        for x in range(1, count):
            self._add_permutation(struct.pack('=l', (len(pdt)+x)))
            self._add_permutation(struct.pack('=l', (len(pdt)-x)))

class DoubleLenOffByNBruter(Bruter, DoubleLenPDT):
    """
        Double Length Off-By-N Bruter

    """
    def __init__(self, pdt, count=3):
        if pdt.__class__ is not DoubleLenPDT:
            raise "DoubleLenOffByNBruter must accept only DoubleLenPDT's"
        DoubleLenPDT.__init__(self, pdt)
        Bruter.__init__(self)
        self.expand(pdt, count)

    def expand(self, pdt, count):
        self._add_permutation(struct.pack('=q', len(pdt)))
        for x in range(1, count):
            self._add_permutation(struct.pack('=q', (len(pdt)+x)))
            self._add_permutation(struct.pack('=q', (len(pdt)-x)))

