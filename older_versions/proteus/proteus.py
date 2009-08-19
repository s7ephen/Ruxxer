#!/usr/bin/env python
"""

    Proteus the Protocol Fuzzer
    ---------------------------

    Usage example:
        ./proteus.py -d dataflows/first_dataflow.py -i -g

        -d <dataflow> ||  --dataflow=<dataflow> 
                Dataflow to execute

        -w <dataflow> || --walk=<dataflow>
                Walk the dataflow, dont execute it 

        -f <number> || --fast-forward=<number>
                Fast forward to iteration <number>

        -i || --interactive: 
                Use the interactive ProteusShell

        -g || --use-gui:  
                Display the Dataflow Browser GUI

        -h || --help: 
                Display this usage info.
       
"""

from lib import *

class ProteusBaseUI(Cmd):
    """

        This is a parent class used to create the Proteus Interactive
    CLI.

    """
    path =[] #this is how we fake the "path" of commands.
    name = ""

    def __init__(self):
        Cmd.__init__(self)

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
           Getting help on "help" is kinda silly dont you think?
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
            print "\tWhat!? I dont understand: %s'" % (e)

    def do_exit(self, args):
        """
            Exits from this tier in the CLI.
            If you need to HARD exit, use 'diemfqr'.
        """
        return 1

    do_quit = do_exit

    def do_die(self, args):
        """
            Hard exit from Proteus.
        """
        print("\nHard exiting...")
        sys.exit(1)

