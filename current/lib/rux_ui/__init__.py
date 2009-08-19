from Tkinter import *
from tkMessageBox import *
from tkFileDialog import askopenfile
from binascii import hexlify
from cmd import Cmd

class WindowList:

    def __init__(self):
        self.dict = {}
        self.callbacks = []

    def add(self, window):
        window.after_idle(self.call_callbacks)
        self.dict[str(window)] = window

    def delete(self, window):
        try:
            del self.dict[str(window)]
        except KeyError:
            # Sometimes, destroy() is called twice
            pass
        self.call_callbacks()

    def add_windows_to_menu(self,  menu):
        list = []
        for key in self.dict.keys():
            window = self.dict[key]
            try:
                title = window.get_title()
            except TclError:
                continue
            list.append((title, window))
        list.sort()
        for title, window in list:
            menu.add_command(label=title, command=window.wakeup)

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def unregister_callback(self, callback):
        try:
            self.callbacks.remove(callback)
        except ValueError:
            pass

    def call_callbacks(self):
        for callback in self.callbacks:
            try:
                callback()
            except:
                print "warning: callback failed in WindowList", \
                      sys.exc_type, ":", sys.exc_value

registry = WindowList()

add_windows_to_menu = registry.add_windows_to_menu
register_callback = registry.register_callback
unregister_callback = registry.unregister_callback


class ListedToplevel(Toplevel):

    def __init__(self, master, **kw):
        Toplevel.__init__(self, master, kw)
        registry.add(self)
        self.focused_widget = self

    def destroy(self):
        registry.delete(self)
        Toplevel.destroy(self)
        # If this is Idle's last window then quit the mainloop
        # (Needed for clean exit on Windows 98)
        if not registry.dict:
            self.quit()

    def update_windowlist_registry(self, window):
        registry.call_callbacks()

    def get_title(self):
        # Subclass can override
        return self.wm_title()

    def wakeup(self):
        try:
            if self.wm_state() == "iconic":
                self.wm_withdraw()
                self.wm_deiconify()
            self.tkraise()
            self.focused_widget.focus_set()
        except TclError:
            # This can happen when the window menu was torn off.
            # Simply ignore it.
            pass
        
class MainWindow(Tk):
    """
        This is just a small container class for the main Tk() window
        class
    """
    from Tkinter import Toplevel
    def __init__(self):
        Tk.__init__(self)
        self.title(string="Ruxxer: The Fuzzing Language IDE (EDITOR WINDOW)")
        self.editor_win = CodingWindow(root=self)

class SecondaryWindow(Toplevel):
    """
        This is a small container class for Toplevel type secondary windows.
    """
    def __init__(self):
        Toplevel.__init__(self)
        self.title(string="Ruxxer: The Fuzzing Language IDE (OUTPUT WINDOW)")
        self.output_win = OutputWindow(root=self)
        self.stdout = self.output_win.stdout
        self.stderr = self.output_win.stderr
 
class CodingWindow:
    """

        The main class for the Text Editor Window that the user will use
    for editing ruxxer code.

    Contains:
        --> Menu, Frame, and Text widgets.

    """
    def __init__(self, root=None):
        self.root = root
        self.menubar = menubar = Menu(root)
