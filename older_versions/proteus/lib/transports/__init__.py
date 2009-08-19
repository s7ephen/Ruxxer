from lib import *

class BaseTransport:
    """
        This is the parent class of all Transport classes. It defines the
    skeletal structure of a Transport class. Each Transport that extends from
    this will obviously have to fill in what happens in these basic methods.


    NOTES:
        Prepare for Dataflow to load up config values by creating the variables
    (with the same name as the 'options' field in config file) in
    self.__init__().

    Then do all the things you would normally do in __init__() in
    .post_load_config()
    """
    #This will eventually have to support a callback being passed in
    #so that any data that comes from a recv() can be passed back.
    #to userdefined protocol parsers and dataflow logic
    def __init__(self):
        self._active = False #Whether the transport is active/connected/etc

        # ._parent is set externally.

    def send(self, data):
        """
            This method will be overloaded in the extending Transports.
        """
        pass

    def recv(self, data):
        """
            This method will be overloaded in the extending Transports.
        """
        pass

    def reset(self, data):
        """
            This method will be overloaded in the extending Transports.
        """
        pass

    def get_parent(self):
        return self._parent

    def step(self):
        """
            This attribute must be present in every transport, but will usually
        overloaded with a custom version in the Transports that extend from
        this.
        """
        pass

class TCPClientTransport(BaseTransport):
    """
        Client Transport
        
        This allows Proteus to speak TCP, starting out as a client of course.

    """
    def __init__(self, ip="127.0.0.1", port="80"):
        BaseTransport.__init__(self)
        self.sockh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockh.connect((ip, port))
    #OVERLOADS
        self.send = self.sockh.send
        self.recv = self.sockh.recv
        self.reset = self.sockh.close

    def __del__(self):
       self.sockh.close()

BasicTCPTransport = TCPClientTransport

class TCPServerTransport(BaseTransport):
    """

        Server TCP Transport
       
        Single Threaded TCP Server.

        Usage:
            TCPServerTransport(ip="127.0.0.1", port="80", accept_callback)
            
            accept_callback is a function reference that will get called 
            when accept() receives a connection. It will get called with a handle 
            to the new socket being passed into it like so.

                accept_callback(new_connection_handle)

            TCPServerTransport gives the dataflow writer "one shot", in other
            words with each iteration the socket is set up, callback is called,
            and is torn down.
    """
    def __init__(self, ip="127.0.0.1", port="7777", accept_callback=None):
        BaseTransport.__init__(self)
        self.ip = ip
        self.port = port
        self.callback = accept_callback


    def step(self):
        """
            With each iteration, we have to reset the current connection and
        return to the accept().
        """
        if self.get_parent().iter_count < self.get_parent().permutations:
            self.bind_accept()
           
    def bind_accept(self):
        self.sockh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockh.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sockh.bind((self.ip, self.port))
        self.sockh.listen(5)
        self.conn_sock = None #a handle to the socket of the established
                                # connection
        print "\n%s accept()ing on %s:%s for iteration: %d/%d" % \
            (self.__class__.__name__, self.ip, self.port,\
                self.get_parent().iter_count+1, self.get_parent().permutations)
        self.conn_sock, self.conn_details = self.sockh.accept()
        print "\nRemote connection from %s" % self.conn_details[0]
    #OVERLOADS
        self.send = self.conn_sock.send
        self.recv = self.conn_sock.recv
        self.reset = self.conn_sock.close
        if self.callback is None:
            print "No accept() callback defined. skipping."
        else:
            self.callback(self.conn_sock)
        self.conn_details = None #the tuple containing the connection details
        self.sockh.shutdown(socket.SHUT_RDWR)
        self.conn_sock.close()
        self.sockh.close()
 
    def __del__(self):
        if self.sockh:
            self.sockh.close()

class FileOutputTransport(BaseTransport):
    """
        File writing transport.
        Usage:
            a = FileOutputTransport(dir, filename_base, ext)

            dir: output directory (default /tmp)
            filename_base: base filename. for dataflows producing multiple
                            iterations, iteration number will be concatenated
                            to this filename base. 
            ext: file extension to be appended to file name base and 
                 iteration number 
    """
    def __init__(self):
        BaseTransport.__init__(self)

        try:
            os.mkdir(self.dir)
        except OSError:
            pass

        print "Outputting to \"%s\"" % self.dir

    def send(self, *args):
        if not hasattr(self, 'fileh'):
            self.filename = self.dir + self.filename_base + str(self.get_parent().iter_count) + "." + self.ext
            self.fileh = open(self.filename, self.mode)
            self.send = self.fileh.write
            self.recv = self.fileh.read
            self.close = self.fileh.close
            self.reset = None
            self.send(*args)
        
    def step(self):
        """
            Because new file contents are generated with each iteration, and
        because each file generated has a different filename, we must perform
        all this logic in this custom step.

        """
        self.filename = self.dir + self.filename_base + str(self.get_parent().iter_count) + "." + self.ext
        self.fileh = open(self.filename, self.mode)
        self.send = self.fileh.write
        self.recv = self.fileh.read
        self.close = self.fileh.close
        self.reset = None

    def __del__(self):
        self.fileh.close()
