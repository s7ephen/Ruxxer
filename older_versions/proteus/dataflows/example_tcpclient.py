from lib.protocols.basic_tcpclient import *
from lib.transports import *
from lib.bruters import *

firstDataflow = Dataflow(" ")
firstDataflow.add_stage(StringPDT("HEAD / "))
#firstDataflow.add_stage(StringPDT("HTTP/1.1"))
# EXAMPLE OF BRUTER USE TO DEMONSTRATE ITERATIONS.
firstDataflow.add_stage(HttpVersionBruter(StringPDT("HTTP/8.0")))
firstDataflow.add_stage(StringPDT("\n\n"))

firstDataflow.bind_transport(BasicTCPTransport, "127.0.0.1", 8000)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = firstDataflow

#THE following function must also exist. This controls what actually happens
#during a protocol's session.
def execute():
    firstDataflow.send(firstDataflow.get_bytes())
    data = firstDataflow.recv(10000)
#    responseHandler(data)
    print(repr(data))