#        self.top = top = WindowList.ListedToplevel(root, menu=self.menubar)
        self.top = top = root
        self.vbar = vbar = Scrollbar(top, name='vbar')
        self.text_frame = text_frame = Frame(top)
        self.text = text = Text(text_frame, name='text', padx=5, wrap='none',
                foreground="black",
                background="white",
                highlightcolor="white",
                highlightbackground="purple",
                insertbackground="green",
                width = 80,
                height = 25)
        self.grammar_mode = "python";
       
        #-----special "environment" values we internally 
        self.env_fhandle = None #The handle to the currently open file.

        self.top.focused_widget = self.text
        # should probably create menubars here
        # Doing a buncha menubar shit here:
        # create a pulldown menu, and add it to the menu bar
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.hello)
        filemenu.add_command(label="Save As...", command=self.hello)
        filemenu.add_command(label="Close", command=self.hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        #change this later
        filemenu.add_command(label="Save and Exit", command=root.quit)
        recentmenu = Menu(filemenu, tearoff = 0)
        recentmenu.add_command(label="Demo1.rux", command=self.demo1)
        recentmenu.add_command(label="Demo2.rux", command=self.hello)
        recentmenu.add_command(label="Demo3.rux", command=self.hello)
        recentmenu.add_command(label="Demo4.rux", command=self.hello)
        recentmenu.add_command(label="Demo5.rux", command=self.hello)
        recentmenu.add_command(label="Demo6.rux", command=self.hello)

        filemenu.add_cascade(label="Open Recent", menu=recentmenu)
        menubar.add_cascade(label="File", menu=filemenu)

        #the "EDIT" dropdown
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut", command=self.hello)
        editmenu.add_command(label="Copy", command=self.hello)
        editmenu.add_command(label="Paste", command=self.hello)
        menubar.add_cascade(label="Edit", menu=editmenu)

        #the "TOOLS" dropdown
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Insert Bytes from file",\
            command=self.insert_bytes_from_file)
        menubar.add_cascade(label="Tools", menu=editmenu)

        # the "ACTIONS" dropdown
        actionmenu = Menu(menubar, tearoff=0)
        #actionmenu.add_command(label="Compile", command=self.hello)
        #actionmenu.add_command(label="Run", command=self.hello)
        actionmenu.add_command(label="Run and Compile",\
            command=self.build_and_compile)
        actionmenu.add_command(label="Visualizer", command=self.hello)
        menubar.add_cascade(label="Action", menu=actionmenu)

        #Grammar Mode Selection Dropdown
        grammar_select = Menu(menubar, tearoff=0)
        grammar_select.add_radiobutton(label="Python", variable=self.grammar_mode,\
             value="python")
        grammar_select.add_radiobutton(label="Ruxxer", variable=self.grammar_mode,\
             value="ruxxer")
        grammar_select.add_radiobutton(label="Python Interactive",\
             variable=self.grammar_mode, value="pyinteract", state="disabled")
        grammar_select.add_radiobutton(label="BNF", variable=self.grammar_mode,\
             value="bnf", state="disabled")
        grammar_select.add_radiobutton(label="C", variable=self.grammar_mode,\
             value="c", state="disabled")
        menubar.add_cascade(label="Grammar Mode", menu=grammar_select)

        # the "HELP" dropdown
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.hello)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        root.config(menu=menubar)

        # also do all the keybindings for this window. 
        # self.apply_bindings()
        # and then also do all the bindings here probably.
        vbar['command'] = text.yview
        vbar.pack(side=RIGHT, fill=Y)
        text['yscrollcommand'] = vbar.set
        fontWeight = 'normal'
        #probably should perform text.config() here
        text_frame.pack(side=LEFT, fill=BOTH, expand=1)
        text.pack(side=TOP, fill=BOTH, expand=1)
        text.focus_set()
    
    def hello(self):
        print("That is not yet implemented :-(")

    def filemenu():
        pass

    def open_file(self):
        """
            Open a file in the coding window.
        """
        f_h = askopenfile('r')
        if f_h is not None:
            self.fhandle = f_h
            self.text.insert(END, self.fhandle.read())
#            print(self.fhandle.read())
        print(repr(f_h))

    def demo1(self):
        """ A damn shame """
        new_start()

    def insert_bytes_from_file(self):
        """
            Insert hex escaped bytes from a files on the filesystem.
        """
        f_h = askopenfile('r')
        disp_buf = ""
        if f_h is not None:
            self.fhandle = f_h
            f_bytes = self.fhandle.read()
            print(("%d escaped bytes inserted from file..." % (len(f_bytes))))
            #change this to use slicing
#            wrap_count = 0 
            for byte in f_bytes:
#                if wrap_count < 10:
#                    wrap_count+=1
#                elif wrap_count == 10:
#                    disp_buf+="\\\n\t"
#                    wrap_count = 0
                disp_buf+='\\x'+hexlify(byte)
            self.text.insert(END, "\""+disp_buf+"\"")
#            print "\""+disp_buf+"\""
        else:
            print "Error Opening that File."

    def build_and_compile(self):
        """
            This will get all the text from the text window
        and pass it to the lexxer for processing. It will then
        attempt to 'execute' the code.
        """
        self.text_contents = self.text.get("1.0", END)
#        print repr(self.text_contents)
        #Change this to have the grammar mode stored in teh Environment Object
#        print self.grammar_mode
        if self.grammar_mode is "ruxxer":
            c = rux_grammar.RuxxerParser()
            c.parse_and_execute(self.text_contents)
        elif self.grammar_mode is "python":
            compiled = compile(self.text_contents, 'text-window-contents',\
                'exec')
            exec(compiled)
 
    def apply_bindings(self, keydefs=None):
        """
            Set up and perform call bindings.
        """
        if keydefs is None:
            keydefs = self.Bindings.default_keydefs
        text = self.text
        text.keydefs = keydefs
        for event, keylist in keydefs.items():
            if keylist:
                text.event_add(event, *keylist)

