from lib.protocols.mcProxy import *

bod = Body("bod1")

# HTTP METHODS
#head = Header("head1", "GET")
#head = Header("head1", "TRACE")
head = Header("head1", "HEAD")
#head = Header("head1", "CONNECT")

head.addHttpVersion("HTTP/1.1")
#head.addHttpVersion(HttpVersionBruter(StringPDT("HTTP/1.1")).get_bytes())

#spipeDF = Dataflow("")

#spipeDF.add_stage("")

# HTTP Header Fields
#head.addHost("www.google.com", ":80")
#head.addDate()
#head.addAccept_Language()
#head.addAccept_Language(FormatStringAttack(StringPDT("en-US")).get_bytes())
#head.addConnection(0)
#head.addAccept_Encoding("application/octet-stream")
head.addAccept_Encoding(FormatStringAttack(StringPDT("application/octet-stream")))
#head.addContent_Encoding("application/octet-stream")
#head.addContent_Length()
#head.addContent_Length("10")
#head.addTransfer_Encoding()
#head.addTransfer_Encoding("gzip")

req = Request("req1", bod, head)

#print "bod.__class__.__name__: ", bod.__class__.__name__
#print "head.__class__.__name__: ", head.__class__.__name__
#print "req.__class__.__name__: ", req.__class__.__name__

req.bind_transport(BasicTCPTransport, "google.com", 80)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = req

def execute():
    print "----------"
    print "get_bytes: \n", req.get_bytes()
    print "----------"
    req.send(req.get_bytes())
    data = req.recv(10000)
    responseHandler(data)
 

