### this translates interactions on the gui to game state and game state to gui look
# basically it is the engine behind the tute game visualization
# below I have a comment that gives you a rough ascii sketch of what this will look like

import pygame

pygame.font.init() # don't want to init all of python because that wants to read my keystrokes

# TODO display play order, players, game suit
from tute import Tute, to_dict # TODO remove this, it's only for testing
from tute import SUITS
from tute import VALUES

# we will use hitboxes and mouse clicks
# a left mouse click plays the card
# a right mouse click reveals the card

# interesting thing to note is that if you draw the last things drawn are on the top
# so basically we might have to think about that in some cases maybe?
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

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 840

EPSILON = 10

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0,0,0)
CARD_HEIGHT_TO_WIDTH_RATIO = 279.0/201.0 # this is width/height
CARD_WIDTHS_PER_SCREEN = 14
CARD_DENSITY = 2 # 1/CARD_DENSITY is how much we show of each card
INVERSE_CENTER_X = 2
INVERSE_CENTER_Y = 2
SUIT_HW = 80

# you would literally not believe how much this speeds everything up
# loading images (especially the back is a huge fucking bottleneck)
BACK_IMAGE = pygame.image.load('./cartas-españolas/back.jpg')
GET_IMAGE = {
    val + '_' + st : pygame.image.load('./cartas-españolas/'+val+'_'+st+'.jpg') for val in VALUES for st in SUITS
    }
SUIT_IMAGE = {
    'O':pygame.image.load('./cartas-españolas/oros.jpg'),
    'E':pygame.image.load('./cartas-españolas/espadas.jpg'),
    'B':pygame.image.load('./cartas-españolas/bastos.jpg'),
    'C':pygame.image.load('./cartas-españolas/copas.jpg'),
}

#################### Sprite Types and Graphics Helpers ####################
# A dummy card sprite can have None as its 'card' or we can just put a placeholder
# This card is also used for hitbox detection
# Rotation is (front, back)
class CardSprite:
    # suits that are possible in Tute are: bastos, copas, espadas, oros
    # for more generality add width and height options
    # only supports rotations that are 0, 90, 180, 270
    def __init__(self, card, width, height, rotation, x, y, back):
        # type of card
        self.value, self.suit = card.split('_')
        self.card = card

        # positional information
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # show style information
        self.back = back
        self.rotation_front, self.rotation_back = rotation
        self.front_image = None
        self.back_image = None

        # load image information
        self.front_image = GET_IMAGE[card]
        self.front_image = pygame.transform.scale(self.front_image, (self.width, self.height))

        self.back_image = BACK_IMAGE
        self.back_image = pygame.transform.scale(self.back_image, (self.width, self.height))

        self.front_image = pygame.transform.rotate(self.front_image, self.rotation_front)
        self.back_image = pygame.transform.rotate(self.back_image, self.rotation_back)
        #print('LOADED')
    
    # move it to a tuple for x and y
    def move(self, xy):
        self.x, self.y = xy
    # get the location tuple
    def loc(self):
        return self.x, self.y

    # display information
    def display(self, window):
        if not self.back:
            window.blit(self.front_image, (self.x, self.y)) 
        else:
            window.blit(self.back_image, (self.x, self.y))
    
    # for this just remember that the coordinate system increments as you go down, not up
    def contains_point(self, x, y):
        # declare some temp variables we will use
        left = self.x
        top = self.y
        bot = self.y + self.height
        right = self.x + self.width
        
        # ignore rotation since we've dealt with that in the init
        # every time we need to rotate we'll update

        return left <= x and x <= right and top <= y and y <= bot

# player_sprites encapsulates all the sprites that a single player has
# type tells you wether they are top, bottom, left, or right
# 'TOP', 'PLAYER', 'LEFT', 'RIGHT' (player is always bottom, but their cards are revealed by default)
# player = 0, 0, right = 0, 90, top = 0, 180, left = 0, 270

