# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server

# this game will have a simple gui where you see your cards and whats on the table
# packets sent and recieved will be encrypted
# it will have basic timers to make sure people don't take too long
# and it will have a simple installer to install python and the necessary dependencies on mac, windows, or linux

from tute import deserialize
from gui import GUI
from network import Channel

def main():
    # onboard the network parameters
    print('Please enter your IP Address.')
    ip = input()
    print('Please enter 5555.')
    port = input()

    net = Channel(server_ip, server_port)
    gui = Interface()

    running = True
    while running:
        # see what the game state is and update our look
        game_state = net.message()
        gui.update(game_state)
        gui.draw()

        # now get user actions
        gui.execute() # execute events and store messages in internal structures
        requests = gui.requests() # query message structures to see what requests users have made
        for request in requests:
            # if you quit you'd like to perhaps be able to reconnect...
            # also we'll let people manually quit
            if request == 'QUIT':
                running = False
                pygame.quit() # not sure if your pygame stuff is gonna work properly
            else:
                net.send(request)

if __name__ == "__main__":
    main()