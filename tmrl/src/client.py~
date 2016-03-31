# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 14:40:55 2014

tcp_client.py

ref: 
    https://docs.python.org/2/library/socketserver.html
@author: carlos
"""

import socket
#import sys

## ===========================================================================
# Check response from tcp server
# ----------------------------------------------------------------------------
def check_tcp_server(cmd='check',dev="1"):
    """Check the server (the status of other devices).
    (str, str) -> (str)
    cmd   = str that can take one of three values: check, connect, disconnect
    devid = str that can take various values that must be included in the 
            server. E.g., dev1, dev2, or dev3. Each computer should have a 
            unique dev<#>.
    received = a list of connected devices"""
    # ====== Client Variables:
##    HOST = "localhost"
#    HOST = "192.168.1.87"    # Alien WiFi - Kenneland
#    HOST = '192.168.1.87'    # Alien WiFi - ECE Net
#    HOST = "128.111.185.30"  # Alien Wired- ECE Net    PORT = "5007"
#    HOST = "128.111.185.232" # Desktop Wired ECE Net
    
    HOST = "192.168.1.10" # Local network
    
    received =""
    
    devid = "dev{}".format(dev)
    dev_dict = {'dev1':{'PORT':50007},
                'dev2':{'PORT':50008},
                'dev3':{'PORT':50009},
                'dev4':{'PORT':50010},               
                'dev5':{'PORT':50011},                
                'dev6':{'PORT':50012}                
                }    
    PORT = dev_dict[devid]["PORT"] # The same port as used by the server
#    print "Connecting to PORT: ", PORT

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    data = str(dev) + " " + cmd
    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(data + "\n")
    
        # Receive data from the server and shut down
        received = sock.recv(1024)
        
        #print "Sent:     {}".format(data)
        #print "Received: {}".format(received)
    except:
        pass
        
#    finally:
#        sock.close()
        
    return received
#check_tcp_server()

