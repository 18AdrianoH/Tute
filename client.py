# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server

# this game will have a simple gui where you see your cards and whats on the table
# packets sent and recieved will be encrypted
# it will have basic timers to make sure people don't take too long
# and it will have a simple installer to install python and the necessary dependencies on mac, windows, or linux

import pygame
import random

from structs import Suits
from network import Network

WIDTH = 1280
HEIGHT = 720
COLOR_WHITE = (255, 255, 255)

CARD_WIDTH = int(201/1.5)
CARD_HEIGHT = int(279/1.5)

# default images for the rotated card backs that we will show for other players
CARD_BACK_LEFT_IMG = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("./cartas-españolas/back.jpg"), (CARD_WIDTH, CARD_HEIGHT)),270)
CARD_BACK_TOP_IMG = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("./cartas-españolas/back.jpg"), (CARD_WIDTH, CARD_HEIGHT)),180)
CARD_BACK_RIGHT_IMG = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("./cartas-españolas/back.jpg"), (CARD_WIDTH, CARD_HEIGHT)),90)

class CardSprite:
    # suits that are possible in Tute are: bastos, copas, espadas, oros
    # for more generality add width and hegiht options
    def __init__(self, value, suit, x=None, y=None):
        self.value = value
        assert type(value) == int
        self.suit = suit
        assert type(suit) == Suits

        self.front_image = pygame.image.load("./cartas-españolas/"+str(self.suit.value)+"_"+str(self.value)+".jpg")
        self.back_image = pygame.image.load("./cartas-españolas/back.jpg")

        self.front_image = pygame.transform.scale(self.front_image, (CARD_WIDTH, CARD_HEIGHT))
        self.back_image = pygame.transform.scale(self.back_image, (CARD_WIDTH, CARD_HEIGHT))

        self.x = x
        self.y = y
    
    def is_ace(self):
        return self.value == 1

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value and self.suit == other.suit
    
    def display_front(self, window): # if None and None then will bitch about needing initialization
        window.blit(self.front_image, (self.x, self.y)) 

def draw(window, color):
    window.fill(color)
    pygame.display.update()

def main(client_id=0):
    hand_size = 12
    starting_x = 0
    starting_y = HEIGHT - CARD_HEIGHT

    left_back_x = WIDTH//2 - CARD_WIDTH//2
    left_back_y = 0
    top_back_x = 0
    top_back_y = HEIGHT//2 - CARD_WIDTH//2
    right_back_x = WIDTH - CARD_HEIGHT
    right_back_y = HEIGHT//2 - CARD_WIDTH//2

    cards = [CardSprite(i,j) for i in range(1,13) for j in Suits]
    random.shuffle(cards)

    my_cards = cards[:hand_size] # take the first 12 cards for myself
    for i in range(hand_size):
        my_cards[i].x = starting_x + (CARD_WIDTH//2) * i # they will overlap by half
        my_cards[i].y = starting_y # they all will have the same y since they are in the bottom showwing
    
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
        
        # draw the empty board
        draw(window, COLOR_WHITE)

        # draw my cards faceup so I know what I have
        for card in my_cards:
            card.display_front(window)

        # display their placeholder cards that show they have cards still
        window.blit(CARD_BACK_LEFT_IMG, (left_back_x, left_back_y))
        window.blit(CARD_BACK_TOP_IMG, (top_back_x, top_back_y))
        window.blit(CARD_BACK_RIGHT_IMG, (right_back_x, right_back_y))

        # update
        pygame.display.update()

# main
if __name__ == "__main__":
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("client")
    main(client_id=0)