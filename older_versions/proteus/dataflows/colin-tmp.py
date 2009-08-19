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
#firstDataflow.add_stage(StringPDT("HTTP/1.1"))
firstDataflow.add_stage(HttpVersionBruter(StringPDT("1.0")))
#firstDataflow.add_stage(StringPDT("1.0"))
firstDataflow.add_stage(StringPDT(" 200 OK\n"))
firstDataflow.add_stage(StringPDT("Content-Length: 40\n"))
firstDataflow.add_stage(CompletelyCorruptString(StringPDT("0123456789"),100))
#firstDataflow.add_stage(ContentLengthBruter(StringPDT("9")))
#firstDataflow.add_stage(ContentLengthBruter(StringPDT("0")))
#firstDataflow.add_stage(StringPDT("100"))
#firstDataflow.add_stage(StringPDT(" 200 OK\nContent-Length: 0"))
firstDataflow.add_stage(StringPDT("\n\n"))
firstDataflow.add_stage(StringPDT("40\n"))
#firstDataflow.add_stage(StringPDT("123456789\n"))
firstDataflow.add_stage(CompletelyCorruptString(StringPDT("0123456789i012345678901234567890123456789"),100))


firstDataflow.bind_transport(TCPServerTransport, "172.16.18.66", 7777, AcceptHandler)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = firstDataflow

#THE following function must also exist. This controls what actually happens
#during a protocol's session.
def execute():
#    firstDataflow.reset() 
    pass
