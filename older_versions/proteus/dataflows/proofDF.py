"""
        A SKELETAL example of the bare minumum contents of a dataflow.
"""
from lib.protocols.basic_tcpserver import *
from lib.transports import *
from lib.bruters import *

global MASTER_DATAFLOW

proofDF = Dataflow("ProofDataflow")

# PDTs
proofDF.add_stage(UnsignedBytePDT(0x10))
proofDF.add_stage(SignedBytePDT(0x11))
proofDF.add_stage(UnsignedShortPDT(0x1000))
proofDF.add_stage(SignedShortPDT(0x1100))
proofDF.add_stage(UnsignedLongPDT(0x10000000))
proofDF.add_stage(SignedLongPDT(0x11000000))
proofDF.add_stage(UnsignedDoublePDT(0x1000000000000000))
proofDF.add_stage(SignedDoublePDT(0x1100000000000000))

# Randoms
proofDF.add_stage(RandBytePDT())
proofDF.add_stage(RandShortPDT())
proofDF.add_stage(RandLongPDT())
proofDF.add_stage(RandDoublePDT())

# File
#fileStr = proofDF.add_stage(FileReaderPDT("TODO.txt"))
#print fileStr

# Garbage
proofDF.add_stage(GarbageBytesPDT(4))
proofDF.add_stage(GarbageASCIIBytesPDT(4))

# String
proofDF.add_stage(StringPDT("test"))
proofDF.add_stage(EmailPDT("qa","mcafee","com"))
proofDF.add_stage(RepeaterStringPDT("A", 10))

# Encoded
proofDF.add_stage(ZlibDataPDT("encodeMe"))
proofDF.add_stage(Base64DataPDT("encodeMe"))
proofDF.add_stage(URLEncodedDataPDT("encode=Me"))

# Length Calculators
proofDF.add_stage(ByteLenPDT(UnsignedBytePDT(0x10)))
proofDF.add_stage(ShortLenPDT(UnsignedShortPDT(0x1000)))
proofDF.add_stage(LongLenPDT(UnsignedLongPDT(0x10000000)))
proofDF.add_stage(DoubleLenPDT(UnsignedDoublePDT(0x1000000000000000)))

# Bruters
#proofDF.add_stage(FormatStringAttack(StringPDT("FORMATSTRINGATTACK")))
#proofDF.add_stage(SpecialFilesAttack())
#proofDF.add_stage(DirectoryTraversalAttack(StringPDT("index.htm")))
#proofDF.add_stage(CompletelyCorruptString(StringPDT("corruptMe"), 10))
#proofDF.add_stage(CompletelyASCIICorruptString(StringPDT("corruptMe"), 10))
#proofDF.add_stage(SlightlyCorruptString(StringPDT("corruptMe"), 3))
#proofDF.add_stage(SlightlyASCIICorruptString(StringPDT("corruptMe"), 3))
#proofDF.add_stage(StringSwapCaseBruter(StringPDT("sWapCase")))
#proofDF.add_stage(HttpVersionBruter(StringPDT("HTTP/1.0")))
#proofDF.add_stage(ByteBruter(BytePDT(0x10)))
#proofDF.add_stage(ShortBruter(ShortPDT(0x1000)))
#proofDF.add_stage(LongBruter(LongPDT(0x10000000)))
#proofDF.add_stage(DoubleBruter(DoublePDT(0x1000000000000000)))
#proofDF.add_stage(ByteLenOffByOneBruter(ByteLenPDT(BytePDT(0x01))))
#proofDF.add_stage(ShortLenOffByOneBruter(ShortLenPDT(ShortPDT(0x1000))))
#proofDF.add_stage(LongLenOffByOneBruter(LongLenPDT(LongPDT(0x10000000))))
#proofDF.add_stage(DoubleLenOffByOneBruter(DoubleLenPDT(DoublePDT(0x1000000000000000))))
#proofDF.add_stage(ByteLenOffByNBruter(ByteLenPDT(BytePDT(0x01)), 3))
#proofDF.add_stage(ShortLenOffByNBruter(ShortLenPDT(ShortPDT(0x1000)), 3))
#proofDF.add_stage(LongLenOffByNBruter(LongLenPDT(LongPDT(0x10000000)), 3))
#proofDF.add_stage(DoubleLenOffByNBruter(DoubleLenPDT(DoublePDT(0x1000000000000000)), 3))
#proofDF.add_stage()

proofDF.bind_transport(FileOutputTransport)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = proofDF

#THE following function must also exist. This controls what actually happens
#during a protocol's session.
def execute():
    proofDF._transport.send(proofDF.get_bytes())