class PlayerSprites:
    def __init__(self, cards, screen_width, screen_height, type, player_id):
        self.player_id = player_id

        self.type = type
        self.screen_height = screen_height
        self.screen_width = screen_width

        # these are initialized below
        # these refer to PRE-ROTATION (this is important!)
        # real refers to hitbox, otherwise it refers to the card's inherent properties
        self.card_height = None
        self.card_width = None
        self.real_width = None
        self.real_height = None

        self.start_position = None # kinda necessary for subsequent additions

        # initialize the cards
        self.rotation = (0,0)
        self.init_rotation()

        self.cards = cards
        self.won_cards = [] # lul
        
        self.card_sprites = []
        self.init_card_sprites(cards) # now they are not None
        self.won_card_sprites = [] # lol it starts empty

        # who's who?
        self.font = pygame.font.Font('freesansbold.ttf', 20) 
        self.id_text = self.font.render(player_id, True, COLOR_BLACK) 
        self.id_text_rect = self.id_text.get_rect()
        idx, idy = self.start_position
        if self.type == 'PLAYER':
            idx += int((14/CARD_DENSITY * self.card_width) + EPSILON)
            idy = self.screen_height - 3* EPSILON
        elif self.type == 'RIGHT':
            idx = 1300 # LMAO
            idy = 152
        elif self.type == 'TOP':
            idx = 2 * self.card_height + 25 * EPSILON
            idy = 7 * EPSILON #int((16/CARD_DENSITY * self.card_width) + EPSILON)
        else:
            idx = 10 * EPSILON
            idy = 676
        self.id_text_rect.center = (
            idx,
            idy
        )

    # initialization helper functionality
    def init_rotation(self):
        if self.type == 'PLAYER':
            self.rotation = (0, 0)
        elif self.type == 'RIGHT':
            self.rotation =  (90, 90)
        elif self.type == 'TOP':
            self.rotation = (0, 180)
        else:
            self.rotation = (270, 270)

    # remember to use correctly rotated forms
    def init_card_dims(self):
        # obviously this is an approximation but should be good enough
        self.card_width = self.screen_width / CARD_WIDTHS_PER_SCREEN
        self.card_height = CARD_HEIGHT_TO_WIDTH_RATIO * self.card_width
        self.card_width = int(self.card_width)
        self.card_height = int(self.card_height)

        if self.type == 'PLAYER' or self.type == 'TOP':
            self.real_width = self.card_width 
            self.real_height = self.card_height
        else:
            self.real_width = self.card_height 
            self.real_height = self.card_width

    def init_card_sprites(self, cards):
        # decide on the width/height of cards
        self.init_card_dims()

        # you get your leftmost corner looking towards the center
        # remember that the sideways ones have width as its height
        if self.type == 'PLAYER':
            # offset with card_width avoids collision with left
            self.start_position = (self.card_height, self.screen_height - self.card_height)
        elif self.type == 'RIGHT':
            self.start_position = (self.screen_width - self.card_height, self.screen_height - self.card_width)
        elif self.type == 'TOP':
            # last card_height is to avoid collision with right
            self.start_position = (self.screen_width - self.card_width - self.card_height, 0)
        else:
            self.start_position = (0,0)
        
        self.update_cards(cards, [])

    # it will regenerate the whole graphics shit
    def update_cards(self, cards, revealed_cards):
        self.cards = cards
        self.card_sprites = []

        # temporary helper variables
        startx, starty = self.start_position

        offset = int(self.card_width / CARD_DENSITY)

        # len(cards) = 12 at the start
        for i in range(0, len(cards), 1):
            x_pos, y_pos = None, None
            card = cards[i]

            rev = card in revealed_cards
            back = not rev

            if self.type == 'PLAYER':
                back = False
                x_pos = i * offset+ startx # go right so positive
                y_pos = starty
                if rev:
                    y_pos -= EPSILON # so that we can get some responsiveness
            elif self.type == 'RIGHT':
                x_pos = startx
                y_pos = -1 * i * offset + starty # go up so negative
            elif self.type == 'TOP':
                x_pos = -1 * i * offset + startx # go left so negative
                y_pos = starty
            elif self.type == 'LEFT':
                x_pos = startx
                y_pos = i * offset + starty # go down so positive
            
            #print(f'display card {card} at {x_pos}, {y_pos}, from type {self.type}')
            self.card_sprites.append(
                CardSprite(
                    card, 
                    self.card_width, 
                    self.card_height, 
                    self.rotation, 
                    x_pos,
                    y_pos,
                    back
                    )
                )
    # this is very similar to above, it's just shifted up
    def update_won_cards(self, won_cards, revealed_cards):
        self.won_cards = won_cards
        self.won_card_sprites = []

        start_x, start_y = self.start_position
        if self.type == 'PLAYER':
            start_y -= self.real_height # your won cards display above your play cards
        elif self.type == 'RIGHT':
            start_x -= self.real_width # for them its on the left
        elif self.type == 'TOP':
            # we'll display for 'them' not for 'you'
            start_y += self.real_height # for them its on the bottom
        elif self.type == 'LEFT':
            start_x += self.real_width # for them its on the right (duh)

        offset = int(self.card_width / CARD_DENSITY)

        for i in range(0, len(won_cards), 1):
            x_pos, y_pos = None, None
            card = won_cards[i]

            revealed = card in revealed_cards
            back = not revealed

            if self.type == 'PLAYER':
                back = False
                x_pos = i * offset + start_x
                y_pos = -1 * EPSILON  + start_y # up epsilon to allow for a little bit of responsiveness when u reveal
                if revealed:
                    y_pos -= EPSILON # to show others that we are revealing
            elif self.type == 'RIGHT':
                x_pos = start_x
                y_pos = i * offset * -1 + start_y
            elif self.type == 'TOP':
                # we'll display for 'them' not for 'you'
                x_pos = i * offset * -1 + start_x # remember we start on the right
                y_pos = start_y
            elif self.type == 'LEFT':
                x_pos = start_x 
                y_pos = i * offset + start_y
            
            #print(f'display won card {card} at {x_pos}, {y_pos}, from type {self.type}')
            self.won_card_sprites.append(
                CardSprite(
                    card, 
                    self.card_width, 
                    self.card_height, 
                    self.rotation,
                    x_pos,
                    y_pos,
                    back
                    )
            )

    def update(self, cards, won_cards, revealed_cards, revealed_won_cards):
        self.update_cards(cards, revealed_cards)
        self.update_won_cards(won_cards, revealed_won_cards)

    # display functionality
    # note how it displays in order
    # also note how the card_sprites are added to display in order previously
    def display(self, window):
        for cardsp in self.card_sprites:
            cardsp.display(window)
        for cardsp in self.won_card_sprites:
            cardsp.display(window)
        
        window.blit(self.id_text, self.id_text_rect)

