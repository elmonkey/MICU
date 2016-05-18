import client
import time, sys

done = False
if __name__=='__main__':
    dev = 1
    clientConnectThread = client.ClientConnect('connect', dev=dev)
    clientConnectThread.setDaemon(True)
    clientConnectThread.start() #launching thread
    while not done: # view <= nviews
        clientConnectThread.update_command('check')
        server_response = clientConnectThread.get_command()
        if "save" in server_response:
            print "RECEIVED FLAG TO SAVE DATA"
            time.sleep(5)            
        elif "close"in server_response:
            print ('Closing the connection')
            clientConnectThread.update_command('close')
            time.sleep(5)
            done = True
        else:
            print "\t doing other stuff"        
        print server_response
        time.sleep(2)
sys.exit(1)
