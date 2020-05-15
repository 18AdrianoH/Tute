# server houses the main gaming logic and keeps track of who's playing

import socket
from _thread import *

server = "10.0.0.211" # used ipconfig getifaddr en0 ... might want to automate

# ports are unsigned 16-bit integers, so the largest port is 65535
port = 5555 # TODO add something to find open/free ports
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.bind((server, port))
except socket.error as socket_error:
    print(socket_error)

sock.listen(10) # parameter is how many people you want to let in maximum
print("Started")
print("Waiting...")

# what to do with a client 
def threaded_client(connection, address):
    # initial connection message
    connection.send("Connected".encode("utf-8"))

    connected = True
    while connected:
        reply = ""
        try:
            data = connection.recieve(2048) # number of bits corresponds here to 256 bytes
            decoded_data = data.decode(encoding="utf-8")

            if not data:
                print("{} disconnected".format(str(address)))
                connected = False
            else:
                print("Recieved {}".format(decoded_data))
                print("Sending {}".format(reply))
                connection.sendall(reply.encode(encoding="utf-8"))

        except:
            break # TODO figure out what to do here; right now we are just trying to avoid infinite loops
    
    connection.close()
    print("Closing Thread...")
    return # this will terminate a thread in python

# continually looks for connections
while True:
    connection, address = sock.accept()
    print ("connected to {}".format(str(address)))
    start_new_thread(threaded_client, (connection, address))