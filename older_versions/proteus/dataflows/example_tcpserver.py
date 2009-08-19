from lib.protocols.basic_tcpserver import *
from lib.transports import *

firstDataflow = Dataflow("")
firstDataflow.add_stage(StringPDT("GET / HTTP/1.1"))
firstDataflow.add_stage(StringPDT("\n\n"))

firstDataflow.bind_transport(TCPServerTransport, "192.168.189.129", 7777, ServerHandler)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = firstDataflow

#THE following function must also exist. This controls what actually happens
#during a protocol's session.
def execute():
#    firstDataflow.send(firstDataflow.get_bytes())
#    data = firstDataflow.recv(10000)
#    responseHandler(data)
    pass
