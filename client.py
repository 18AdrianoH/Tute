# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server

# this game will have a simple gui where you see your cards and whats on the table
# packets sent and recieved will be encrypted
# it will have basic timers to make sure people don't take too long
# and it will have a simple installer to install python and the necessary dependencies on mac, windows, or linux

import json #LMAO
from tute import deserialize
from gui import Interface
from network import Channel

def main():
    # onboard the network parameters
    print('Please enter the server\'s IP and port')
    server_ip = '10.0.0.211'#input() # TODO
    server_port = 5555#int(input())
    print('Please enter your username')
    player_id = input()

    net = Channel(server_ip, server_port, player_id)
    gui = None

    running = True
    while running:
        # see what the game state is and update our look
        game_state = json.loads(net.listen())
        print('to play ', game_state['to play'])

        if gui == None:
            gui = Interface(player_id, game_state)
        else:
            gui.update(game_state)
        #print("...")
        #print(game_state)
        #gui.update(game_state)
        #gui.draw()

        # now get user actions
        gui.execute_actions() # execute events and store messages in internal structures
        #net.send(['CYCLE'])
        requests = gui.requests() # query message structures to see what requests users have made
        for request in requests:
        #    # if you quit you'd like to perhaps be able to reconnect...
        #    # also we'll let people manually quit
            if request == 'QUIT':
                running = False
                pygame.quit() # not sure if your pygame stuff is gonna work properly
            else:
                net.send(request)
        gui.draw()

if __name__ == "__main__":
    main()