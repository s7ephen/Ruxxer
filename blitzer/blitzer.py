#!/usr/bin/env python2.4
"""
   Blitzer
 
        Blindly 'bitblitz' through a file, outputting each variation
    of that file onto the filesystem or serving it embedded in an
    HTML document


    -f <filename> : file to fuzz.

        CONTENT DELIVERY OPTIONS
    -h : serve bruted iterations as html content.
    -d <directory> : output iterations by placing them in 'directory'.
                     CAN NOT be used with "-h"
    -i <ip> : IP of local interface to bind HTTP server to.
    -p <port> : Port to bind HTTP server to.

        FILE FUZZING OPTIONS
    -e : Endianness
        1 : Big Endian
        2 : Little Endian
        3 : System default endianness    ***default***

    -c <1,2,4>: Munge chunk size
        1 : Munge at byte level (1 byte)     ***default***
        2 : Munge at word level (2 bytes) (signed short)
        4 : Munge a double-word level (4 bytes) (signed int)
       
    -m <1,2,3,4>: Munge type 
        1: Off-by-one munge (current chunk value +1, current chunk value -1)
        2: Min Value only (E.G.: if chunk_size is one byte: \\x00)
        3: Max Value only (E.G.: if chunk_size is one byte: \\xff)
        4: Do all the above for each chunk in my "chunk_size"    ***default***

    -M <e,l>: Munge Mode
           e: "Exponential" (produces an almost unusable number of variations.
           l: "Linear" (more reasonable)    ***default*** 

    S.A. Ridley
    Oct 2006
"""
try:
    import struct,string,cgi,time,getopt,sys, socket, BaseHTTPServer
    from os import curdir, sep
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    print "There is a problem importing a critical component."

