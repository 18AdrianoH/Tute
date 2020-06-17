### this translates interactions on the gui to game state and game state to gui look
# basically it is the engine behind the tute game visualization
# below I have a comment that gives you a rough ascii sketch of what this will look like

import pygame
import random # TODO remove, this is done by the server

# TODO we have to display their look somewhere

# we will use hitboxes and mouse clicks
# a left mouse click plays the card
# a right mouse click reveals the card
"""
    .__.
    |__|  | | | | | | | | | | | |
     #                             .__.
                                 # |__|
——                                  ——
——                                  ——
——                                  ——
——                                  ——
——     _1_  _2_  _3_  _4_  P        ——
——                                  ——
——                                  ——
——                                  ——
——                                  ——
——                                  ——
——                                  ——
——                                  ——
.__.
|__|  #                       
                              #
                             .__.
    | | | | | | | | | | | |  |__|
"""

# constants pertaining to our files and stuff
COLOR_WHITE = (255, 255, 255)
CARD_WIDTH_TO_HEIGHT_RATIO = 201.0/279.0 # this is width/height

#################### Sprite Types and Graphics Helpers ####################
# A dummy card sprite can have None as its 'card' or we can just put a placeholder
# This card is also used for hitbox detection
class Card:
    # suits that are possible in Tute are: bastos, copas, espadas, oros
    # for more generality add width and hegiht options
    def __init__(self, card, width, height, rotation, back, x, y):
        # type of card
        self.value = value, self.suit = card.split('_')
        self.card = card

        # positional information
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # show style information
        self.back = back
        self.rotation = rotation if rotation is not None else 0 # angle counterclockwise as usual
        self.front_image = None
        self.back_image = None

        # load image information
        if not self.back:
            self.front_image = pygame.image.load('./cartas-españolas/'+self.value+'_'+self.suit+'.jpg')
            self.front_image = pygame.transform.scale(self.front_image, (self.width, self.height))
        else:
            self.back_image = pygame.image.load('./cartas-españolas/back.jpg')
            self.back_image = pygame.transform.scale(self.back_image, (self.width, self.height))

        if rotation > 0:
            if not self.back:
                self.front_image = pygame.transform.rotate(self.front_image, theta)
            else:
                self.back_image = pygame.transform.rotate(self.back_image, theta)
    
    # display information
    def display(self, window):
        if not self.back:
            window.blit(self.front_image, (self.x, self.y)) 
        else:
            window.blit(self.back_image, (self.x, self.y))
    
    # for this just remember that the coordinate system increments as you go down, not up
    def contains_point(self, x, y):
        left = self.x
        top = self.y
        bot = self.y + self.height
        right = self.x + self.width

        return left <= x and x <= right and top <= y and y <= bot

# player_sprites encapsulates all the sprites that a single player has
class PlayerSprites:
    def __init__(self, cards, won_cards, screen_width, screen_height, main_player, rot):
        self.cards = self.init_card_sprites(cards)
        self.won_cards = won_cards

        self.screen_height = screen_height
        self.screen_width = screen_width
        # determine screen height and width here
        
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
        for card in self.cards:
            card.display(window)
        for card in self.won_cards:
            card.display(window)

# this encapsulates all of the players' cards
# 
class Sprites:
    pass
#################### Orchestration for Graphics Below ####################

"""
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
"""

# will display a pygame game and return messages based on in user input
# it takes in game state and uses that to display and returns messages
class Interface:
    def __init__(self, player_id):
        self.player = player_id
        self.requests = []

        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.WIDTH, self.HEIGHT = pygame.display.get_surface().get_size()


        pygame.display.set_caption('client')

        self.action_state = 'WAITING'

        # realistically you'd want something like a quad-tree or search trees
        self.hitboxes = {}

    ########## Key Graphics Functionality ##########
    def update(self, game_json):
        pass            
    
    def draw(self, color):
        self.window.fill(color)
        pygame.display.update()
    
    ########## Key Action Functionality Below ##########

    # QUIT
    # 'PLAY-SELECT'
    # 'REVEAL-SELECT'
    # 'PLAY'
    # 'REVEAL'
    # 'CYCLE'
    # 'WAITING'

    # return one of above in that order (i.e. if you play and reveal then you are playing)
    # this will return the next state to go to in actions
    # and any important data in a tuple (state, data)
    # will return None if there is no action need be taken
    def get_action(events):
        for event in events:
            if event.type == pygame.QUIT or event.type == pygame.KEYUP and event.key = K_q:
                return ('QUIT', )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # left mid right scrollup scrolldown
                left, _, right, _, _ = pygame.mouse.get_pressed()
                if self.action_state == 'WAITING':
                    pos = pygame.mouse.get_pos()
                    if left and right:
                        # can't do both
                        return None
                    elif left:
                        return ('PLAY-SELECT', pos)
                    elif right:
                        return ('REVEAL-SELECT', pos)
                else:
                    # clicked too fast somewhere so was in another state
                    return None
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if self.action_state == 'PLAY-SELECT':
                    # pos technically not necessary since we got that before
                    return ('PLAY', pos)
                elif self.action_state == 'REVEAL-SELECT':
                    return ('REVEAL', pos)
                else:
                    # no change of state
                    return None
            # since we only have one spacebar it's fine to just do keyup
            elif event.type == pygame.KEYUP and event.key == K_SPACE:
                if self.action_state == 'WAITING':
                    return ('CYCLE', )
                else:
                    return None
        return None # no action taken

    def execute_action(self):
        # this implementation insures that one event happens per execute cycle
        actions = get_action(pygame.event.get())

        if actions is None:
            return # do nothing
        # else
        state, data = actions

        if state == 'QUIT':
            running = False
            pygame.display.quit()
            net.quit()
            pygame.quit()
        elif state == 'PLAY':
            self.execute_play()
        elif state == 'REVEAL':
            self.execute_reveal()
        elif state == 'CYCLE':
            self.execute_cycle()

        # if we are going to a select state then we do nothing since those are just there to insure
        # that we dont do multiple actions faster than we can see by mouse down repeatedly
    
    # these are the functions that figure out 

    def execute_reveal(self):
        pass

    def execute_play(self):
        play_string = ''
        card = ''
        requests.append(play_string)

    # lol this is a simple one 
    def execute_cycle(self):
        requests.append('CYCLE')
    
    def messages(self):
        return self.messages