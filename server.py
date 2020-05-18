# server houses the main gaming logic and keeps track of who's playing

import socket
import threading
import time
# structs is our custom gaming data structures implementation
from structs import Tute

DEFAULT_IP = "" # empty string will become whichever ip is available
DEFAULT_PORT = 5555
MAX_CONNECTIONS = 4 # maximum number of people allowed to connect

# server is the executor of our game
class Server:
    # a server will initially figure out what parameters to try and use
    def __init__(self):
        self.running = False
        self.socket = None
        self.server_ip = None
        self.port = None

    def get_ip(self):
        # used ipconfig getifaddr en0 ... might want to automate
        print("Please enter your IP Address or click enter for the default.")
        ip = input()
        if ip == "":
            ip = DEFAULT_IP
        return ip
    
    def get_port(self):
        # ports are unsigned 16-bit integers, so the largest port is 65535
        print("Please enter a valid port or click enter for the default (5555).")
        port = input()
        if port == "":
            port = DEFAULT_PORT
        return int(port)

    # launches the networking for the server
    # provides a simple UI with multiple connection tries to the server
    # just cntrl + c to cancel if you misclicked
    def start_networking(self):
        not_connected = True
        tries = 3 # try three times to connect with that ip and that port if possible

        while not_connected:
            try:
                # do this at start time because otherwise might lose access in the interim
                self.server_ip = self.get_ip()
                self.port = self.get_port()

                # we are using a TCP socket I believe with a "connection oriented protocol"
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("Socket created, trying to connect...")

                for i in range(tries):
                    print("Try number " + str(i+1))
                    try:
                        self.socket.bind((self.server_ip, self.port))
                        self.socket.listen(MAX_CONNECTIONS) # parameter is how many people you want to let in maximum
                        print("Started server at {} on port {}".format(self.server_ip, str(self.port)))
                        print("Waiting for connections...")
                        not_connected = False
                        break

                    except socket.error as socket_error:
                        print("Failed to start server...")
                        print(socket_error)
                        if i == tries - 1:
                            print("IP/Port aren't available or don't work, try again please")
                        else:
                            delta = 5 * (1 << i)
                            print("Will try to connect again in " + str(delta) + " seconds")
                            time.sleep(delta) # wait five seconds before we try again

            except TypeError as type_error:
                print("You entered the wrong types for IP and port. Port should be an integer")
            except Exception as unknown_error:
                print("Unknown error, please try again...")
   
   # begin the game of Tute in the waiting for "log in phase"
    def start_game(self):
        pass

    # helper for start_listening
    def listen(self):
        while self.running:
            try:
                connection, address = self.socket.accept()
                print ("connected to {} who is using port {}".format(address[0], str(address[1])))
                player_thread = threading.Thread(target=self.process_response, args=(connection, address))
                player_thread.start()
            except ConnectionAbortedError as err:
                # this should only be caused by a race condition where we tried to connect after quitting
                # but before self.running was False so we still did it
                # a better solution would involve locks but this should be fine for now
                assert not self.running, "Some other than the connection race condition may have occured"
        return # threads close when you you return from a function

    # will start a loop that will run a loop that allows you to shut down the server
    # and also at the same time waits for requests from clients to arrive
    def start_listening(self):
        print("Running... type \"quit\" to shut it down")
        self.running = True
        loop_thread = threading.Thread(target=self.listen)
        loop_thread.start()
        # at the same time take input until we get the message to quit
        while input() != "quit":
            pass
        self.running = False
        self.socket.close()

    def start(self):
        self.start_networking()
        self.start_game()
        self.start_listening()

    def process_response(self, connection, address):
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


if __name__ == "__main__":
    server = Server()
    server.start()