class FileBruter:
    """
        
        This class handles the 'munging' of a specific file. A file (specified
        by the user) is munged according to the specifications of the user.

    """
    def __init__(self, target_fname, endian, chunk_size, munge, munge_mode):
        self.doc = ""
        self.target_fname = target_fname
        self.endian = endian
        self.chunk_size = chunk_size
        self.munge = munge
        self.file_ext = None #this gets set in .load_target_fname()
        self.raw_bytes = self.load_target_fname()
        self.chunks = [] #this get set in .expand_chunks()
        self.mal_chunk = False #indicates if there is a trailing chunk
        self.expand_chunks()
        self._packop = "" #placeholder for pack opcode set in .set_packing()
        self.set_packing() #set all the packing variables
        self.munge_mode = munge_mode
        print "%d chunks" % len(self.chunks)
        self.mungers = [] #this gets set in .expand_mungers()
        self.expand_mungers()
        self._mung_ind = 0 #this is only used to keep state for linear munging.
        self._chunk_ind = 0 #this is only used to keep state for linear munging.
        self.perms = self.calc_perms()
        print "%d mungers" % len(self.mungers)
        print "%d permutations" % self.perms
        self.iteration = 0 #starting on first iteration

    def set_packing(self):
        if self.endian == 1: #Big endian
            e_pack = '>'
        if self.endian == 2: #Little endian
            e_pack = '<'
        if self.endian == 3:
            e_pack = '='

        if self.chunk_size == 1: #byte
            s_pack = 'b' 
        if self.chunk_size == 2: #unsigned short
            s_pack = 's'
        if self.chunk_size == 4: #unsigned int
            s_pack = 'i'

        self._packop = e_pack+s_pack

    def calc_perms(self):
        if self.munge_mode == 'exponential':
            perms = len(self.mungers)**len(self.chunks) #the total number of variations of the file.
        if self.munge_mode == 'linear':
            perms = len(self.mungers)*len(self.chunks)

        return(perms)

    def load_target_fname(self):
        """
            Load the file itself as the first iteration value.
        Also, parse out the file's extension and store.
        """
        bytes = []
        try:
            file_h = open(self.target_fname, "rb")
            bytes = file_h.read()
            file_h.close()
        except IOError:
            print "File '%s' doesnt appear to exist or be readable" % (self.target_fname)
            sys.exit(2)

        #now we save the file extension sanz the '.'
        tmp = str.split(self.target_fname, '\\') # just in case it has a fully
                                           # path
        tmp2 = str.split(tmp[len(tmp)-1], '.') # split last element on period
        self.file_ext = tmp2[len(tmp2)-1] # get last element

        if len(bytes) > 0:
            return bytes

    def permute(self):
        """

        """
        print "Serving Iteration (%d/%d) of '%s'." %\
            (self.iteration + 1, self.perms, self.target_fname)
    
        bytes = self.get_file_bytes()
        self.step()
        return bytes

    def get_file_bytes(self):
        """
            Reconstruct the file from the list of chunks by executing the correct
        munger for the chunk, and appending to a new file list.
        """
        munged_file = []
        if self.munge_mode == 'linear':
            for chunk_index in range(len(self.chunks)):
                if (chunk_index == self._chunk_ind) and not self.isrightmost(chunk_index):
                                                   #then we are at the one that
                                                   #we want to manipulate
                                                   #omitting the last chunk
                    print "we are on munge %d chunk %d" % (self._mung_ind, self._chunk_ind)
                    new_chunk = self.mungers[self._mung_ind](self._chunk_ind)
                else: #we are not at one we care about so just get the
                      #unmanipulated bytes
                    new_chunk = self.chunks[chunk_index]
                munged_file.append(new_chunk)
            print "retrieving bytes at munger %d of chunk %d" % (self._mung_ind, self._chunk_ind)
            print repr("".join(munged_file))
            return "".join(munged_file)

        if self.munge_mode == 'exponential':
            for chunk_index in range(len(self.chunks)):
                if not self.isrightmost(chunk_index):
                    new_chunk = self.mungers[self.select_munger(chunk_index)](chunk_index)
                    munged_file.append(new_chunk)
                else: #it *is* the rightmost chunk and we ignore that one for
                      #now
                    new_chunk = self.chunks[chunk_index]
            print repr("".join(munged_file))
            return "".join(munged_file)

    def step(self):
        """
            Step forward in our iteration list.
        """
        if self.munge_mode == 'exponential':
            print "stepping exponentially"
            if self.iteration <= (self.perms-1):
                self.iteration += 1
        if self.munge_mode == 'linear':
            print "stepping linearly"
            self.iteration += 1
            if self._mung_ind < (len(self.mungers)-1):
                self._mung_ind+=1
            elif self._mung_ind >= (len(self.mungers)-1):
                self._mung_ind = 0
                self._chunk_ind+=1

    def expand_chunks(self):
        index = 0
        if (len(self.raw_bytes) % self.chunk_size) != 0:
            self.mal_chunk = True
        while index <= ((len(self.raw_bytes)/self.chunk_size)*self.chunk_size):
            self.chunks.append(self.raw_bytes[index:index+self.chunk_size])
            index+=self.chunk_size
        if self.mal_chunk:
            self.chunks.append(self.raw_bytes[((len(self.raw_bytes)/self.chunk_size)*self.chunk_size):])

    def count_rightmost(self, chunk_index):
        """
            Count the number of chunks to the right of chunk_index.
        """
        count = len(self.chunks[chunk_index+1:])
#        print "there are %d to the right of %d" % (count, chunk_index)
        return count

    def product_of_rightmost(self, chunk_index):
        """
            Multiply together the number of mungers for each chunk to the right
            of chunk_index. 
        """
        #We cheat here, since we know the number of mungers is homogenenous for
        #all chunks we dont actually count them up.
        product = len(self.mungers)**self.count_rightmost(chunk_index)
