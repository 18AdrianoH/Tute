# server houses the main gaming logic and keeps track of who's playing

import socket
from _thread import *

# what to do with a client 
def threaded_client(connection, address):
    # initial connection message
    connection.send("Connected".encode("utf-8"))

    connected = True
    while connected:
        reply = "response from the server"
        try:
            data = connection.recv(2048) # number of bits corresponds here to 256 bytes
            decoded_data = data.decode(encoding="utf-8")

            if not data:
                print("{} disconnected".format(str(address)))
                connected = False
            else:
                print("Recieved {}".format(decoded_data))
                print("Sending {}".format(reply))
                connection.sendall(reply.encode(encoding="utf-8"))

        except Exception as exc:
            print(str(exc))
            break # TODO figure out what to do here; right now we are just trying to avoid infinite loops
    
    connection.close()
    print("Closing Thread...")
    return # this will terminate a thread in python

class Server:
    # a server will initially figure out what parameters to try and use
    def __init__(self):
        self.running = False
        self.socket = None
        self.server_ip = None
        self.port = None

    def get_ip(self):
        # used ipconfig getifaddr en0 ... might want to automate
        return "10.0.0.211" 
    
    def get_port(self):
        # ports are unsigned 16-bit integers, so the largest port is 65535
        return 5555

    def start(self):
        # do this at start time because otherwise might lose access in the interim
        self.server_ip = self.get_ip()
        self.port = self.get_port()

        # we are using a TCP socket I believe with a "connection oriented protocol"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.server_ip, self.port))
            self.socket.listen(10) # parameter is how many people you want to let in maximum
            print("Started server at {} on port {}".format(self.server_ip, str(self.port)))
            print("Waiting for connections...")
        except socket.error as socket_error:
            print("Failed to start server...")
            print(socket_error)

    def run(self):
        self.running = True
        start_new_thread(self._run_loop, ())

        # at the same time take input until we get the message to quit
        while input() != "quit":
            pass
        self.running = False
        self.socket.close()

    def _run_loop(self):
        while self.running:
            connection, address = self.socket.accept()
            print ("connected to {} who is using port {}".format(address[0], str(address[1])))
            start_new_thread(threaded_client, (connection, address))



if __name__ == "__main__":
    server = Server()
    server.start()
    server.run()