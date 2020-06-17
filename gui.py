### this translates interactions on the gui to game state and game state to gui look
# basically it is the engine behind the tute game visualization
# below I have a comment that gives you a rough ascii sketch of what this will look like

import pygame

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

COLOR_WHITE = (255, 255, 255)
CARD_HEIGHT_TO_WIDTH_RATIO = 279.0/201.0 # this is width/height
CARD_WIDTHS_PER_SCREEN = 12
CARD_DENSITY = 2 # 1/CARD_DENSITY is how much we show of each card

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
        self.value = value, self.suit = card.split('_')
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
        self.front_image = pygame.image.load('./cartas-españolas/'+self.value+'_'+self.suit+'.jpg')
        self.front_image = pygame.transform.scale(self.front_image, (self.width, self.height))

        self.back_image = pygame.image.load('./cartas-españolas/back.jpg')
        self.back_image = pygame.transform.scale(self.back_image, (self.width, self.height))

        self.front_image = pygame.transform.rotate(self.front_image, self.rotation_front)
        self.back_image = pygame.transform.rotate(self.back_image, self.rotation_back)
    
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
    def __init__(self, cards screen_width, screen_height, type):
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

        # lul
        self.back = True if not self.type == 'PLAYER' else False

        # initialize the cards
        self.rotation = self.init_rotation()

        # TODO maybe delete this if they are not used
        self.cards = cards
        self.won_cards = [] # lul
        
        self.card_sprites = self.init_card_sprites(cards)
        self.won_card_sprites = [] # lol it starts empty

    # initialization helper functionality
    def init_rotation(self):
        return \
            (0, 0) if self.type == 'PLAYER' else \
            (90, 90) if self.type == 'RIGHT' else \
            (0, 180) if self.type == 'TOP' else \
            (270, 270) if self.type == 'LEFT'

    # remember to use correctly rotated forms
    def init_card_dims(self):
        # obviously this is an approximation but should be good enough
        self.card_width = self.screen_width / CARD_WIDTHS_PER_SCREEN
        self.card_height = CARD_HEIGHT_TO_WIDTH_RATIO * self.card_width
        self.card_width = int(self.card_width)
        self.card_height = int(self.card_height)

        self.real_width, self.real_height = \
            self.width, self.height if self.type == 'PLAYER' or self.type == 'TOP' else \
            self.height, self.width

    def init_card_sprites(self, cards):
        card_sprites = []

        # decide on the width/height of cards
        self.init_card_dims()

        # you get your leftmost corner looking towards the center
        # remember that the sideways ones have width as its height
        self.start_position = \
            (0, self.screen_height - self.card_height) if self.type == 'PLAYER' else \
            (self.screen_height - self.card_width, self.screen_width - self.card_height) if self.type == 'RIGHT' else \
            (self.screen_width - self.card_width, 0) if self.type == 'TOP' else \
            (0,0) if self.type == 'LEFT'
        
        # temporary helper variables
        startx, starty = start_position

        offset = int(self.card_width / CARD_DENSITY)

        # len(cards) = 12 at the start
        for i in range(0, len(cards), 1):
            x_pos, y_pos = None, None
            card = self.cards[i]

            if self.type == 'PLAYER':
                x_pos = i * offset+ startx # go right so positive
                y_pos = starty
            elif self.type == 'RIGHT':
                x_pos = startx
                y_pos = -1 * i * offset + starty # go up so negative
            elif self.type == 'TOP':
                x_pos = -1 * i * offset + startx # go left so negative
                y_pos = starty
            elif self.type == 'LEFT':
                x_pos = startx
                y_pos = i * offset + starty # go down so positive
            
            card_sprites.append(
                CardSprite(card, self.real_width, self.real_height, self.rotation, x_pos, y_pos, self.back)
                )

        return card_sprites

    # you'll be able to reveal on either and it does so by checking equality (will also hide if revealed)
    def toggle_reveal_card(self, card):
        for card_sprite in self.card_sprites:
            if card_sprite.card == card:
                card_sprite.back = not card_sprite.back
                return

    # note you never add to your cards or remove from your won cards
    def add_card_to_won(self, card):
        next_x, next_y = None, None
        offset = int(self.card_width / CARD_DENSITY)
        start_x, start_y = self.start_position

        if self.type == 'PLAYER':
            start_y -= self.real_height # your won cards display above your play cards
            next_x = len(self.won_card_sprites) * offset + start_x
            next_y = start_y
        elif self.type == 'RIGHT':
            start_x -= self.real_width # for them its on the left
            next_x = start_x
            next_y = len(self.won_card_sprites) * offset * -1 + start_y
        elif self.type == 'TOP':
            # we'll display for 'them' not for 'you'
            start_y += self.real_height # for them its on the bottom
            next_x = len(self.won_card_sprites) * offset * -1 + start_x # remember we start on the right
            next_y = start_y
        elif self.type == 'LEFT':
            start_x += self.real_width # for them its on the right (duh)
            next_x = start_x 
            next_y = len(self.won_card_sprites) * offset + start_y
        
        self.won_cards.append(card)
        self.won_card_sprites.append(
            CardSprite(card, self.real_width, self.real_height, self.rotation, next_x, next_y, self.back)
            )

    def remove_card_from_hand(self, card):
        self.cards.remove(card)
        i = 0
        while self.cards[i] != card:
            i+=1
        old = self.card_sprites.pop(i) # now i will be on the next card
        # now we need to shift all these to the left (or opposite direction lol)
        while i < len(self.card_sprites):
            # this should work no matter what type
            self.card_sprites[i].move(old.loc())
            old = self.card_sprites[i]

    # display functionality
    # note how it displays in order
    # also note how the card_sprites are added to display in order previously
    def display(self, window):
        for card in self.cards:
            card.display(window)
        for card in self.won_cards:
            card.display(window)

# this encapsulates all of the players' cards
# this handles basically all sprites in the game
# there is no text in the game (because you can see all the cards)
class Sprites:
    def __init__(self, player_cards, player_order, player_id, screen_width, screen_height):
        self.player_id = player_id

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.types = ['PLAYER', 'RIGHT', 'TOP', 'LEFT']

        # order is bot, right, top, left
        self.player_sprites = []

        index = 0
        while player_order[bot_index] != player_id:
            index += 1
        
        for i in range(4):
            self.left_player_sprites.append(
                PlayerSprites(
                    player_cards[player_order[index]],
                    self.screen_width,
                    self.screen_height,
                    type[i]
                    )
                )
            index = (index + 1) % len(player_order)

        self.bot_player_sprites, self.right_player_sprites, self.top_player_sprites, self.left_player_sprites = \
            self.player_sprites
    
    def display(self, window):
        for player_sprites in self.player_sprites:
            player_sprites.display(window)
    
    # we only react to cards clicked if they are ours (we don't get to choose what to do with others' cards)
    def card_clicked(self, x, y):
        for card_sprite in self.bot_player_sprites:
            if card_sprite.contains_point(x, y):
                return card_sprite.card
        # no card found
        return None

#################### Orchestration for Graphics Below ####################

# will display a pygame game and return messages based on in user input
# it takes in game state and uses that to display and returns messages
class Interface:
    def __init__(self, player_id, game_state):
        # constants pertaining to our files and stuff

        self.player = player_id
        self.sprites = Sprites(game_state, player_id)
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