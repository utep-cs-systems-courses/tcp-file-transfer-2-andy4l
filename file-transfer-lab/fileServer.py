#! /usr/bin/env python3
import sys
sys.path.append("../lib") # For params
import re, socket, params, os
from os.path import exists

from framedSock import framedSend, framedReceive
switchesVarDefaults= (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False),
    )
progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

listsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bindAddr = ("127.0.0.1", listenPort)
listsock.bind(bindAddr)
listsock.listen(5)
print("Listening on:", bindAddr)

while True:
    sock, addr = listsock.accept()
    
    if not os.fork():
        print("new child process handling connection from", addr)
        while True:
            payload = framedReceive(sock,debug)
            if not payload:
                break

            try:
                payload2 = framedReceive(sock, debug)
            except:
                print("Connection Lost while receiving")
                sys.exit(0)
                
            if not payload2:
                break
            try:
                framedSend(sock, payload2, debug)
            except:
                print("Connection Lost while sending")
                
            outFile = open(payload, 'wb')
            outFile.write(payload2)
            sock.close()