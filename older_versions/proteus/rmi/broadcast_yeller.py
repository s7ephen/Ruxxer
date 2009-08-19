#!/usr/bin/env python
from socket import *
import time

def udp_shout():
    data = "I have no legs."
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.sendto(data, ('<broadcast>', 7777))
    print "message \"%s\" sent." % data
    s.shutdown(1)
    time.sleep(10)
