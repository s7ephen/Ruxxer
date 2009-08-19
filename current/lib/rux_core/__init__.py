"""
    PythonLib

"""

import os
import sys
import struct
import time
import pprint
from threading import Thread
import ConfigParser as CP
import pygtk
import socket
import urllib
import getopt
#import gtk
import md5

from binascii import hexlify
from cmd import Cmd

from primitives import *
from ruxxers import *
from comms import *

def rux_repr(bytes):
    """
        Ruxxer's custom repr(). It forces display as escaped bytes *even*
        when the value is within printable ascii range (unlike repr()).

        EG: \\xde\\xad\\xbe\\xef

    """
    retstr = ""
    if issubclass(bytes.__class_, str):
        for byte in bytes:
            retstr+='\\x'+hexlify(byte)
        return retstr
    else: #we cant handle those types so just default to the normal repr()
        print "Ruxxer Error. Ruxxer can not handle %s" %\
            bytes.__class__
        repr(bytes)

class Session:
    """
        Sessions are the master object...a Ruxxer API script will look like:
        
            mySMTPFuzz = Session()
            mySMTPFuzz.bind_transport(TCPClient())
            def session_main():
                .....
                ... A buncha the Structures, Primitives, Ruxxers getting used
                .....
            mySMTPFuzz.setmain(session_main)
            mySMTPFuzz.execute()
        
        the goal here is to pull all the 'execution' stuff out of Structures and Primitives
        and place it entirely in this new object...For now the "body" of what happens during
        the session will have to be placed inside of whatever function gets passed to setmain()
        
   """
    def __init__(self, name):
    	self._transport = None
        self._transport_co = None
        self._stages = []

    def add_stage(self, *additions):
        """

        """
        #If the object being added is a Dataflow, we
        #   1. tell him that we are his parent, then add him
        #       so that in effect every child dataflow has a link to his parent
        #   2. we update our permutation count to reflect that of our children

        for addition in additions:
            if issubclass(addition.__class__, (Primitive, Structure, Ruxxer)):
                if addition not in self._stages: #uniqueness is PARAMOUNT!!!
                    addition._parent = self
                    self._stages.append(addition)
                    self.permutations = self.calculate_permutations()
                else:
                    raise "%s already exists in %s" % (repr(addition), repr(self))
            else:
                raise "You can only add Primitives, Ruxxers, and other Structures to Dataflow objects!"
    def _set_start_time(self):
        self._start_time=time.time()
        for stage in self._stages:
            if issubclass(stage.__class__, Dataflow):
                stage._start_time = time.time()

    def _prepare_transport(self):
        """
            This method is simply a helper function to organize the process
        of setting up the Transport for use by the Dataflow its bound to.
        """
        setattr(self._transport_co, "_parent",self)
        if len(self._transport_args) == 0:
    #       Now we must check the configuration for this Dataflow and see if there
    #       are any sections in it that match the Transport we are currently dealing
    #       with. If so, then we set those values inside the class object so that 
    #       the Transport can make use of them as early as his __init__()
            transport_name = self._transport_co.__name__.upper()
            if self.PEC.config.has_section(transport_name):
                #proceed getting and settng values
                for option in self.PEC.config.options(transport_name):
                    value = self.PEC.config.get(transport_name, option)
                    if hasattr(self._transport_co, option): #set the attribute
                        print "%s already has attribute %s ...skipping." % \
                            (transport_name, option)
                    else:
                        setattr(self._transport_co, option, value)
            else:
                raise "Transport Configuration Error. Section %s not found in Proteus self.config." % \
                    transport_name
        else: #the Dataflow developer specified Transport args, so use them
            pass

