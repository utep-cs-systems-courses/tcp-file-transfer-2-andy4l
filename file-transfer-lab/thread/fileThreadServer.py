#! /usr/bin/env python3

import sys
sys.path.append("../../lib")       # for params
import re, socket, params, os
from threading import Thread, enumerate, Lock
from os import path
from os.path import exists
global fileLock
fileLock = Lock()

cFile = []

def fileTransfer(filename):
    if filename in cFile:
        fsock.send()(b"exists", debug)
    else:
        cFile.append(filename)

def fileDisconnect(filename):
    cFile.remove(filename)


switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)

print("listening on:", bindAddr)


from encapFramedSock import EncapFramedSock

class Server(Thread):
    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)
    def run(self):
        print("new thread handling connection from", self.addr)

        serverFile = self.fsock.receive(debug)
        fileLock.acquire()
        fileTransfer(serverFile)
        fileLock.release()
        nfile = serverFile.decode()
        nfile = "transfered"+nfile
        if exists(nfile):
            self.fsock.send(b"True",debug)
        else:
            self.fsock.send(b"False", debug)
            payload = self.fsock.receive(debug)
            if debug: print("rec'd: ",payload)

            if not payload:
                if debug: print(f"thread connected to {addr} done")
                self.fsock.close()
                return
            outfile = open(nfile,"wb")
            outfile.write(serverFile)
            outfile.write(payload)
            fileDisconnect(serverFile) ## Thread done with file
            self.fsock.send(b"file saved to server",debug)
        

while True:
    sockAddr = lsock.accept()
    server = Server(sockAddr)
    server.start()