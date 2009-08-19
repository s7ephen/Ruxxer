from lib.transports import *
from lib.bruters import *

global MASTER_DATAFLOW

def responseHandler(data):
    """
        Doc function here ... 
    """  
    if len(data) <= 0:
        print "oh no!\n\n"
    else:
        print "\n\n%s" % data

class Request(Dataflow):
    """
        Doc class here ... 
    """  
    def __init__(self, name, body, header):
        Dataflow.__init__(self, name)
        self.add_stage(header, body)

class Body(Dataflow):
    """
        Doc class here ... 
    """  
    def __init__(self, name=" ", data="\n\n"):
        Dataflow.__init__(self, name)
        self.add_stage(StringPDT(data))

class Header(Dataflow):
    """
        Doc Header class here ... 
    """    
    def __init__(self, name, method):
        Dataflow.__init__(self, name)

        # method instance variables
        self.method = StringPDT(method)
        self.remotePath = StringPDT(" / ")
        self.httpVersion = StringPDT("HTTP/1.1")

        # addAccept_Encoding variables
        self.acceptEncodingLabel = StringPDT("\nAccept-Encoding: ")
        self.acceptEncodingValue = StringPDT("*")

        # addAccept_Language variables
        self.acceptLangLabel = StringPDT("\nAccept-Language: ")
        self.acceptLangValue = StringPDT("en")

        # addConnection variables
        self.connectionLabel = StringPDT("\nConnection: ")
        self.connectionValue = StringPDT("close")

        # addContent_Encoding variables
        self.conEncodingLabel = StringPDT("\nContent-Encoding: ")
        self.conEncodingValue = StringPDT("identity")

        # addContent_Length variables
        self.conLengthLabel = StringPDT("\nContent-Length: ")
        self.conLengthValue = StringPDT("1024")

        # addDate variables
        self.dateLabel = StringPDT("\nDate: ")
        self.dateValue = StringPDT("Tue, 5 Jun 2007 11:21:31 GMT")

        # addExpect variables
        self.expectLabel = StringPDT("\nExpect: ")
        self.expectValue = StringPDT("100-continue")

        # addHost variables
        self.hostLabel = StringPDT("\nHost: ")
        self.hostURL = StringPDT("www.google.com")
        self.hostPort = StringPDT(":80")

        # addTransfer_Encoding variables
        self.transEncodingLabel = StringPDT("\nTransfer-Encoding: ")
        self.transEncodingValue = StringPDT("identity")
        
        if method == "GET":
            self.add_stage(self.method, self.remotePath)
            # need to add Range
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.35
            
        elif method == "HEAD":
            self.add_stage(self.method, self.remotePath)
            # need to add Range (if appplicable to HEAD)
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.35

        elif method == "CONNECT":
            # TODO: make this work
            self.add_stage(self.method, self.hostURL, self.hostPort)
            
        elif method == "POST":
            pass
        elif method == "OPTIONS":
            pass
        elif method == "PUT":
            pass
        elif method == "DELETE":
            pass
        elif method == "TRACE":
            pass
        elif method == "CONNECT":
            pass
        else:
            raise "HTTP Method not recognized", method

    def addAccept_Encoding(self, val="*"):
        """
            HTTP Header Field
            Type: Request
            Usage: [HeaderInstance].addAccept_Encoding("[encoding string]")
        """
        self.acceptEncodingValue = StringPDT(val)            
        self.add_stage(self.acceptEncodingLabel, self.acceptEncodingValue)        

    def addAccept_Language(self, lang="en"):
        """
            HTTP Header Field
            Type: Request
            Usage: [HeaderInstance].addAccept_Language("lang")
        """
        self.acceptLangValue = StringPDT(lang)
        self.add_stage(self.acceptLangLabel, self.acceptLangValue)        

    def addConnection(self, connectionVal=0):
        """
            HTTP Header Field
            Type: General
            Usage: [HeaderInstance].addConnection([0, 1, 2])
                0 = close
                1 = Keep-Alive
                2 = Persist
        """  
        if connectionVal == 0 :    
            self.connectionValue = StringPDT("close")
            self.add_stage(self.connectionLabel, self.connectionValue)
        elif connectionVal == 1:
            # HTTP 1.0 - depreciated
            self.connectionValue = StringPDT("Keep-Alive")
            self.add_stage(self.connectionLabel, self.connectionValue)
        elif connectionVal == 2:
            # HTTP 1.0 - depreciated
            self.connectionValue = StringPDT("Persist")
            self.add_stage(self.connectionLabel, self.connectionValue)
        else:
            raise "Invalid parameter supplied to HTTP.addConnection([0-2])", connectionVal

    def addContent_Encoding(self, val="identity"):
        """
            HTTP Header Field
            Type: Entity
            Usage: [HeaderInstance].addContent_Encoding("media-type")
        """
        self.conEncodingValue = StringPDT(val)
        self.add_stage(self.conEncodingLabel, self.conEncodingValue)        

    def addContent_Length(self, val="1024"):
        """
            HTTP Header Field
            Type: Entity
            Usage: [HeaderInstance].addContent_Length("len")
        """
        self.conLengthValue = StringPDT(val)
        self.add_stage(self.conLengthLabel, self.conLengthValue)        
        
    def addDate(self):
        """
            HTTP Header Field
            Type: General
            Usage: [HeaderInstance].addDate()
        """        
        self.add_stage(self.dateLabel, self.dateValue)

    def addExpect(self, val="100-continue"):
        """
            HTTP Header Field
            Type: Request
            Usage: [HeaderInstance].addExpect()
        """
        self.expectValue = StringPDT(val)
        self.add_stage(self.expectLabel, self.expectValue)

    def addHttpVersion(self, val="HTTP/1.1"):
        """
            HTTP Version attribute
            Usage: [HeaderInstance].addHttpVerion("ver")
        """
        #self.httpVersion = HttpVersionBruter(StringPDT(val))
        self.httpVersion = StringPDT(val)
        self.add_stage(self.httpVersion)

    def addHost(self, host="www.google.com", port=":80"):
        """
            HTTP Header Field
            Type: Request
            Usage: [HeaderInstance].addHost()
        """
        self.hostURL = StringPDT(host)
        self.hostPort = StringPDT(port)
        self.add_stage(self.hostLabel, self.hostURL, self.hostPort)

    def addTransfer_Encoding(self, val="identity"):
        """
            HTTP Header Field
            Type: General
            Usage: [HeaderInstance].addTransfer_Encoding("media-type")
        """
        self.transEncodingValue = StringPDT(val)
        self.add_stage(self.transEncodingLabel, self.transEncodingValue)        
        
