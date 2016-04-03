import client
import time


if __name__=='__main__':
    dev = 3
    clientConnectThread = client.ClientConnect('connect', dev=dev)
    clientConnectThread.setDaemon(True)
    clientConnectThread.start() #launching thread
    while True: # view <= nviews
        clientConnectThread.update_command('check')
        server_response = clientConnectThread.get_command()
        if "wait" in server_response:
            print "RECEIVED FLAG TO SAVE DATA"
            time.sleep(10)
            clientConnectThread.update_command('close')
            print ('closed the connection')
        else:
            print "\t doing other stuff"        
        print server_response
        time.sleep(10)