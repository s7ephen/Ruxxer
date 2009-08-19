#!/usr/bin/python
#
#


# I saw these in some other protocol thing.. im assuming they're required 
from lib.transports import *
from lib.bruters import *

global MASTER_DATAFLOW


SPIPE_VERSION1 = int(0x10000001)
SPIPE_VERSION2 = int(0x20000001)
SPIPE_VERSION3 = int(0x30000001)
SPIPE_VERSION4 = int(0x40000001)

KEY_PACKAGE_TYPE = int(1)
DATA_PACKAGE_TYPE = int(2)

class spipeHeader(): 
	"SPIPE Header class"

	
	def __init__(self):
		self.header = ""

		# Every SPIPE header begins with 'PO' 
		self.headerID = StringPDT("PO")
		
		# version
		self.version = int(0)
		
		# offset to datablock
		self.offsetDataBlock = int(0)
		
		# data count
		self.dataCount = int(0) 

		# data block length
		self.dataBlockLength = int(0)
	
		# sender GUID (guranteed uniq ID)
		self.guidLength = int(0)

		# package type 
		self.packageType = int(0)

		# computer name
		self.computerName = ""

	def buildHeader():
		self.header	+= self.headerID
		self.header += self.version
		self.header += self.offsetDataBlock
		self.header += self.dataCount
		self.header += int(0)
		self.header += self.dataBlockLength
		self.header += self.guid
		self.header += self.packageType
		self.header += self.computerName



#
