from lib import *

global MASTER_DATAFLOW


def ServerHandler(connection):#we get a handle to the connection passed in.
    connection.recv(2)
    print "Got some data in...yay"
    connection.send("YAY\n\n")

def responseHandler(data):
    if len(data) > 0:
        print "WE GOT DATA!\n%s" % data
    else:
        print "WE DIDNT GET ANY DATA!"

