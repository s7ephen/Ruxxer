#!/usr/bin/env python

"""
    The testbed for all Ruxxer UI related code.

"""
from Tkinter import *
from tkMessageBox import *
from tkFileDialog import askopenfile
from binascii import hexlify
import WindowList
import rux_grammar

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
    #output window
    global saved_stderr, saved_stdout
    saved_stderr = sys.stderr
    saved_stdout = sys.stdout
    sys.stderr = outputWindow.stderr
    sys.stdout = outputWindow.stdout

    rootWindow.mainloop()
    rootWindow.destroy()
         
if __name__ == "__main__":
    pass

