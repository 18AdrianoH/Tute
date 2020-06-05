# server houses the main gaming logic and keeps track of who's playing

# messages to server are 
# CONNECT <username>
# PLAY <card>

import socket
import threading
import time
import random

DEFAULT_IP = "10.0.0.211" # empty string will become whichever ip is available
DEFAULT_PORT = 5555
MAX_CONNECTIONS = 4 # maximum number of people allowed to connect

FACES = ("B", "E", "C", "O")
VALUES = ("A", "R", "C", "S", "9", "8", "7", "6", "5", "4", "3", "2")

def get_cards():
    cards = [face + "_" + value for face in FACES for value in VALUES]
    random.shuffle(cards)
    return cards

def split_cards():
    # there are a total of 48 cards
    return cards[:12], cards[12:24], cards[24:36], cards[36:]

players = [] # go in this order

class Player:
    def __init__(self, id):
        # your id is a string
        assert type(id) == str
        self.id = id

        self.cards = []
    
    def has(self, card):
        return card in self.cards

# Tute states are
# WAITING # waiting for players
# WAITING_P1 # waiting for player 1 to play
# WAITING_P2 # waiting for player 2 to play
# WAITING_P3 # waiting for player 3 to play
# WAITING_P4 # waiting for player 4 to play
# TERMINAL # game has ended players now count points, can restart game now
class Tute:
    def __init__(self, players):
        ############################ STATE MACHINE #######################
        self.state = "WAITING" # initially in waiting state
        self.round_num = 0
        # play states are always randomized
        self.play_states = ["WAITING_P1", "WAITING_P2", "WAITING_P3", "WAITING_P4"]
        random.shuffle(play_states) # decide order of play
        # if we want to re-initialize just use previous players
        self.players = [None, None, None, None] if players is None else players
        self.player_index = 0
        self.play_state_index = 0
        ############################
    
    # add a player if a player with that id is not already present
    def add_player(self, player_id):
        num_player = 0 # i.e. player 1
        for player in self.players:
            if player is not None:
                if player == player_id: # assume "player" is a string
                    return False
                # else
                num_player += 1
        
        assert num_player < 4 # lul

        index = 0 # for player inside the players array
        insert_index = 0
        for player in self.play_states:
            player_num = int(player[-1]) - 1
            if player_num == num_player:
                insert_index = index
                break
            index += 1
        
        self.players(insert_index) = player_id
        return True
    
    # start the game after we are waiting for players
    # called after we have all four players
    def start_game(self):
        assert not players.contains(None) # will have the four names of the four people
        assert self.state == "WAITING"
        self.state = self.play_states[0]
        self.round_num = 1 # start at 1
        # self.state is now WAITING_PX for some X so taking [-1] is the last element
        self.player_index = int(self.state[-1]) - 1 # will always index by one so -1
        self.play_state_index = 0
    
    # this should only be called when 
    def increment_state(self):
        # if we are still in the same round
        if self.play_state_index < 3:
            self.play_state_index += 1
            self.player_index = int(self.state[-1]) - 1
        # if we are going to a new round
        elif self.round_num < 12: # 12 rounds at the last round it will be over
            self.round_num += 1
            self.play_state_index = 0
            self.state = self.play_states[0] # TODO FIX THIS SO THAT THE WINNER GOES FIRST
        else:
            # this is basically all that needs to be done, now players 
            self.state = "TERMINAL" # we will be in the terminal state
    
    # for the next game
    def reset_game(self):
        self.__init__(self.players) # list of names

# server is the executor of our game
class Server:
    # a server will initially figure out what parameters to try and use
    def __init__(self):
        self.running = False
        self.socket = None
        self.server_ip = None
        self.port = None
        self.game = Tute()

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