class OutputWindow:
    """

        This is the window that displays all text.
        All standard print functions will be overridden
        to do a print within the new text output window.

    """
    def __init__(self, root=None):
        self.root = root
        self.top = top = root
        self.tv_frame = tv_frame = Frame(top)
        self.tv = tv = Text(tv_frame, name='text', padx=5, wrap='none',
                foreground="black",
                background="white",
                highlightcolor="white",
                highlightbackground="purple",
                width = 80,
                height = 25)
#                state = 'disabled')
        self.tv.bind("<Key>", self.key_handler)
        self.vbar = vbar = Scrollbar(tv_frame, name='vbar')
        vbar['command'] = tv.yview
        vbar.pack(side=RIGHT, fill=Y)
        tv['yscrollcommand'] = vbar.set
        fontWeight = 'normal'
        clear_button = Button(tv_frame, text="Clear Scrollback",
            state="disabled")
        clear_button.pack(side=BOTTOM, fill=X)    
        #probably should perform tv.config() here
        tv_frame.pack(side=LEFT, fill=BOTH, expand=1)
        tv.pack(side=TOP, fill=BOTH, expand=1)
        tv.focus_set()
        self.stderr = PseudoFile(self)
        self.stdout = PseudoFile(self)

    def oprint(self, text_to_print):
        """
            This function will be exposed externally to allow others to
        print to our window.
        """
        self.tv.insert(END, text_to_print)

    def key_handler(self, event):
        """
        """
        pass

    def clear_scrollback(self):
        """
            Clear the scrollback of the text window.
        """
        self.tv.delete("1.0", END)

class PseudoFile:
    """
        This is used to overload sys.stderr and sys.stdout.
        the object reference passed in on "window_obj" must
        have an "oprint" method.
    """
    def __init__(self, window_obj, encoding=None):
        self.encoding = encoding
        self.window_obj = window_obj
    
    def write(self, s):
        self.window_obj.oprint(s)
    
    def writelines(self, l):
        map(self.write, l)
    
    def flush(self):
        pass

    def isatty(self):
        return True

class VisualizerWindow:
    """
        This is the window that displays the TreeView of the compiled
        Session object.
    """
    def __init__(self, root=None):
        self.root = root
        self.vbar = vbar = Scrollbar(name='vbar')
        self.top = top = root
        self.tv_frame = tv_frame = Frame(top)
         
def start_gui():
    """
        Start the Ruxxer GUI.
    """
    rootWindow = MainWindow()
    outputWindow = SecondaryWindow()

    #We overload the normal stdout/stderr to go to our 
    #output window so we save it here so we can use later if we want.
    global saved_stderr, saved_stdout
    saved_stderr = sys.stderr
    saved_stdout = sys.stdout
    sys.stderr = outputWindow.stderr
    sys.stdout = outputWindow.stdout

    rootWindow.mainloop()
    rootWindow.destroy()
    
class RuxxerBaseUI(Cmd):
    """

        This is a parent class used to create the Ruxxer Interactive
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
            Hard exit from Ruxxer.
        """
        print("\nHard exiting...")
        sys.exit(1)

