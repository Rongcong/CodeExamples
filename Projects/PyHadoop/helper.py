# This file provides common functions for both Master and Worker Classes.
import socket
def recv_message(clientsocket):
    max_data = 1024
    all_data = ""
    # ensures all data is received. 
    while True:
        message = clientsocket.recv(max_data)
        all_data += message.decode("utf-8")
        if len(message) != max_data:
           	break
    # when message is received, close socket.
    clientsocket.close()
    return all_data 
