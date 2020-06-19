# server houses the main gaming logic and keeps track of who's playing

import threading # for dealing with multiple requests

from network import Master # the network code
from tute import Tute # our game lol
from tute import serialize # serializes the Tute game

THREAD_TIMEOUT = 3.0
REQUESTS = []

# server is the executor of our game
class Server:
    # a server will initially figure out what parameters to try and use
    def __init__(self):
        print('Enter server IP, then server port.')
        self.server_ip = '10.0.0.211'#input() # use ipconfig getifaddr en0
        self.server_port = 5555#int(input())
        
        self.game = Tute()
        self.master = Master(self.server_ip, self.server_port) # master automatically does handshakes

        # LOL
        for address, info in self.master.address_info.items():
            self.game.add_player(info['id'])

        self.running = False
        
        self.start_game() # starts the game itself

    # will start two threads: one lets you quit by typing quit, the other games
    def start_game(self):
        #print('Running... type \'quit\' to shut it down')
        self.running = True
        #loop_thread = threading.Thread(target=self.play)
        #loop_thread.start()
        self.play() # LOL
        # at the same time take input until we get the message to quit
        #while input() != 'quit':
        #    pass
        #self.running = False
        #self.master.socket.close()
        #loop_thread.join(THREAD_TIMEOUT) # doesn't work because it's waiting for a lock

    def listen(self):
        global REQUESTS
        while True:
            # careful with deadlocks
            for request in self.master.listen():
                REQUESTS.append(request)
                if request[1] == 'CYCLE':
                    print('recieved cycle request in listen, len of unfulfilled is now ', len(REQUESTS))

    def play(self):
        global REQUESTS

        print('playing')
        listener = threading.Thread(target=self.listen)
        listener.start()

        while self.running:
            print('.')
            # listen will block on the other end if we need the state to change >:( lul
            self.master.send_state(serialize(self.game)) # update players
            print('sent updated state')
            #state_changed = False
            print('read requests')

            for request in REQUESTS:
                state_changed = self.process_client_message(request[0], request[1]) 
            REQUESTS = []

        print('done playing')
        return
    
    # this processes a message from a user
    def process_client_message(self, player_id, message):
        args = message.split(',') # it should be a string by now
        mtype = args[0]
        # they cycle if they press spacebar
        if mtype == 'CYCLE':
            # this will try to start the game
            if self.game.state == 'WAITING' or self.game.state == 'TERMINAL':
                self.game.increment_state() # might change the state if it's possible
                return True # unfortunately does not always yield a change of state... sometimes there is no change
        # this is if they play a card
        elif mtype == 'PLAY':
            # will inform people of what cards in the center after playing a card
            self.game.play_card(args[1], args[2]) # name of player, card to play
            return True
        # will reveal if not revealed and hide if revealed
        elif mtype == 'REVEAL':
            if args[1] in self.game.player_cards[player_id]:
                self.game.reveal_card(args[1])
                return True
            elif args[1] in self.game.player_won_cards[player_id]:
                self.game.reveal_won_card(args[1])
                return True
            return False
        return False
        


if __name__ == "__main__":
    server = Server()