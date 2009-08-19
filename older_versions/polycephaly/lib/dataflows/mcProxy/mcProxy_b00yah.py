from lib.protocols.basic_tcpserver import *
from lib.transports import *
from lib.bruters import *
global MASTER_DATAFLOW


def AcceptHandler(connection):#we get a handle to the connection passed in.
    connection.recv(16)
    connection.send(firstDataflow.get_bytes())

def responseHandler(data):
    if len(data) > 0:
        print "WE GOT DATA!\n%s" % data
    else:
        print "WE DIDNT GET ANY DATA!"

firstDataflow = Dataflow("")
#firstDataflow.add_stage(StringPDT("1.0"))
firstDataflow.add_stage(HttpVersionBruter(StringPDT("1.0")))
firstDataflow.add_stage(SlightlyCorruptString(StringPDT(" 200 OK\nContent-Length: 0"), 5))
#firstDataflow.add_stage(StringPDT(" 200 OK\nContent-Length: 0"))
firstDataflow.add_stage(StringPDT("\n\n"))

firstDataflow.bind_transport(TCPServerTransport, "172.16.18.66", 7777, AcceptHandler)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = firstDataflow

#THE following function must also exist. This controls what actually happens
#during a protocol's session.
def execute():
#    firstDataflow.reset() 
    pass
