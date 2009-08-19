#!/usr/bin/env python
"""

    McProxy client, to simulate requests from a HTTP client.

    Usage:
        -i <ip>: Destination IP to connect to
        -p <port>: Destination port to connect to
        -h : This help

"""
import socket
import sys
import getopt
import urllib

def sendloop (ip, port, what_to_send):
    try:
       while True:
           print "Connecting to %s" % ip
           f = urllib.urlopen("http://%s:%s" % (ip, port))
           if f:
               print "Received:\n", f.read()
               f.close()
           else:
                print "Could not connect...trying again."

    except KeyboardInterrupt:
       print "Quitting..."
       sys.exit(1)
 
def sendloop_raw(ip, port, what_to_send):
    print "Press CTRL-C to exit:"
    failures = 1
    tolerance = 5
    try:
        while True:
            try:
                sockh = None
                sockh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sockh.connect((ip, int(port)))
                print "------------------"
                print "Sending: %s" % repr(what_to_send)
                failures = 0
                sockh.send(what_to_send)
                print "Received: %s" % repr(sockh.recv(0xffff))
                print "------------------"
                if not sockh:
                    print "Connection closed by remote host..."
                    sockh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sockh.connect((ip, int(port)))
                    print "\nSending: '%s'" % what_to_send
                    sockh.send(what_to_send)
                    print("\nReceived: ", sockh.recv(0xffffff))
                    sockh.close()
            except socket.error, msg:
                if failures == tolerance:
                    print "\n\n%s to %s:%s...Quitting." % (msg[1], ip, port)
                    sys.exit(1)
                else:
                    print "\n\n%s to %s:%s...try %d of %d" %\
                        (msg[1], ip, port, failures, tolerance)
                    failures += 1
                    continue

    except KeyboardInterrupt:
        print "quitting..."
        sys.exit(1)
            
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],\
            "i:p:h:", ["ip=","port=", "help"])
    except getopt.error:
        print __doc__
        sys.exit(2)
    if len(sys.argv) <= 3:
        print __doc__
        sys.exit(1)
    else:
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                sys.exit(1)
            if o in ("-i", "--ip"):
                ip = a
            if o in ("-p", "--port"):
                port = a
        try:
            socket.inet_aton(ip)
        except socket.error:
            print "IP format is invalid.\n"
            sys.exit(1)
        if ip and port:
            sendloop_raw(ip, port, "GET / HTTP/1.1\n\n")
        else: #this should be pretty much everything else
            print __doc__
            sys.exit(1)

if __name__ == "__main__":
    main()
 