class ProteusMasterUI(ProteusBaseUI):
    """
        This is the Proteus master user interface class.
    It can be extended to create addition "command directories" similar to
    Cisco IOS so that each "directory" is actually a submenu with its own
    different commands and such.

    """
    def __init__(self):
        ProteusBaseUI.__init__(self)
        self.prompt = self.make_prompt("Proteus")
        self.doc_header = "ProteusShell Commands:"
        self.intro = "\n\n...oooOOO Welcome to ProteusShell OOOooo...\n\n"
        self.root = None # A place holder for a reference to 
                         # the MASTER_DATAFLOW aka "root" get set in ._load()
        self.loaded_dataflow = None #a place holder in this CMD module
                                    # for the currently 'loaded' dataflow
                                    #note that this is the MODULE and NOT
                                    # the root Dataflow object
        self.proteus_tv = None  #this only get used if the user choses
                                #to use the gui ProteusDisplay from the
                                #CLI
    def do_show_pec(self, *args):
        """
            This command allows you to display *some* of the contents of the PEC object
        which contains detailed information about the Proteus execution
        environment, as well as configuration infomation.

            Usage:
                Proteus.>> show_pec

        """
        if not self._isloaded():
            print "No Dataflow is currently loaded"
        else:
            print "\nRunning as user: '%s'." % self.root.PEC.user
            print "Running on OS: '%s'." % self.root.PEC.os_type
            print "Running in dir: '%s'." % self.root.PEC.pwd
            print "Using config file: '%s'." % self.root.PEC.config_file
            print "The global output dir is: %s " % self.root.PEC.output_dir
            print "\n"

    def do_reset(self, *args):
        """

            Reset the internal state of the Dataflow, so that it can be
        executed again.

            Usage:
                Proteus.>> reset

        """
        if not self._isloaded():
            print "There is no Dataflow to reset, there isnt one loaded!"
        else:
            master_dataflow = self._get_root()
            if (master_dataflow.set_iter_count(0)):
                print "Dataflow successfully reset!"
            else:
               raise "Dataflow was not successfully reset..."

    def do_set_iter(self, *args):
        """

            Set the iteration at a specific number. This is particularly
        useful when 'fast forwarding' to a specific iteration.
 
            Usage:
                Proteus.>> set_iter 10
                
                This will fast forward to iteration 10

        """
        #NOTE: all the logic testing if the iteration actually exists
        #       is down in .set_iter_count()
        iter = int(args[0]) - 1 #the iteration is +1 the iter_count
        
        if(self.root.set_iter_count(iter)):
            print "Dataflow %s was successfully fast forwarded to iteration %d" % \
                (self.loaded_dataflow.__name__, iter+1)

    def do_step(self, *args):
        """
            Step forward a single iteration in the dataflow.

        """
        if self._isloaded():
            self.root.step()
            print "Ok now current iteration is: %d" % (int(self.root.iter_count)+1)
        else:
            print "Can not step. There is no Dataflow loaded. Use 'load'."
 
    def do_dump(self, *args):
        """

            Dump contents of Dataflow to a file.
            If a file argument is specified, then use that file, if not 
            dump in the standard format to the global dumps directory specified
            in your proteus.conf.

            Usage:
                dump <filename>
                
        """ 
        output_dir = self.root.PEC.config.get("GENERAL", "output_dir")
        splitr = (self.loaded_dataflow.__name__).split(self.root.PEC.sep)
        if len(splitr) > 1:
            dname = splitr[1]
        else: dname = splitr[0]
        dname_withtime = dname + str(self.root._load_time).split('.')[0] 
        if args[0] != '': #check if there is something in the string.
                            #if so then we will use it as our filename
            fname = output_dir + self.root.PEC.sep+args[0]
        else:
            fname = output_dir + self.root.PEC.sep + dname_withtime +\
                "_" + str(self.root.iter_count+1) + ".dump"
             
        try:
            outf = open(fname, "wb")
            outf.write(self.root.get_bytes())
            outf.close()
        except IOError, msg:
            raise "Proteus Dump Error %s" % msg

        print "Successfully write %s contents to %s." %\
            (self.root.__class__.__name__ , fname)

 
    def do_load(self, *args):
        """
            This command will attempt to load the dataflow file from the
        filesystem, it will however *NOT* begin execution until you do so
        explicitly.

            Usage: 
                Proteus.>> load <some_dataflow_file>

        """
        file = args[0].strip()
        if (file == "") or (file is None):
            print "Error: Dataflow '%s' could not be loaded" % file
            return 0 
        else:
            if os.path.exists(file):
                print "Attempting to load '%s' ..." % file
                self.loaded_dataflow = self._load(file)
            elif os.path.exists(file+".py"):
                print "Attempting to load '%s' ..." % file
                self.loaded_dataflow = self._load(file)
            else:
                print "Error: File '%s' does not exist!" % file
        if self._isloaded():
            print "Successfully loaded '%s' !" % file
        else:
            print "Error: There was some error while loading '%s'" % file
            self.root = None
            self.loaded_dataflow = None

    def do_execute(self, *args):
        """
            This command tells Proteus to execute the currently loaded dataflow.
        If there is no currently loaded dataflow this command requires a file
        to be specified.

            Usage:
                Proteus.>> execute  
                    or 
                Proteus.>> execute <some_dataflow_file>

        """
        file = args[0].strip()
        if (self._isloaded()) and (file is None or ""):
            print "Error: No Dataflow specified, and no Dataflow is loaded!"
            return 0
        if self.loaded_dataflow is None:
            self._load_and_execute(file)
        else:
            try:
                self._execute(self.loaded_dataflow)
            except KeyboardInterrupt:
                print "\nExiting dataflow execution...\"execute\" to resume..."

    def do_walk(self, *args):
        """

            This command tells Proteus to walk through each iteration of the
        dataflow without actually "executing" the dataflow. You will have to
        hit Enter between each iteration. For testing purposes.

            Usage:
                Proteus.>> walk  
                    or 
                Proteus.>> walk <some_dataflow_file>

        """
        file = args[0].strip()
        
        if (self._isloaded()) and (file is None or ""):
            print "Error: No Dataflow specified, and no Dataflow is loaded!"
            return 0
        if self.loaded_dataflow is None:
            self._load(file)
        else:
            try:
                self._walk(self.loaded_dataflow)
            except KeyboardInterrupt:
                print "\nExiting Dataflow walk type \"walk\" again to resume..."

    def do_browser(self, *args):
        """
            
            This command will display the loaded Dataflow using the GUI Dataflow
        browser.

            Usage:
                Proteus.>> browser
            
        """
        if not (self._isloaded()):
            print "No Dataflow to browse. There isnt one loaded!"
        else:
            self.proteus_tv = ProteusDisplay()
            #We have to detect the os to handle the fact that NT cant fork()
            if self.root.PEC.os_type == 'nt':
                self.proteus_tv.show_gui_nt(self._get_root())
            if self.root.PEC.os_type == 'posix':
                self.proteus_tv.show_gui_posix(self._get_root())

    def do_dataflow_info(self, *args):
        """
            This command provides some basic information about the dataflow
        that is currently loaded
    
            Usage:
                Proteus.>> dataflow_info

        """
        print "\n\tDataflow Name: %s" % self.loaded_dataflow.__name__
        print "\tDataflow file: %s" % self.loaded_dataflow.__file__
        print "\tDataflow loaded at: %s" %\
            time.asctime(time.localtime(self.root._load_time))
        print "\tCurrent Iteration: %d" % (int(self.root.iter_count)+1)
        print "\tNumber of Permutations: %d" % self.root.permutations
        print "\t\nNote: Use get_bytes command to see the contents of dataflow."

    def do_find_dups(self, *args):
        """
            Walk the entire dataflow, checking if there are iterations that
        somehow contain duplicate bytes.
 
        Usage:
            Proteus.>> find_dups

        """
        iter_digest = {} #a dict to store the digests
        dups = {} #a dict to tally the number of duplicates
        iters_with_dups = 0

        if not (self._isloaded()):
            print "Error: No Dataflow specified, and no Dataflow is loaded!"
            return 0

        while self.root.iter_count+1 < self.root.permutations:
            iter_digest[int(self.root.iter_count)] = \
                md5.md5(self.root.get_bytes()).hexdigest()
            self.root.step()

        for key in iter_digest.keys():
            if dups.has_key(iter_digest[key]):
                dups[iter_digest[key]] += 1
            else:
                dups[iter_digest[key]] = 0

        dupped = 0
        for key in dups.keys():
            if dups[key] > 0:
                iters_with_dups += 1
                for ikey in iter_digest.keys():
                    if iter_digest[ikey] == str(dups[key]):
                        dupped = ikey

        if iters_with_dups > 0:
            print "Total number of iterations with duplicates: %d" %\
                iters_with_dups
        else:
            print "Each iteration seems to be unique!"

        self.do_reset()

    def do_get_bytes(self, *args):
        """
            Print out the contents of the dataflow.

            Usage:
                Proteus.>> get_bytes
        """
        if not (self._isloaded()):
            print "No Dataflow to print. There isnt one loaded!"
        else:
            print(repr(self.root.get_bytes()))

    def do_debug(self, *args):
        """
            Enter a PDB session.
        """
        import pdb; pdb.set_trace()

    def _load(self, file):
        """
            The *real* loader. This takes in the file and returns a reference to
        module object that is the loaded dataflow. This functional intended
        only for internal class use.

        """
        #print "--------", file
        #import pdb;pdb.set_trace()
        if file.endswith(".py"):
            file = file.replace(".py", "")
        try:
            df = __import__(file)
        except ImportError:
        #import pdb;pdb.set_trace()
            raise "The Dataflow '%s' could not be found." %file
        if "MASTER_DATAFLOW" not in dir(df):
            raise "MASTER_DATAFLOW not set."
        if "execute" not in dir(df):
            raise "No \"execute\" method defined"
        if getattr(df, 'MASTER_DATAFLOW')._parent != None:
            raise "Can not set MASTER_DATAFLOW on a dataflow with parents!"

        self.loaded_dataflow = df
        self.root = self._get_root()
        self.root._load_time = time.time()
        self.root.PEC = ProteusEnvConf() #instantiate PEC in root Dataflow
        return df

    def _load_and_execute(self, file):
        self._load(file)
        self._execute(self.loaded_dataflow)

    def _execute(self, dataflow_module):
        execute = getattr(dataflow_module, 'execute')
        master_dataflow = getattr(dataflow_module, 'MASTER_DATAFLOW')

        master_dataflow._set_start_time()
        master_dataflow.execute()
        disp = ProteusDisplay()
        while master_dataflow.iter_count < master_dataflow.permutations:
            print "\n"
            print " -- ITERATION %d --" % (master_dataflow.iter_count + 1)#+1 for readability
            disp._print_tree(master_dataflow, " ")
            dataflow_module.execute() #execute "execute()" in dataflow
            master_dataflow._transport.step()
            master_dataflow.step()

    def _walk(self, dataflow_module):
        execute = getattr(dataflow_module, 'execute')
        dataflow = getattr(dataflow_module, 'MASTER_DATAFLOW')
        if dataflow._parent != None:
            raise "Can not set MASTER_DATAFLOW on a dataflow with parents!"
        dataflow._set_start_time()
        disp = ProteusDisplay()
        while dataflow.iter_count < dataflow.permutations:
            print "\n"
            print " -- ITERATION %d --" % (dataflow.iter_count + 1)#+1 for readability
                            #for algorithmic reasons (in Bruter's
                            #calc_permutation_selection()) the first
                            # iteration actually has to be zero
            disp._print_tree(dataflow, " ")
            print "\nHit <Enter> to step to next iteration...",
            raw_input()
            dataflow.step()
        dataflow.set_iter_count(0) #reset back to beginning and display data