#       OK now that everything has been set in the class instance its safe to
#       instantiate!
        self._transport = self._transport_co(*self._transport_args)
        self.send = self._transport.send
        self.recv = self._transport.recv
        self.reset = self._transport.reset

    def execute(self):
        """
            This method begins everything. This method should only get called
        on the "root" or "MASTER" dataflow.

        """
        self._set_start_time()
        self._prepare_transport()

    def bind_transport(self, transport, *args):
        """
            Associate a transport with the instance of the Dataflow object.
        """
        #Instantiation of the transport doesnt *actually* happen here, just
        #gets stored as classobj. It happens in self.execute(), so its closer to runtime
        self._transport_co = transport
        self._transport_args = args
                
class Structure:
    """

    """
    def __init__(self, name):
        self._transport = None #The actual instance of the Transport
        self._transport_co = None #The "class object" of the Transport, for
                                  #storage until runtime
        self._transport_args = None #arguments the user wanted for the Transport
        self._stages = [] 
        self._parent = None
        self._name = name # Dataflows must have a name assigned.
        self.permutations = 0 # A placeholder for what will be an permutation 
                               # count
        self.iter_count = 0
        self._start_time = None #this get sets at .execute() time.
        self._load_time = None #this gets set in the root dataflow at load time.
        self.PEC = None# Contains a reference to the instance of ProteusEnvConf
                 # This only gets set in the root Dataflow
                 # It exists here simply because we dont want to rely on it
                 # being anywhere else (like the CLI). We *do* however rely
                 # on someone else setting this value for us. currently the CLI

    def __del__(self):
        del(self._transport) 
        #some other stuff should probably happen here.

    def __len__(self):
        """
            
        """
        count = 0
        for stage in self._stages:
            count+=len(stage)
        return count

    def step(self):
        if self.iter_count+2 > self.permutations: #skip adding
            pass
        
        self.iter_count += 1

        for stage in self._stages: #recurse downward.
            stage.step()

    def isRoot(self):
        """

        """
        if self._parent == None:
            return True
        else:
            return False

    def set_iter_count(self, iter):
        """
            Used in fastforwarding. Recursively step()s until an iteration is
        reached.
        
            Usage:
                set_iter_count(1)  <-- first iteration.

        """
        if iter > self.permutations > 0:
            retval = False
            raise "Can not set Structure %s to iteration %d for it only has %d" %\
                (self.__class__, iter, self.permutations)

        if iter == 0:
            self.iter_count = 0
            return True

        while self.iter_count != iter:
            self.step()
#            self.set_iter_count(iter)
        retval = True
#        self.iter_count = iter
#        for stage in self._stages:
#            stage.set_iter_count(iter)
        return retval

    def calculate_permutations(self):
        my_perms = []
        permutations = 1
        for stage in self._stages:
            my_perms.append(stage.permutations)
        for perm in my_perms:
            permutations *= perm
        return permutations
            
    def get_stagecount(self):
        return len(self._stages)

    def _get_childs_rightpeer_count(self, child):
        """
            Find child in _stages and tell it how many peers it has
            to the right of it.

            NOTE! this algorithm doesnt allow for copies of the same instance in
                 _stages . this MUST BE FIGURED OUT!
        """
        child_index = 0
        for stage in self._stages:
            if stage == child:
                break
            child_index += 1
        #for now assume the child is actually in there.
        return ((len(self._stages)-1) - child_index)

    def _get_childs_rightpeer_perms(self, child):
        """
            Find child in _stages and calculate all the permutations
            to the right of it.
        """
        child_index = 0
        right_perms = 1
        for stage in self._stages:
            if stage == child:
                break
            child_index += 1
        #for now assume the child is actually in there.
        for stage in self._stages[(child_index+1):]: #we *dont* want to also
                                                     #include childs
                                                     # permutation count in this
                                                     # calculation
            right_perms *= stage.permutations
        return (right_perms)

    def get_parent(self):
        """
            Return a reference to my parent.
        """
        return self._parent

        
    def flatten(self, lis):
        """
            Flatten a list of objects. used recursively to return pdt contents
        to the caller.
        """
        ret_list = []
        for val in lis:
            if val.__class__ is list:
                ret_list.extend(self.flatten(val))
            else:
                ret_list.append(lis)
                break
        return ret_list

    def get_bytes(self):
        """
            Check all potential children for data, concatentate, and return
        data.

        """
        bytes = []
        for stage in self._stages:
            if stage.__class__ is Dataflow:
                bytes.extend(stage.get_bytes()) #this looks right, but seems like
                                                #should be an append
            else:
                bytes.append(stage.get_bytes())
        return "".join(bytes)