#        print "%d is product for %d" % (product, chunk_index)
        return product

    def select_munger(self, chunk_index):
        """
            Based on iteration we are currently on, select the appropriate
        munger. based on the 'rightmost' equation.
        """
        if not self.isrightmost(chunk_index):
            mung_ind = (self.iteration/self.product_of_rightmost(chunk_index)) % len(self.mungers)
        else:
            mung_ind = self.iteration % len(self.mungers)
#        print "munge: %d" % mung_ind
        return mung_ind
        
    def isrightmost(self, chunk_index):
        """
            Check if chunk_index is the end.
        """
        if (self.chunks[chunk_index] == self.chunks[(len(self.chunks)-1)]):
            return True
        else: return False
        
    def expand_mungers(self):
        """
            The munger's array is a list of references to all the munge's that are to be
        performed on each chunk. Since the same munges are applied to each
        chunk we only need one list. Consequently the number of variations
        of the file will be equal to the len(self.chunks) * len(self.mungers)
        """
        if self.munge == 1:
            self.mungers.append(self.munge_current)
            self.mungers.append(self.munge_plus_one)
            self.mungers.append(self.munge_minus_one)

        if self.munge == 2:
            self.mungers.append(self.munge_current)
            self.mungers.append(self.munge_min)

        if self.munge == 3:
            self.mungers.append(self.munge_current)
            self.mungers.append(self.munge_max)

        if self.munge == 4:
            self.mungers.append(self.munge_current)
            self.mungers.append(self.munge_plus_one)
            self.mungers.append(self.munge_minus_one)
            self.mungers.append(self.munge_min)
            self.mungers.append(self.munge_max)

    def munge_plus_one(self, chunk_index):
        val = struct.unpack(self._packop, self.chunks[chunk_index])[0]
        val += 1
        val = struct.pack(self._packop, val)
        return val
 
    def munge_minus_one(self, chunk_index):
        val = struct.unpack(self._packop, self.chunks[chunk_index])[0]
        val -= 1
        val = struct.pack(self._packop, val)
        return val
    
    def munge_current(self, chunk_index):
        return self.chunks[chunk_index]
    
    def munge_max(self, chunk_index):
        return self.chunks[chunk_index]
    
    def munge_min(self, chunk_index):
        return self.chunks[chunk_index]

class MyHTTPServer(HTTPServer):
    """
        We extend this so we can cache the reference to our 
    """
    def __init__(self, ref, *args):
        HTTPServer.__init__(self, *args)
        if ref.__class__ is FileBruter:
            self.ref = ref
        else:
            raise "SOMETHING IS SERIOUSLY BROKEN!"

    def gen_embed(self):
        """
            Generate the HTML Document that will embed our fuzzed content.
        """
        embed_doc = \
"""
<html>
<head>
<title>Iteration (""" + str((self.ref.iteration + 1)) + "/" + str(self.ref.perms) + """)</title>
</head>
<script language="Javascript">
<!--
var URL   = ""
function reload() {
location = URL
}
setTimeout("reload()");
//-->
</script>
<body onload="reload()">
<img src=\"""" + "brute_target." + self.ref.file_ext + """ " >
</body>
</html>
"""
        return embed_doc

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            #this .server reference isnt documented but luckily its there!
            if self.path.endswith(self.server.ref.file_ext): #they are prolly
                                                             #requesting the
                                                             #file we are
                                                             #bruting
                if self.server.ref.iteration >= self.server.ref.perms:
                    self.wfile.write("DONE")
                else:
                    self.wfile.write(self.server.ref.permute())
            else:
                self.send_response(200)
#                self.send_header('Content-type', 'text/html; charset="us-ascii"')
#                self.end_headers()
                if self.server.ref.iteration >= self.server.ref.perms:
                    self.wfile.write("DONE")
                else:
                    self.wfile.write(self.server.gen_embed())
        except IOError:
            self.send_error(404,'%s isn\'t a page you asshat.' % self.path)

