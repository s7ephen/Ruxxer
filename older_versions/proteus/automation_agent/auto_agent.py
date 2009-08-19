#!/usr/bin/env python
"""
    Automation Agent
        
"""
#from aa_mods import *
#import aa_mods
from cmd import *
import inspect, socket, thread, os, sys, re, pdb, code, pprint

__modules__ = []

global BINDPORT, BINDADDY, OUTPORT
BINDPORT = OUTPORT = 9999
BINDADDY = ''

class AABaseUI(Cmd):
    """

        The base User Interface object.

    """
    path =[] #this is how we fake the "path" of commands.
    name = ""
    listeners = {}

    def __init__(self):
        Cmd.__init__(self)

    def listener(self):
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        mySocket.bind((BINDADDY, BINDPORT))
        mySocket.listen(5)
        print "Ok, I'm listening...what!?"
        channel, details = mySocket.accept()
        thread.start_new_thread(connection,(channel,))
        while True:
            channel, details = mySocket.accept()
            thread.start_new_thread(connection,(channel,))
            print 'We have opened a connection with', details

    def make_prompt(self, name=""):
        test_str = self.get_prompt()
        if test_str.endswith(name+"."):
            test_str += ">> "
            return(test_str)
        #the above is a little hack to test if the path
        #is already set for us, incase this object instance
        #is actually getting reused under the hood.
        self.path.append(name)
        tmp_name = ""
        tmp_name = self.get_prompt()
        tmp_name += ">> "
        return(tmp_name)

    def get_prompt(self):
        tmp_name = ""
        for x in self.path: #iterate through object heirarchy
            tmp_name += (x + ".")
        return tmp_name

    def do_help(self, args):
        """
           Getting help on "help" is kinda retarded dont you think?
        """
        #The only reason to define this method is for the help text in the
        #docstring
        Cmd.do_help(self, args)

    def do_hist(self, args):
        """

            Display command history.

        """
#        n = 0
#        for i in self._hist:
#            print "%d: %s" % (n, i)
#            n+=1
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self._hist)

    def emptyline(self):
        """
            Do nothing on empty input line
        """
        pass

    def preloop(self):
        """
            Initialization before prompting user for commands.
            Despite the claims in the Cmd documentaion, Cmd.preloop() is not a
            stub.
        """
        Cmd.preloop(self)   ## sets up command completion
        self._hist    = []      ## No history yet
        self._locals  = {}      ## Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """
            Take care of any unfinished business.
            Despite the claims in the Cmd documentaion, Cmd.postloop() is not a
            stub.
        """
        Cmd.postloop(self)   ## Clean up command completion
        print "Exiting..."

    def precmd(self, line):
        """
            This method is called after the line has been input but before
            it has been interpreted. If you want to modifdy the input line
            before execution (for example, variable substitution) do it here.

        """
        self._hist+=[line.strip()]
        return line

    def postcmd(self, stop, line):
        """
            If you want to stop the console, return something that evaluates to
            true. If you want to do some post command processing, do it here.

        """
        return stop

    def default(self, line):
        """
            Called on an input line when the command prefix is not recognized.
            In that case we execute the line as Python code.

        """
        try:
            exec(line) in self._locals, self._globals
        except Exception, e:
            #print e.__class__, ":", e
            print "\tCommand not recognized! %s'" % (e)

    def do_exit(self, *args):
        return -1

    do_quit = do_exit
    do_EOF = do_exit

class AAMasterUI(AABaseUI):
    """
        This is the AA master menu, from it other menus extend.
    """
    def __init__(self):
        AABaseUI.__init__(self)
        self.prompt = self.make_prompt("AA")
        self.intro = "\n\tWelcome to the Automation Agent..."

#    def do_pyshell(self, args):
#        """
#            enter an interactive python shell
#        """
#        refs = {}
#        code.interact(None,None,refs)

    def do_shellcmd(self, args):
        """

            Pass anything beginning with '!' to shell.
        
        """
        os.system(args)

#    def do_pyimport(self,string):
#        """
#            Import a python module into the python context
#        """
#        try:
#            __import__(string)
#        except:
#            print "Package %s not found!" % string

#    def do_debug(self,string):
#        """
#            enter the python debugger
#        """
#        pdb.set_trace()


    def do_controllers(self, *args):
        """

            Controllers.
            Remote control of specific applications.

        """
        new_cmd = Ctrlrs()
        new_cmd.cmdloop()
        del(new_cmd)

class Ctrlrs(AABaseUI):
    saved_prompt = ""
    def __init__(self):
        AABaseUI.__init__(self)
        self.prompt = self.make_prompt("Ctrlrs")
        self.intro = "\nControllers."
 
    def do_ie(self, *args):
        """

            A remote control for Internet Explorer.

        """
        new_cmd = ieCtrl()
        new_cmd.cmdloop()
        del(new_cmd)

class ieCtrl(AABaseUI):
    """

        A Controller for Internet Explorer.

    """
    saved_prompt = ""
    def __init__(self):
        AABaseUI.__init__(self)
        self.prompt = self.make_prompt("IECtrl")
        self.intro = "\nWelcome to IE Controller"
        try:
            import win32com.client
        except(ImportError):
            print "*** Unable to import critical modules! Functionality disabled. ***"

        self.ie = win32com.client.Dispatch("InternetExplorer.Application")

    def do_start(self, *args):
        """

            Start IE.

        """
        self.ie.Visible = 1

    def do_stop(self, *args):
        """

            Stop IE.

        """
        self.ie.Visible = 0

    def do_goURL(self, *args):
        """
       
            goURL <URL>

                Tell IE to go to a specific address...  

        """ 
        print "Navigating to %s" % args[0]
        #self.ie.Navigate = args[0]

def main():
    try:
        MasterConsole = AAMasterUI()
        MasterConsole.cmdloop()   
    except(KeyboardInterrupt):
        print "Please use the proper exit commands."

if __name__ == '__main__':
    main()
else:
	print __doc__
