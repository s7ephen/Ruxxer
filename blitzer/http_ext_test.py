#!/usr/bin/env python2.4
"""
    Trying to extend HTTPServer to accept and make use
    of an external object.
"""

try:
    import string,cgi,time,getopt,sys, socket, BaseHTTPServer
    from os import curdir, sep
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    print "There is a problem importing a critical component."
    raise


class TextGenerator:
    def __init__(self):
        self.index = 0
        self.text = ['red', 'white', 'blue', 'green']

    def get_text(self):
        ret =  self.text[self.index]
        self.index += 1
        if self.index > (len(self.text) - 1):
            self.index = 0 #reset index back to beginning
        return ret


class MyServer(HTTPServer):

    """Extended to keep a bit of data around."""

    def __init__(self, ref, *args):
        HTTPServer.__init__(self, *args)
        self.ref = ref


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset="us-ascii"')
        self.end_headers()
        self.wfile.write("<html><body><br/>My favorite color is:<br/>")
        self.wfile.write(self.server.ref.get_text())
        self.wfile.write("</body></html>")

if __name__ == '__main__':
    tgen = TextGenerator()
    server = MyServer(tgen, ('', 7777), MyHandler)
    try:
        print 'started httpserver on first available interface port 7777...'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'ok...quitting...'
        server.socket.close()
        sys.exit(2)
