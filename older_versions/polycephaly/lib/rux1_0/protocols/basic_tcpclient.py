global MASTER_DATAFLOW

def responseHandler(data):
    if len(data) > 0:
        print "WE GOT DATA!\n%s" % data
    else:
        print "WE DIDNT GET ANY DATA!"

