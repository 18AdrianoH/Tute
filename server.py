# server houses the main gaming logic and keeps track of who's playing

import threading # for dealing with multiple requests
import time # for time.sleep and more

from network import Master # the network code
from tute import Tute # our game lol
from tute import serialize # serializes the Tute game


# server is the executor of our game
class Server:
    # a server will initially figure out what parameters to try and use
    def __init__(self):
        print('Enter server IP, then server port.')
        self.server_ip = input() # use ipconfig getifaddr en0
        self.port = int(input())
        
        self.master = Master(self.server_ip, self.server_port)
        self.game = Tute()
        
        self.start_networking()
        self.start()

    # launches the networking for the server
    # if it fails just try again with different values
    def start_networking(self):
        # do this at start time because otherwise might lose access in the interim
        self.server_ip = self.get_ip()
        self.port = self.get_port()

        self.master.bind()

    # will start a loop that will run a loop that allows you to shut down the server
    # and also at the same time waits for requests from clients to arrive
    def start(self):
        print('Running... type \'quit\' to shut it down')
        self.running = True
        loop_thread = threading.Thread(target=self.listen)
        loop_thread.start()
        # at the same time take input until we get the message to quit
        while input() != 'quit':
            pass
        self.running = False
        self.socket.close()

    def start(self):
        self.start_networking()
        self.start_game()
        self.start_listening()

    # called when game state changes (should be sent to everyone)
    # 1. someone plays a card
    # 2. someone reveals/hides are a card
    # 3. someone cycles
    def get_on_start_on_round_on_play_on_reveal_message(self):
        # master handles the networking
        self.master.send_state(serialize(tute))

    def process_client_message(self, message):
        args = message.split(' ')
        mtype = args[0]
        # they connect upon first connecting to the server
        if mtype == 'CONNECT':
            self.game.add_player(args[1]) # name of player
            reply = 'CONNECTED {}'.format()
            return reply
        # they cycle if they press spacebar
        elif mtype == 'CYCLE':
            # this will try to start the game
            if self.game.state == 'WAITING' or self.game.state == 'TERMINAL':
                if self.game.state == 'TERMINAL':
                    self.game.reset_game()
                self.game.start_game()
                reply = 'PLAYING' + self.get_play_order()
                return reply
        # this is if they play a card
        elif mtype == 'PLAY':
            # will inform people of what cards in the center after playing a card
            self.game.play_card(args[1], args[2]) # name of player, card to play
            # TODO every individual player needs to be notified of this
            reply = 'CENTER'
            for card in center:
                if not card is None:
                    reply += ' ' + card
            return reply
        # will reveal if not revealed and hide if revealed
        elif mtype == 'REVEAL':
            pass # TODO

    def process_response(self, connection, address):
        # initial connection message
        connection.send('Connected'.encode('utf-8'))

        connected = True
        while connected:
            try:
                data = connection.recv(2048) # number of bits corresponds here to 256 bytes
                decoded_data = data.decode(encoding='utf-8')

                if not data:
                    print('{} disconnected'.format(str(address)))
                    connected = False
                else:
                    print('Recieved {}'.format(decoded_data))
                    print('Sending {}'.format(reply))
                    reply = self.process_client_message(decoded_data)
                    connection.sendall(reply.encode(encoding='utf-8'))

            except Exception as exc:
                print(str(exc))
                break # TODO figure out what to do here; right now we are just trying to avoid infinite loops
        
        connection.close()
        print('Closing Thread...')
        return # this will terminate a thread in python


if __name__ == "__main__":
    server = Server()