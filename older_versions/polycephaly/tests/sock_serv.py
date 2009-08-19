#!/usr/bin/env python
import thread, socket

mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
mySocket.bind(("127.0.0.1", 8000))
mySocket.listen(5)
print "Ok, I'm listening...what!?"
channel, details = mySocket.accept()
thread.start_new_thread(connection,(channel,))
while True:
    channel, details = mySocket.accept()
    thread.start_new_thread(connection,(channel,))
    print 'We have opened a connection with', details

