#!/usr/bin/env python
import Pyro.core
import threading



class Overlord(Pyro.core.ObjBase):
    daemon = None
    uri = None
    lock = None
    lock_val = None
 
    def __init__(self):
        self.lock = threading.Lock()
        self.lock_val = 0
        Pyro.core.ObjBase.__init__(self)

    def bootstrap(self):
        """ 
        This starts the Minion-side pyro server that will share
        out the Minion execution object.
        """
        Pyro.core.initServer()
        self.daemon=Pyro.core.Daemon()
        self.uri=self.daemon.connect(Overlord(),"overlord")
        print "Overloard running on port:",self.daemon.port
        print "The object's uri is:",self.uri
        self.daemon.requestLoop()
   
    def do_it(self, minion_callback_uri):
        self.lock.acquire()
        #critical section
        tmp = Pyro.core.getProxyForURI(minion_callback_uri) 
        #end of critical section
        self.lock.release()

if __name__ == '__main__':
    tmpinst = Overlord()
    tmpinst.bootstrap()

