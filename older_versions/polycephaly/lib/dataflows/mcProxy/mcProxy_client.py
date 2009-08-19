from lib.protocols.mcProxy import *

bod = Body("bod1")

# McProxy HTTP methods and header-fields to fuzz against: 
# HTTP/%d.%d, GET, POST, CONNECT, HEAD, expect:, accept-encoding:, host:, 
# content-length:, text/, image/, content-length:, content-encoding:, transfer-encoding:, identity

# HTTP METHODS
#head = Header("head1", "GET")
#head = Header("head1", "TRACE")
head = Header("head1", "HEAD")
#head = Header("head1", "CONNECT")

head.addHttpVersion("HTTP/1.1")

# HTTP Header Fields
#head.addHost()
head.addHost("www.microsoft.com", ":80")
head.addDate()
#head.addAccept_Language()
head.addAccept_Language("en-US")
#head.addConnection()
head.addConnection(0)
#head.addExpect()
#head.addExpect("100-continue")
#head.addAccept_Encoding()
#head.addAccept_Encoding("compress;q=0.5, gzip;q=1.0")
#head.addContent_Encoding()
#head.addContent_Encoding("gzip")
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