# this encapsulates all of the players' cards
# this handles basically all sprites in the game
# there is no text in the game (because you can see all the cards)
class Sprites:
    def __init__(self, player_cards, player_order, player_id, screen_width, screen_height, game_suit, to_play):
        self.player_id = player_id

        self.screen_width = screen_width
        self.screen_height = screen_height

        # lol copy paste because I forgot to add center the first time around
        self.center_card_width = self.screen_width / CARD_WIDTHS_PER_SCREEN
        self.center_card_height = CARD_HEIGHT_TO_WIDTH_RATIO * self.center_card_width
        self.center_card_width = int(self.center_card_width)
        self.center_card_height = int(self.center_card_height)

        # so people know the suit
        self.suit_img = SUIT_IMAGE[game_suit]
        self.suit_x = x_i = int(self.screen_width / INVERSE_CENTER_X) - self.center_card_width - SUIT_HW
        self.suit_y = y_i = int(self.screen_height / INVERSE_CENTER_Y) - SUIT_HW # same as center
        self.suit_img = pygame.transform.scale(self.suit_img, (SUIT_HW, SUIT_HW))

        # who is to play? (LOL WE SHOULD REUSE THE LOCATION STUFF WTF)
        self.font = pygame.font.Font('freesansbold.ttf', 20) 
        player_order_str = ','.join(player_order)
        self.text = self.font.render('Siguiente:'+to_play + ', orden:' + player_order_str, True, COLOR_BLACK) 
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (
            int(self.screen_width / INVERSE_CENTER_X) - self.center_card_width - 2*SUIT_HW,
            int(self.screen_height / INVERSE_CENTER_Y) + 2 * EPSILON # further down!
        )

        # who's who is in PlayerSprites because it belongs to the player type

        self.types = ['PLAYER', 'RIGHT', 'TOP', 'LEFT']

        # order is bot, right, top, left
        self.player_sprites = []

        self.center_sprites = []

        #print(player_order)
        index = 0
        while player_order[index] != player_id:
            index += 1
        
        for i in range(4):
            self.player_sprites.append(
                PlayerSprites(
                    player_cards[player_order[index]],
                    self.screen_width,
                    self.screen_height,
                    self.types[i],
                    player_order[index]
                    )
                )
            index = (index + 1) % len(player_order)

        self.bot_player_sprites, self.right_player_sprites, self.top_player_sprites, self.left_player_sprites = \
            self.player_sprites
    
    def display(self, window):
        for player_sprites in self.player_sprites:
            player_sprites.display(window)
        
        for sprite in self.center_sprites:
            sprite.display(window)
        
        window.blit(self.suit_img, (self.suit_x, self.suit_y))
        window.blit(self.text, self.text_rect)
    
    # we only react to cards clicked if they are ours (we don't get to choose what to do with others' cards)
    def card_clicked(self, xy):
        x, y = xy
        cs = self.bot_player_sprites.card_sprites
        css = self.bot_player_sprites.won_card_sprites
        # why go backwards? hitboxes. (this is the shittiest least mantainable crap ive ever done lol)
        for i in range(len(cs)-1, -1, -1):
            csp = cs[i]
            if csp.contains_point(x, y):
                return csp.card
        for i in range(len(css)-1, -1, -1):
            csp = css[i]
            if csp.contains_point(x, y):
                return csp.card
        # no card found
        return None
    
    def update(self, game_state):
        # patch because of mistakes made
        revealed_cards = set()
        revealed_won_cards = set()

        for id in game_state['player order']:
            for card,rev in game_state['revealed cards'][id].items():
                if rev == True:
                    revealed_cards.add(card)
            for card,rev in game_state['revealed won cards'][id].items():
                if rev == True:
                    revealed_won_cards.add(card)
        
        player_order_str = ','.join(game_state['player order'])
        self.text = self.font.render('Siguiente:' + game_state['to play'] + ', orden:' + player_order_str, True, COLOR_BLACK)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (
            int(self.screen_width / INVERSE_CENTER_X) - self.center_card_width - SUIT_HW,
            int(self.screen_height / INVERSE_CENTER_Y) + 2 * EPSILON # further down!
        )
        
        #print(revealed_cards, revealed_won_cards)# seems to be working

        for ob in self.player_sprites:
            ob.update(
                game_state['players cards'][ob.player_id],
                game_state['won cards'][ob.player_id], 
                revealed_cards, 
                revealed_won_cards
                )

        self.center_sprites = []
        i = 0
        center = game_state['center']
        x_i = int(self.screen_width / INVERSE_CENTER_X) - self.center_card_width
        y_i = int(self.screen_height / INVERSE_CENTER_Y) - self.center_card_height
        offset = int(self.center_card_width / CARD_DENSITY)
        while i < len(center) and center[i] is not None:
            if i > 0:
                x_i += offset # usual left to right action
            self.center_sprites.append(
                CardSprite(
                    center[i], 
                    self.center_card_width, 
                    self.center_card_height, 
                    (0,0), 
                    x_i,
                    y_i,
                    False
                    )
            )
            i += 1 # lmao I forgot this before

