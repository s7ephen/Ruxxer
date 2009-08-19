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


html_document = Dataflow("")
html_document.add_stage(StringPDT("<html><body>"))
html_document_body = SlightlyCorruptString(\
    RepeaterStringPDT("BlahBLah", 200), 5)
html_document.add_stage(html_document_body)
html_document.add_stage(StringPDT("</body></html>"))

firstDataflow = Dataflow("")
#firstDataflow.add_stage(StringPDT("1.1"))
#firstDataflow.add_stage(HttpVersionBruter(StringPDT("1.0")))
#firstDataflow.add_stage(twohun_ok)
#firstDataflow.add_stage(StringPDT(" 200 OK\nContent-Length: 0"))
#firstDataflow.add_stage(StringPDT("\n\n"))
firstDataflow.add_stage(html_document)

firstDataflow = Dataflow("")
firstDataflow.add_stage(HttpVersionBruter(StringPDT("1.0")))
firstDataflow.add_stage(StringPDT(" 200 OK\nContent-Length: 0"))
firstDataflow.add_stage(StringPDT("\n\n"))
firstDataflow.add_stage(html_document)

firstDataflow.bind_transport(TCPServerTransport, "192.168.189.129", 80, AcceptHandler)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = firstDataflow

#THE following function must also exist. This controls what actually happens
#during a protocol's session.
def execute():
#    firstDataflow.reset() 
    pass
