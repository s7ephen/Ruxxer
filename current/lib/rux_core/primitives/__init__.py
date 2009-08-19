#eventually these will all be broken out into individual files when I figure otu
#how to tweak __import__ and __init__.py to work properly
from random import Random

class Primitive:
    """ 


    """
    # For those extending from this class, all helper functions should be prepended with "__h_"
    # for "helper"
    def __init__(self):
        self._data = [] 
        self.permutations = 1 
        self._parent = None 
        self.step_index = 0
        self.endian = "NA" 

    def __len__(self):
        """
           
        """
        return len(self._data[self.step_index])

    def get_bytes(self):
        """
            
        """
        return self._data[self.step_index]

    def step(self):
        """
            
        """
        pass

    def set_iter_count(self, iter):
        """

        """
        pass

    def get_parent(self):
        """
            
        """
        return self._parent

    def push(self, data):
        """
            
        """
        self._data.append(data)

    def pack(self, pack_char, data):
        """
            
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
             
        """
        if self.endian=="BE":
            pack_char = ">"+pack_char
        if self.endian == "LE":
            pack_char = "<"+pack_char
        if self.endian == "NA": #use native
            pack_char = "="+pack_char
        
        return(struct.unpack(pack_char, data))
    
class UnsignedByte(Primitive):
    """
        A Unsigned Byte. 

    Width: 8 bits, 1byte
    Range: 0 to 255
    Defaults to 0x99 if not specified. 
    """
    def __init__(self, data=0x99, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('B', data))

class String(Primitive):
    """
        A string datatype. Defaults to 'str1' if not specified.
    """
    def __init__(self, data='str1'):
        Primitive.__init__(self)
        self.push(data)
        
class SignedByte(Primitive):
    """
        A Signed Byte. 
    
    Width: 8 bits, 1 byte
    Range: -128 to 127
    Defaults to 0x01 if not specified. 
    """
    def __init__(self, data=0x01, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('b', data))

Byte = UnsignedByte
UByte = UnsignedByte

class UnsignedShort(Primitive):
    """
        Unsigned Short. 

    Width: 16 bites, 2 bytes 
    Range: 0 to 65,535
    Defaults to 0x9999 if not specified. 
    """
    def __init__(self, data=0x9999, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('H', data))

UShort = UnsignedShort

class SignedShort(Primitive):
    """
        Signed Short 

    Width: 16 bites, 2 bytes
    Range: -32,768 to 32,767
    Defaults to 0x0001 if not specified. 
    """
    def __init__(self, data=0x0001, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('h', data))

Short = SignedShort

class UnsignedLong(Primitive):
    """
        Unsigned Long Integer. 
    
    Width: 32 bits, 4 bytes 
    Range:
    Defaults to 0x99999999 if not specified.
    """
    def __init__(self, data=0x99999999, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('L', data))

ULong = UnsignedLong

class SignedLong(Primitive):
    """
        Signed Long Integer. 

    Width: 32 bits, 4 bytes 
    Range:
    Defaults to 0x00000001 if not specified.
    """
    def __init__(self, data=0x00000001, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('l', data))

Long = SignedLong

class UnsignedDouble(Primitive):
    """
        Unsigned Long Long Integer. 
  
    Width: 64 bits, 8 bytes
    Range:
    Defaults to 0x9999999999999999 if not specified.
    """
    def __init__(self, data=0x9999999999999999, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('Q', data))

UDouble = UnsignedDouble

class SignedDouble(Primitive):
    """
        Signed Long Long Integer. 

    Width: 64 bits, 8 bytes
    Range:
    Defaults to 0x0000000000000001 if not specified.
    """
    def __init__(self, data=0x0000000000000001, endian="NA"):
        Primitive.__init__(self)
        self.endian = endian
        self.push(self.pack('q', data))

Double = SignedDouble

class EmailAddress(Primitive):
    """

    """
    def __init__(self, lName='email', hName='domain', dName='tld'):
        BasePD.__init__(self)
        self.localName = StringPDT(lName)
        self.hostName = StringPDT(hName)
        self.domainName = StringPDT(dName)
        self.push(lName + '@' + hName + '.' + dName)
    
    def __h_setusername(self):
        pass
    def __h_setdomain(self):
        pass
    def __h_settld(self):
        pass

class FileReader(Primitive):
    """

    """
    def __init__(self, filename):
        Primitive.__init__(self)
        try:
            #statinfo = os.stat(filename)
            # Note: not able to parse absolute paths on Windows
            # Because the : in the path messes it up
            tmp_h = os.open(filename, 0777)
            data = tmp_h.read()
        except OSError, e:
            raise "Unable to read file: ", filename
        os.close(tmp_h)
        self.push(data)
        #del(os)
        
class RandomPrimitive(Random, Primitive):
    """

    """
    def __init__(self):
        Primitive.__init__(self)
        Random.__init__(self, "sa7ori")
        
class RandByte(RandomPrimitive):
    """

    """
    def __init__(self, endian="NA"):
        RandomPrimitive.__init__(self)
        self.endian = endian
        self.push(self.pack('B', self.randint(0, 0xff)))

class RandShort(RandomPrimitive):
    """

    """
    def __init__(self, endian="NA"):
        RandomPrimitive.__init__(self)
        self.endian = endian
        self.push(self.pack('H', self.randint(0, 0xffff)))

class RandLong(RandomPrimitive):
    """
    """
    def __init__(self, endian="NA"):
        RandomPrimitive.__init__(self)
        self.endian = endian
        self.push(self.pack('L', self.randint(0, 0xffffffff)))

class RandDouble(RandomPrimitive):
    """

    """
    def __init__(self, endian="NA"):
        RandomPrimitive.__init__(self)
        self.endian = endian
        tmpDouble = self.getrandbits(20)
        self.push(self.pack('Q', tmpDouble))
        
class GarbageASCIIBytes(RandomPrimitive):
    """
    """        
    def __init__(self, length):
        RandomPrimitive.__init__(self)
        count = 1
        retstr = ""
        if length <= 0:
            raise "Length argument must be greater than zero."
        while count <= length:
            retstr += self.pack('B', self.randint(0x21, 0x7e))
            count+=1
        self.push(retstr)

class GarbageBytes(RandomPrimitive):
    """
    
    """
    def __init__(self, length):
        RandomPrimitive.__init__(self)
        count = 1
        retstr = ""
        if length <= 0:
            raise "Length argument must be greater than zero."
        while count <= length:
            retstr += self.pack('B', self.randint(0, 0xff))
            count+=1
        self.push(retstr)

class ByteLen(Byte):
    """

    """
    def __init__(self, pdt):
        Byte.__init__(self, len(pdt))

class ShortLen(Short):
    """

    """
    def __init__(self, pdt):
        Short.__init__(self, len(pdt))

class LongLen(Long):
    """

    """
    def __init__(self, pdt):
        Long.__init__(self, len(pdt))

class DoubleLen(Double):
    """

    """
    def __init__(self, pdt):
        Double.__init__(self, len(pdt))

class RepeaterString(String):
    """

    """
    def __init__(self, data="TEST", count=5):
        String.__init__(self, data*count)

class URLEncodedData(String):
    """

    """
    def __init__(self, data="CHEESE"):
        data = urllib.quote(data) 
        String.__init__(self, data)

class ZlibData(String):
    """

    """
    def __init__(self, data="CHEESE"):
        data = data.encode('zlib') 
        String.__init__(self, data)

class Base64Data(String):
    """

    """
    def __init__(self, data="CHEESE"):
        data = data.encode('base64') 
        String.__init__(self, data)