class RuxxerMasterUI(RuxxerBaseUI):
    """
        This is the Ruxxer master user interface class.
    It can be extended to create addition "command directories" similar to
    Cisco IOS so that each "directory" is actually a submenu with its own
    different commands and such.

    """
    def __init__(self):
        RuxxerBaseUI.__init__(self)
        self.prompt = self.make_prompt("Ruxxer")
        self.doc_header = "RuxxerShell Commands:"
        self.intro = "\n\n...oooOOO Welcome to RuxxerShell OOOooo...\n\n"
        self.root = None # A place holder for a reference to
                         # the MASTER_DATAFLOW aka "root" get set in ._load()
        self.loaded_dataflow = None #a place holder in this CMD module
                                    # for the currently 'loaded' dataflow
                                    #note that this is the MODULE and NOT
                                    # the root Dataflow object
        self.ruxxer_tv = None  #this only get used if the user choses
                                #to use the gui RuxxerDisplay from the
                                #CLI
    def do_show_pec(self, *args):
        """
            This command allows you to display *some* of the contents of the PEC
object
        which contains detailed information about the Ruxxer execution
        environment, as well as configuration infomation.

            Usage:
                Ruxxer.>> show_pec

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
                Ruxxer.>> reset

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
                Ruxxer.>> set_iter 10

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
            in your ruxxer.conf.

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
            raise "Ruxxer Dump Error %s" % msg

        print "Successfully write %s contents to %s." %\
            (self.root.__class__.__name__ , fname)


    def do_load(self, *args):
        """
            This command will attempt to load the dataflow file from the
        filesystem, it will however *NOT* begin execution until you do so
        explicitly.

            Usage:
                Ruxxer.>> load <some_dataflow_file>

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
            This command tells Ruxxer to execute the currently loaded dataflow.
        If there is no currently loaded dataflow this command requires a file
        to be specified.

            Usage:
                Ruxxer.>> execute
                    or
                Ruxxer.>> execute <some_dataflow_file>

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

            This command tells Ruxxer to walk through each iteration of the
        dataflow without actually "executing" the dataflow. You will have to
        hit Enter between each iteration. For testing purposes.

            Usage:
                Ruxxer.>> walk
                    or
                Ruxxer.>> walk <some_dataflow_file>

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
                Ruxxer.>> browser

        """
        if not (self._isloaded()):
            print "No Dataflow to browse. There isnt one loaded!"
        else:
            self.ruxxer_tv = RuxxerDisplay()
            #We have to detect the os to handle the fact that NT cant fork()
            if self.root.PEC.os_type == 'nt':
                self.ruxxer_tv.show_gui_nt(self._get_root())
            if self.root.PEC.os_type == 'posix':
                self.ruxxer_tv.show_gui_posix(self._get_root())

    def do_dataflow_info(self, *args):
        """
            This command provides some basic information about the dataflow
        that is currently loaded

            Usage:
                Ruxxer.>> dataflow_info

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
            Ruxxer.>> find_dups

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
                Ruxxer.>> get_bytes
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
        #try:
        df = __import__(file)
        #except ImportError:
        #import pdb;pdb.set_trace()
        #    print os.getcwd()
        #    raise "The Dataflow '%s' could not be found." %file
        if "MASTER_DATAFLOW" not in dir(df):
            raise "MASTER_DATAFLOW not set."
        if "execute" not in dir(df):
            raise "No \"execute\" method defined"
        if getattr(df, 'MASTER_DATAFLOW')._parent != None:
            raise "Can not set MASTER_DATAFLOW on a dataflow with parents!"

        self.loaded_dataflow = df
        self.root = self._get_root()
        self.root._load_time = time.time()
        self.root.PEC = RuxxerEnvConf() #instantiate PEC in root Dataflow
        return df

    def _load_and_execute(self, file):
        self._load(file)
        self._execute(self.loaded_dataflow)

    def _execute(self, dataflow_module):
        execute = getattr(dataflow_module, 'execute')
        master_dataflow = getattr(dataflow_module, 'MASTER_DATAFLOW')

        master_dataflow._set_start_time()
        master_dataflow.execute()
        disp = RuxxerDisplay()
        while master_dataflow.iter_count < master_dataflow.permutations:
            print "\n"
            print " -- ITERATION %d --" % (master_dataflow.iter_count + 1)#+1for readability
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
        disp = RuxxerDisplay()
        while dataflow.iter_count < dataflow.permutations:
            print "\n"
            print " -- ITERATION %d --" % (dataflow.iter_count + 1)#+1 foreadability
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
            Exit the current Ruxxer CLI session to continue running the
dataflow.
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
    ruxxerCLI = RuxxerMasterUI()
    interactive = use_gui = False
    dataflow_file = ""
    start_iteration = 0
    if len(sys.argv) <= 1:
        ruxxerCLI.cmdloop()
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
                ruxxerCLI.do_load(dataflow_file)
            if use_gui:
                ruxxerCLI.do_browser()
            if start_iteration > 0:
                ruxxerCLI.do_set_iter(start_iteration)
            if interactive is True:
                #then the user probably wants the dataflow loaded theninteractive
                ruxxerCLI.cmdloop()
            if interactive is False:
                #then the user just wants us to go ahead with execution
                #of the dataflow
                ruxxerCLI.do_execute(dataflow_file)
            else: #this should be pretty much everything else
                if not interactive: #this test prevents the doc from being
                                    #printed after exiting interactive mode.
                    print __doc__
                    sys.exit(1)

        except KeyboardInterrupt:
            import pdb; pdb.set_trace()
#            print "\nDropping to Ruxxer CLI..."
#            ruxxerCLI.cmdloop()

def new_start(dataflow_file="example_tcpclient.py", start_iteration=None, use_gui=True):
#    my_path = os.getcwd() + os.path.dirname(__file__)
    my_path = os.path.dirname(__file__)
    temp = my_path+"/dataflows/"+dataflow_file
    dataflow_file=temp.replace(os.getcwd()+"/","")
    print repr(dataflow_file)
    ruxxerCLI = RuxxerMasterUI()
    start_iteration = 0
    ruxxerCLI.do_load(dataflow_file)
    ruxxerCLI.do_execute(dataflow_file)

if __name__ == "__main__":
    pass