class ProteusEnvConf:
    """
        This class is simply a storage location for all Proteus configuration
    information and environmental information that might be needed during
    execution. It gets instantiated and used inside of the master Dataflow, but
    exists outside the Dataflow class definition simply for code cleanliness
    reasons.

    """
    def __init__(self):
        self.user = os.getenv("USER") # The user running proteus
        self.os_type = os.name # The OS name: 'posix', 'nt', 'os2', 'mac',
                                    # 'ce' or 'riscos'
        self.pwd = os.curdir #current working directory
        self.environ = os.environ # a dictionary of the process
                                        # environment
        self.sep = os.sep # The path separator for this filesystem
        self.linesep = os.linesep # The line separator for this filesystem
        self.extsep = os.extsep #The extension separator for this FS 
        
        self.config_file = self.check_config() #the check must preceed
                                                # get_config()
        self.config = self.get_config() # The Config object from the config file
        self.output_dir = self.config.get("GENERAL", "output_dir")

    def get_config(self):
        """
            Read the Proteus Config file and return the config object
        """
        self.config = CP.ConfigParser()
        if self.config_file is False:
            raise "Could not fine a suitable config file!!!"

        self.config.read(self.config_file)
        return self.config
 
    def check_config(self):
        """
            Check if a config file exists in:
                /etc/proteus.conf
                ./proteus.conf
            The filename of the first config that exists is returned or else
        'False' is returned.

        """
        # These configuration locations need to be passed in at some point
        # potentially from a configuration file.
        conf_locations = ['/etc/ruxxer.conf', './ruxxer.conf']
        for potential_place in conf_locations:
            if os.path.exists(potential_place):
                return potential_place
        return False


class BrowserThread(Thread):
    """
        This is strictly an internally used class because the module "threading"
    requires threads to be defined as classes with a .run() method. i
    So to make it generically usable
    I smash pass in a function reference and an argument reference.
    and that function reference gets called with the arguement in the heart
    of the thread.
    """
    def __init__(self, func, arg):
        Thread.__init__(self)
        self.setDaemon(False)
        self.func = func
        self.arg = arg

    def run(self):
        self.func(self.arg)
         