#        disp._print_tree_gtk(dataflow)

    def _isloaded(self):
        """ 
            Helper function to see if a dataflow has yet been loaded.
        """
        if (self.loaded_dataflow is None):
            return 0
        else: #something is loaded, return True
            return 1

    def _get_root(self):
        """
            Helper function to get are reference to the root/master dataflow.
        """
        if self._isloaded():
            df = getattr(self.loaded_dataflow, 'MASTER_DATAFLOW')
            return df
        else:
            print "There isnt a Dataflow currently loaded."
            return 0

    def _get_exec(self):
        """
            Helper function to get a reference to the execute() attribute of a
        Dataflow module.
        """
        if self._isloaded():
            df = getattr(self.loaded_dataflow, 'execute')
            return df
        else:
            print "There isnt a Dataflow currently loaded."
            return 0

    def cont(self, *args):
        """
            Exit the current Proteus CLI session to continue running the dataflow.
        """
        return 0

    def enable_cont(self):
        """
            This command will "enable" the continue command.
        """
        self.do_continue = self.cont
        self.do_cont = self.cont
 
def main():
    msg = "For help use --help or -h"
    try:
        opts, args = getopt.getopt(sys.argv[1:],\
            "higd:w:f:", ["help","dataflow=", "walk=",\
                 "interactive", "use-gui", "fast-forward="])
    except getopt.error, msg:
        print msg
        sys.exit(2)
    proteusCLI = ProteusMasterUI()
    interactive = use_gui = False
    dataflow_file = ""
    start_iteration = 0
    if len(sys.argv) <= 1:
        proteusCLI.cmdloop()
    else:
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                sys.exit(1)
            if o in ("-d", "--dataflow"):
                dataflow_file = a
            if o in ("-w", "--walk"):
                dataflow_file = a
            if o in ("-i", "--interactive"):
                interactive = True
            if o in ("-f", "--fast-forward"):
                start_iteration = int(a)
            if o in ("-g", "--use-gui"):
                use_gui = True
        try:
            if dataflow_file is not "":
                proteusCLI.do_load(dataflow_file)
            if use_gui:
                proteusCLI.do_browser()
            if start_iteration > 0:
                proteusCLI.do_set_iter(start_iteration)  
            if interactive is True:
                #then the user probably wants the dataflow loaded then interactive
                proteusCLI.cmdloop()
            if interactive is False:
                #then the user just wants us to go ahead with execution
                #of the dataflow
                proteusCLI.do_execute(dataflow_file)
            else: #this should be pretty much everything else
                if not interactive: #this test prevents the doc from being
                                    #printed after exiting interactive mode.
                    print __doc__
                    sys.exit(1)

        except KeyboardInterrupt:
            import pdb; pdb.set_trace()
#            print "\nDropping to Proteus CLI..."
#            proteusCLI.cmdloop()

if __name__ == "__main__":
    main()
