import json #LMAO
from tute import deserialize, default_game_state
from gui import Interface
from network import Channel
import threading

GAME_STATE = None

def listening(gui, net):
    global GAME_STATE
    while True:
        GAME_STATE = json.loads(net.listen())

def main():
    global GAME_STATE

    # onboard the network parameters
    print('Please enter the server\'s IP and port')
    server_ip = '10.0.0.211'#input() # TODO
    server_port = 5555#int(input())
    print('Please enter your username')
    player_id = input()

    GAME_STATE = default_game_state()
    #print(GAME_STATE)

    net = Channel(server_ip, server_port, player_id)
    gui = Interface(player_id, GAME_STATE)

    listener = threading.Thread(target=listening,args=(gui,net))
    listener.start()

    #action_boy = threading.Thread()
    #action_boy.start()

    running = True
    while running:
        # see what the game state is and update our look

        #print(GAME_STATE)
        if 'to play' in GAME_STATE:
            print('to play ', GAME_STATE['to play'])
        else:
            print('waiting to play')


        gui.update(GAME_STATE)
        #print("...")
        #print(game_state)
        #gui.update(game_state)
        #gui.draw()

        # now get user actions
        gui.execute_actions() # execute events and store messages in internal structures
        #net.send(['CYCLE'])
        request = gui.request
        if request is not None:
            if request == 'QUIT':
                running = False
                listener.join(1.0)
            else:
                if request == 'CYCLE':
                    print('sending cycle request')
                net.send(request)
                gui.request = None
        gui.draw()

if __name__ == "__main__":
    main()