class ProteusDisplay:
    """
        A class to contain all the display methods for Proteus Dataflows.
        
        This stuff all resides in a class outside of the Dataflow class definition
    simply for code cleanliness.

    """
    def show_gui_posix(self, start_obj):
        """
            Fork a thread to run the GUI Dataflow Browser in.
        """
        import os
        pid = os.fork()
        if pid:
            pass #parent does nothing
        else: #child spawns gtk window
            self._print_tree_gtk(start_obj)
        del(os)

    def show_gui_nt(self, start_obj):
        """
            Fire off a proper thread that the GUI Dataflow Browser will run in.

        Note:
            Currently buggy, GTK and threading arent compatible you will
            have to manually kill python on exit.

        """
        browser = BrowserThread(self._print_tree_gtk, start_obj)
        browser.setDaemon(False)
        browser.start()

    def _print_tree_gtk(self, start_obj):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.main_quit)
        window.connect("destroy", gtk.main_quit)
        window.set_title("Dataflow Viewer :  '%s'" % (start_obj._name))
        window.set_size_request(500, 500)
        # create a TreeStore with one string column to use as the model
        treestore = gtk.TreeStore(str)

        #we assume we are at the top level Dataflow
        p_iter = treestore.append(None, ["%s with %d bytes and %d permutations.\n%.28s...'" % (start_obj.__class__.__name__, len(start_obj), start_obj.permutations, repr(start_obj.get_bytes()))])
        if issubclass(start_obj.__class__, Dataflow):
            self._print_tree_gtk_helper(start_obj, p_iter, treestore)
        else:
            raise "You must provide a top level Dataflow object."

        # create the TreeView using treestore
        treeview = gtk.TreeView(treestore)
        # create the TreeViewColumn to display the data
        tvcolumn = gtk.TreeViewColumn()
        # add tvcolumn to treeview
        treeview.append_column(tvcolumn)
        # create a CellRendererText to render the data
        cell = gtk.CellRendererText()
        # add the cell to the tvcolumn and allow it to expand
        tvcolumn.pack_start(cell, True)
        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        tvcolumn.add_attribute(cell, 'text', 0)
        # make it searchable
        treeview.set_search_column(0)
        # DISAllow sorting on the column
        tvcolumn.set_sort_column_id(1) 
        # DISAllow drag and drop reordering of rows
        treeview.set_reorderable(False)

        #Make headers unclickable, and gone entirely.
        treeview.set_headers_clickable(False)
        treeview.set_headers_visible(False)

        #display window
        window.add(treeview)
        window.show_all()
        gtk.main()

    def _print_tree_gtk_helper(self, start_obj, p_iter, treestore):
            for stage in start_obj._stages:
                if issubclass(stage.__class__, Dataflow):
                    #recurse
                    c_iter = treestore.append(p_iter, ["%s with %d bytes and %d permutations.\n%.28s...'" % (stage.__class__.__name__, len(stage), stage.permutations, repr(stage.get_bytes()))])
                    self._print_tree_gtk_helper(stage, c_iter, treestore)
                elif issubclass(stage.__class__, Bruter):
                    treestore.append(p_iter, ["%s with %d permutations\n%s ...'" % (stage.__class__.__name__, len(stage._data), repr(stage._data[:3]))]) #only first three
                else:
                    treestore.append(p_iter, ["%s with %d bytes\n%.28s ...'" % (stage.__class__.__name__, len(stage), repr(stage.get_bytes()))])   


    def _print_tree(self, start_obj, padding):
        print  "%s+-Dataflow (%d permutations): '%.28s ...'" % (padding[:-1], start_obj.permutations, repr(start_obj.get_bytes()))
#        print padding[:-1] + "+-" + "Dataflow" + " (" + repr(start_obj.permutations) + " permutations)" + ":" + repr(start_obj.get_bytes())
        padding += ' ' # add a space
        count = 0
        if issubclass(start_obj.__class__, Dataflow): 
        #if start_obj.__class__ is Dataflow:
            for stage in start_obj._stages:
                count += 1
                print padding + "|"
                if issubclass(stage.__class__, Dataflow):
                #if stage.__class__ is Dataflow:
                    if count==len(stage._stages):
                        self._print_tree(stage, padding)
                    else:
                        self._print_tree(stage, padding + "|")
                elif issubclass(stage.__class__, Bruter):
#                    print  "%s+-Bruter (%d permutations) (%d peers to the
#                    right) (%d right peer permutations) %d" % (padding,
#                    stage.permutations, stage.get_rightpeer_count(),
#                    stage.get_rightpeer_perms(), stage.step_index)

                     print  "%s+-Bruter (%d/%d permutations): '%.28s ...'" % (padding, stage.step_index+1, stage.permutations, repr(stage.get_bytes()))
#                    print  "%s+-Bruter (%d permutations) on element: %d" %
#                    (padding, stage.permutations, stage.step_index)
                elif issubclass(stage.__class__, BasePDT):
                    print  "%s+-PDT: '%.28s ...'" % (padding, repr(stage.get_bytes()))
        else:
            raise "You must provide a top level Dataflow object."
