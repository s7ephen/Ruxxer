#!/usr/bin/env python
from socket import *

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('0.0.0.0',7777))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
while 1:
    data,addr = s.recvfrom(1024)
    if not data:
        pass
    else:
        print data,"\n"
