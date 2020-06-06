# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server

# this game will have a simple gui where you see your cards and whats on the table
# packets sent and recieved will be encrypted
# it will have basic timers to make sure people don't take too long
# and it will have a simple installer to install python and the necessary dependencies on mac, windows, or linux


# TODO remove
import random

from tute import Suits
from gui import CardSprite, PlayerSprites
from network import Network

############################ KEY GRAPHICS FUNCTIONALITY ###################
# TODO move this to tute and then part is used by client part is used by server
def draw(window, color):
    window.fill(color)
    pygame.display.update()

###################### KEY GAMEPLAY FUNCTIONALITY ######################

# higher numbers mean that card will win
# there are 12 cards per face/suit
card_type_order = {
    'A':11,
    '3':10,
    'R':9,
    'C':8,
    'S':7,
    '9':6,
    '8':5,
    '7':4,
    '6':3,
    '5':2,
    '4':1,
    '3':0,
}

# more efficient way to generate exists lol
use_keycodes = {
    '1':0,
    '2':1,
    '3':2,
    '4':3,
    '5':4,
    '6':5,
    '7':6,
    '8':7,
    '9':8,
    '10':9,
    '11':10,
    '12':11,
}
reveal_keycodes = {
    'q':0,
    'w':1,
    'e':2,
    'r':3,
    't':4,
    'y':5,
    'u':6,
    'i':7,
    'o':8,
    'p':9,
    '[':10,
    ']':11,
}

def main(client_id=0):
    player_sp = PlayerSprites()
    net = Network()

    running = True
    while running:
        for event in pygame.event.get():
            # user can quit just by closing the window
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                net.quit()
                pygame.quit()
            
            # we set it up for testing so that if you set up a space-bar you send a request
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                net.send("request from client with id {}".format(str(client_id)))
            elif event.type == pygame.KEYDOWN:
                pass
        
        # draw the empty board
        draw(window, COLOR_WHITE)
        # draw all the cards that I own plus other helpful ones
        player_sp.display(window)
        # update
        pygame.display.update()

# main
if __name__ == "__main__":
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("client")
    main(client_id=0)