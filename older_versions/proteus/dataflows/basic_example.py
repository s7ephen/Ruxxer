"""

        A SKELETAL example of the bare minumum contents of a dataflow.

"""
from lib.protocols.basic_tcpserver import *
from lib.transports import *
from lib.bruters import *

global MASTER_DATAFLOW

firstDataflow = Dataflow("MyFirstDataflow")

firstDataflow.bind_transport(FileOutputTransport)

# THE FOLLOWING GLOBAL MUST BE SET with the top level dataflow
MASTER_DATAFLOW = firstDataflow

#THE following function must also exist. This controls what actually happens
#during a protocol's session.
def execute():
    firstDataflow._transport.send(firstDataflow.get_bytes())