def do_fs_dump(fbruter, directory):
    import os
    
    print "\nI will be placing %d files each with %d bytes onto the filesystem in '%s'" \
        % (fbruter.perms, len(fbruter.raw_bytes), directory)
    print "That means %d bytes total." \
        % (fbruter.perms * len(fbruter.raw_bytes))
    resp = raw_input("\tAre you sure its ok to continue!? [y/n] ")
    if resp not in ("yes", "Yes", "Y", 'y'):
        print "Ok...quitting."
        sys.exit(1)
    try:
        os.chdir(directory)
    except OSError:
        print "ERROR!"
    while fbruter.iteration < fbruter.perms:
        fname = "%s_%s.%s" % (os.path.split(fbruter.target_fname)[1], str(fbruter.iteration), fbruter.file_ext)
        fh = open(fname, 'wb')
        fh.write(fbruter.permute())
        fh.close()
    print "Done."


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],\
            "f:hi:p:d:e:c:m:M:", ["filename=", "html", "ip=",\
             "port=", "directory=", "endian=", "chunksize=","munge=", "Mode="])
    except getopt.error:
        print __doc__
        sys.exit(2)

    if len(sys.argv) <= 1:
        print __doc__
        sys.exit(2)

    global fbruter; fbruter = None
    fname = None
    HTML = False
    ip = None
    port = None
    output_dir = None
    #set defaults.
    endian = 3; chunk_size = 1; munge = 4; munge_mode='linear'
    for o, a in opts:
        if o in ("-f", "--filename"):
            fname = a
        if o in ("-h", "--html"):
            html = True
        if o in ("-i", "--ip"):
            ip = a
        if o in ("-p", "--port"):
            try:
                port = int(a)
            except:
                "Port must be a numeric value."
                sys.exit(2)
        if o in ("-d", "--directory"):
            output_dir = a
        if o in ("-e", "--endian"):
            try:
                endian = int(a)
            except:
                print "Endianess must be defined as 1, 2, or 3"
                sys.exit(2)
        if o in ("-c", "--chunksize"):
            try:
                chunk_size = int(a)
            except:
                print "Chunk size must be defined as 1, 2, or 4"
        if o in ("-m", "--munge"):
            munge = int(a)
        if o in ("-M", "--Mode"):
            if a in ("e", "E"):
                print "Exponential munging selected, BE WARNED!"
                munge_mode = 'exponential'

    if endian not in (1, 2, 3):
        print "Endianess must be defined as 1, 2, or 3"
        sys.exit(2)
    if chunk_size not in (1, 2, 4):
        print "Chunk size must be defined as 1, 2, or 4"
        sys.exit(2)
    if munge not in (1, 2, 3, 4):
        print "Munge value must be defined as 1, 2, 3, or 4"
        sys.exit(2)

    fbruter = FileBruter(fname, endian, chunk_size, munge, munge_mode)

#DO ALL THE CRAPPY USER INPUT CLEANSING
    if (fbruter == None):
        print "You MUST supply a file to use as input."
        sys.exit(2)
    elif (fbruter != None) and (output_dir != None):
        print "Proceeding with directory output."
        do_fs_dump(fbruter, output_dir)
        sys.exit(0)
    elif (fbruter != None) and (html == False):
        print "You must chose to output files to filesystem or via http."
        sys.exit(2)
    if (html != False) and ((ip == None) or (port == None)):
        print "You must supply a port and ip with the html option."
        sys.exit(2)
    elif ip:
        try:
            socket.inet_aton(ip)
        except socket.error:
            print "Illegal Address supplied."
            sys.exit(2)
        print "Proceeding with serving via http."
        server = MyHTTPServer(fbruter, (ip, port), MyHandler) #CHANGE YER IP
#        server = HTTPServer(('', 7777), MyHandler) #CHANGE YER IP
#        import pdb; pdb.set_trace()
        try:
            print 'Started http server at http://%s:%d/ ...' % (ip, port)
            server.serve_forever()
        except KeyboardInterrupt:
            print 'OK. quitting.'
            server.socket.close()

#----------------------
if __name__ == '__main__':
    main()