#################### Orchestration for Graphics Below ####################

# will display a pygame game and return messages based on in user input
# it takes in game state and uses that to display and returns messages
class Interface:
    def __init__(self, player_id, game_json):
        # constants pertaining to our files and stuff
        print('initializing Interface')

        self.player = player_id # who this interface is for
        self.game_state = game_json # what the game looks like right now
        self.request = None # latest request

        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tute Game Client Interface')
        print('Initialized... now waiting for state change to add sprites')

        self.screen_width, self.screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.sprites = None

        self.action_state = 'WAITING'

    ########## Key Graphics Functionality ##########
    def update(self, game_json):
        self.game_state = game_json

        if self.sprites is None and game_json['state'] != 'WAITING':
            # make sure spirites exist lmao
            self.sprites = Sprites(
                self.game_state['players cards'],
                self.game_state['player order'], 
                self.player, 
                self.screen_width, 
                self.screen_height,
                self.game_state['game suit'],
                self.game_state['to play']
            ) # sprites to show for this person
        if not self.sprites is None:
            #print('NOT NONE')
            self.sprites.update(self.game_state)
    
    def draw(self, color=COLOR_WHITE):
        self.window.fill(color)

        if not self.sprites is None:
            self.sprites.display(self.window)
        
        pygame.display.update()
    
    ########## Key Action Functionality Below ##########

    # 'QUIT'
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
    def get_action(self, events):
        for event in events:
            if event.type == pygame.QUIT or event.type == pygame.KEYUP and event.key == pygame.K_q:
                return ('QUIT', None)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # left mid right scrollup scrolldown
                #left, mid, right = pygame.mouse.get_pressed() # doesn't work
                button = event.button
                #print(button)
                if self.action_state == 'WAITING':
                    #print(button, event.button)
                    pos = pygame.mouse.get_pos()
                    print('clicked at ', str(pos))
                    if button == 1:
                        return ('PLAY-SELECT', pos)
                    elif button == 3:
                        return ('REVEAL-SELECT', pos)
                    else:
                        return None
                else:
                    # clicked too fast somewhere so was in another state
                    return None
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print('let go at ', str(pos))
                if self.action_state == 'PLAY-SELECT':
                    # pos technically not necessary since we got that before
                    return ('PLAY', pos)
                elif self.action_state == 'REVEAL-SELECT':
                    return ('REVEAL', pos)
                else:
                    # no change of state
                    return None
            # since we only have one spacebar it's fine to just do keyup
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                if self.action_state == 'WAITING':
                    return ('CYCLE', None)
                else:
                    return None
        return None # no action taken

    def execute_actions(self):
        # this implementation insures that one event happens per execute cycle
        action = self.get_action(pygame.event.get())

        if action is None:
            return # do nothing
        # else
        #print(action)
        state, data = action

        if state == 'QUIT':
            self.execute_quit()
        elif state == 'PLAY':
            self.execute_play(data)
        elif state == 'REVEAL':
            self.execute_reveal(data)
        elif state == 'CYCLE':
            self.execute_cycle()
        elif state == 'PLAY-SELECT':
            self.action_state = 'PLAY-SELECT'
        elif state == 'REVEAL-SELECT':
            self.action_state = 'REVEAL-SELECT'

        # if we are going to a select state then we do nothing since those are just there to insure
        # that we dont do multiple actions faster than we can see by mouse down repeatedly
    
    # these are the functions that figure out 
    def execute_quit(self):
        self.request = 'QUIT'
        state = 'QUIT'
        pygame.quit()

    def execute_reveal(self, coords):
        if not self.sprites is None:
            clicked = self.sprites.card_clicked(coords)
            if not clicked is None:
                play_string = 'REVEAL,' + clicked
                self.request = play_string
                #print('requesting a reveal')
        self.action_state = 'WAITING'

    def execute_play(self, coords):
        if not self.sprites is None:
            # card_clicked returns the string rep of the card
            clicked = self.sprites.card_clicked(coords)
            if not clicked is None and not clicked in self.game_state['won cards'][self.player]:
                play_string = 'PLAY,' + clicked
                self.request = play_string
        self.action_state = 'WAITING'

    # lol this is a simple one 
    def execute_cycle(self):
        #print('pubbed cycle request')
        self.request = 'CYCLE'
        self.action_state = 'WAITING'
