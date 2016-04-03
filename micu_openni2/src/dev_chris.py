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
        if "save" in server_response:
            print "RECEIVED FLAG TO SAVE DATA"
            time.sleep(30)
            clientConnectThread.update_command('close')
            server_response = clientConnectThread.get_command()
        else:
            print "\t doing other stuff"        
        print server_response
        time.sleep(5)