"""
As of June 4th 2020 we are making an MVP. This means it has to work and be the easiest implementation for me possible.
However, I intend to have graphics.

This will be the control scheme: 1-n (if you have n cards) will deploy card x if you press key x (if n is mod 10 then - then =)
On the right it will show card codes for the cards you have acquired (in text), for others it will display 
the number of cards they have acquired. It will only let you play cards that are legal (by remembering
the face and value of last one and face for the game, might actually not do this yet)
In the middle it will display all cards from LEFT TO RIGHT and decide the winner
Card codes:
type_face where face is either B (bastos), C (copas), E (espadas), or O (oros) and type is:
A for ace, R for rey, C for caballo, S for sota and numbers for the rest
players will count their points up at the end each and tell the server (this can be commandline or something)
To sing the 40s or 20s they can reveal cards to reveal cards they can press q,w,e,r,...[,] (under the numbers)
they press again to hide (they'll have to keep track of their points)

ex for cards:
A_B is the ace of bastos
R_O is the king of oros
3_E is the 3 of espadas
7_C is the 7 of copas (no vale nada)


SPACE BAR WILL BE USED TO CHANGE STATE

MVP HAS NO SECURITY CONSIDERATIONS...
IN THE FUTURE WE WILL HAVE TO ENCRYPT USING OPENSSL ETC...
"""

# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server

# this game will have a simple gui where you see your cards and whats on the table
# packets sent and recieved will be encrypted
# it will have basic timers to make sure people don't take too long
# and it will have a simple installer to install python and the necessary dependencies on mac, windows, or linux


# TODO make code a bit cleaner and go make server do the logic
import pygame
import random

from structs import Suits
from network import Network

############################ KEY GRAPHICS FUNCTIONALITY ###################

WIDTH = 1280
HEIGHT = 720
COLOR_WHITE = (255, 255, 255)

CARD_WIDTH = int(201/1.5)
CARD_HEIGHT = int(279/1.5)

class CardSprite:
    # suits that are possible in Tute are: bastos, copas, espadas, oros
    # for more generality add width and hegiht options
    def __init__(self, value, suit, width=CARD_WIDTH, height=CARD_HEIGHT, theta=None, back=False, x=None, y=None):
        self.value = value
        assert value is None or type(value) == int # for aux none
        self.suit = suit
        assert suit is None or type(suit) == Suits # for aux none

        # positional and type information
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.back = back

        if not (self.value is None and self.suit is None):
            self.front_image = pygame.image.load("./cartas-españolas/"+str(self.suit.value)+"_"+str(self.value)+".jpg")
            self.front_image = pygame.transform.scale(self.front_image, (self.width, self.height))
        else:
            self.front_image = None
        
        self.back_image = pygame.image.load("./cartas-españolas/back.jpg")
        self.back_image = pygame.transform.scale(self.back_image, (self.width, self.height))

        if theta is not None:
            if not (self.value is None and self.suit is None):
                self.front_image = pygame.transform.rotate(self.front_image, theta)
            self.back_image = pygame.transform.rotate(self.back_image, theta)
    
    def is_ace(self):
        return self.value == 1

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value and self.suit == other.suit
    
    def display(self, window): # if None and None then will bitch about needing initialization
        if not self.back:
            window.blit(self.front_image, (self.x, self.y)) 
        else:
            window.blit(self.back_image, (self.x, self.y)) 

# we will call the suit "card" as a card though its just the suit symbol
class PlayerSprites:
    def __init__(self):
        # how many cards each player has
        self.hand_size = 12
        # their card backs
        self.aux = [
            CardSprite(None, None, theta=90, back=True), # right
            CardSprite(None, None, theta=180, back=True), # top
            CardSprite(None, None, theta=270, back=True), # left
            ]
        # where their card backs will be
        self.aux_locs = [
            (WIDTH//2 - CARD_WIDTH//2, 0), 
            (0, HEIGHT//2 - CARD_WIDTH//2), 
            (WIDTH - CARD_HEIGHT, HEIGHT//2 - CARD_WIDTH//2),
        ]
        # where the cards will be positioned for me
        self.starting_x = 0
        self.starting_y = HEIGHT - CARD_HEIGHT
        # make my cards and their cards
        self.make_board()
    
    # creates a shuffled deck
    # temporary since the server will be doing this later
    def generate_cards(self):
        cards =[CardSprite(i,j) for i in range(1,13) for j in Suits]
        random.shuffle(cards)
        return cards[:self.hand_size]

    def make_board(self):
        self.my_cards = self.generate_cards()
        for i in range(self.hand_size):
            self.my_cards[i].x = self.starting_x + (self.my_cards[i].width//2) * i # they will overlap by half
            self.my_cards[i].y = self.starting_y # they all will have the same y since they are in the bottom showwing
        
        for i in range(3):
            self.aux[i].x , self.aux[i].y = self.aux_locs[i]

    def display(self, window):
        for card in self.my_cards:
            card.display(window)
        for card in self.aux:
            card.display(window)

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

# return if the first (challenger) is > defender
# format is as defined above
# game_face is the face we are using in the game
# return None if neither wins (we'll let the first player instead in that case)
def compare_key_strings(challenger, defender, game_face, round_face):
    val1, face1 = challenger.split("_")
    val2, face2 = defender.split("_")
    if face1 == face2:
        assert val1 != val2 # whoopsies
        return card_type_order[face1] > card_type_order[face2]
    elif face1 == game_face and face2 != game_face:
        return True # challenger win
    elif face2 == game_face and face1 != game_face:
        return False # defender win
    elif face1 == round_face and face2 != round_face:
        return True # challenger win
    elif face2 == round_face and face1 != round_face:
        return False # defender win
    else:
        # neither is game_face and neither is round_face so we will return none
        # in practice this will never be returned as you'll see below
        # in this case the first card down wins
        return None

# will go from card 0 (first placed) to card n (of length n card_list) (last placed) and return the index
# for the card that wins
def get_winner(card_list, game_face, round_face):
    assert len(card_list) > 0
    winner = 0
    for i in range(1,len(card_list)):
        if compare_key_strings(card_list[i], card_list[winner], game_face, round_face):
            winner = i
    return i

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