## do note that a client reads from requests

# testing stuff below if it helps u
# if __name__ == '__main__':
#     print('demo')

#     # create our demo state
#     state_start = {'state' : 'WAITING'}
#     demo_state= {
#         'state' : 'ROUNDS',
#         'to play' : 'demodude',
#         'player order': ['demodude', '1', '2' , '3'],
#         'center' : ['A_C', 'A_B', 'A_O', None],
#         'players cards' : {
#             'demodude' : ['A_E', 'A_B'], 
#             '1' : ['A_E', 'A_B'],
#             '2' : ['A_E', 'A_B'],
#             '3' : ['A_E', 'A_B'],
#         },
#         'won cards' : {
#             'demodude' : ['A_E'], 
#             '1' : ['A_E'],
#             '2' : ['A_E'],
#             '3' : ['A_E'],
#         } ,
#         'revealed cards' : {
#             'demodude' : {
#                 'A_E' : False, 
#                 'A_B' : False,
#                 }, 
#             '1' : {
#                 'A_E' : False, 
#                 'A_B' : False,
#                 }, 
#             '2' : {
#                 'A_E' : False, 
#                 'A_B' : False,
#                 }, 
#             '3' : {
#                 'A_E' : False, 
#                 'A_B' : False,
#                 }, 
#         },
#         'revealed won cards' : {
#             'demodude' : {
#                 'A_E' : False, 
#                 }, 
#             '1' : {
#                 'A_E' : False, 
#                 }, 
#             '2' : {
#                 'A_E' : False, 
#                 }, 
#             '3' : {
#                 'A_E' : False, 
#                 }, 
#         },
#         'game suit' : 'O',
#         'to play' : 'demodude',
#     }

#     # a more realistic demo state
#     game = Tute()
#     game.add_player('demodude')
#     game.add_player('delia')
#     game.add_player('paula')
#     game.add_player('alejandro')
#     game.init_game()
#     game.increment_state() # starts the game (TODO might want to make automatic)

#     game.reveal_card('alejandro', game.player_cards['alejandro'][0])
#     #game.play_card('demodude', game.player_cards['demodude'][0])
#     game.increment_state()
#     state = to_dict(game)

#     print(state['player order'])

#     gui = Interface('demodude', state_start)
    
#     running = True
#     #it = 0
#     while running:
#         #it += 1
#         #print(it)
#         gui.execute_actions()

#         query = gui.request
#         gui.request = None # ready to take in a new query (don't repeat!)
#         if not query is None:
#             print(f'query is {query}')
#         if query == 'QUIT':
#             running = False
        
#         gui.update(state)
#         gui.draw()
#     print('finished')