import random
import json

########## Constants #########

SUITS = ('B', 'E', 'C', 'O')
VALUES = ('A', 'R', 'C', 'S', '9', '8', '7', '6', '5', '4', '3', '2')

CARD_ORDER = {'A' : 11,'3' : 10,'R' : 9,'C' : 8,'S' : 7,'9' : 6, '8' : 5, '7' : 4, '6' : 3, '5' : 2, '4' : 1, '2' : 0}
CARD_VALUE = {'A' : 11,'3' : 10,'R' : 4,'C' : 3,'S' : 2,'9' : 0, '8' : 0, '7' : 0, '6' : 0, '5' : 0, '4' : 0, '2' : 0}

# There are three basic states:
# WAITING (waiting for four players to connect)
# ROUNDS (waiting for a player to make a move, the game remembers)
# TERMINAL (game is over - all rounds have ended - waiting to command to start next game)

# Since this is a simple game cards are stored as strings with <value>_<suit>
# and also players are stored by <player_id>, a string
# and also states are stored as strings with the name above
## These methods are not thread safe! Pleae use locks externally.

########## Serialization code ##########

# return a dict representation of a tute game
# only serializes what will be necessary for users
# does not copy but instead uses aliasing (because json dumps doesn't have effects)
def to_dict(game):
    game_dict = {}
    # player whose turn it is (the one to play now)
    game_dict['state'] = game.state

    if game.state == 'WAITING':
        return game_dict
    # else

    # a lot of these will be none if the game just started
    game_dict['game suit'] = game.game_suit

    game_dict['to play'] = game.get_turn_player()
    game_dict['player order'] = game.player_order
    game_dict['center'] = game.center # be careful with None -> 'null' but decode should be ok

    game_dict['players cards'] = game.player_cards
    game_dict['won cards'] = game.player_won_cards

    game_dict['revealed cards'] = game.player_cards_state
    game_dict['revealed won cards'] = game.player_won_cards_state

    return game_dict
# serialize a game dict into bits to be sent
def serialize_dict(game_dict):
    return json.dumps(game_dict).encode('utf-8') # dumps returns a string
# deserializes to a dict
def deserialize(bits):
    return json.loads(bits) # can load from strings or bits
# general serializing for games
def serialize(game):
    return serialize_dict(to_dict(game))

# potentially useful to reconstruct game instances
#def from_dict(game)

class InvalidAction(Exception):
    pass # tried to do something not allowed
class InvalidState(Exception):
    pass # arrived somewhere impossible

########## Tute is a state machine version of a game ##########
class Tute:
    def __init__(self):
        self.state = 'WAITING'

        self.round_num = None # init when we start the game
        self.game_suit = None # init when we start the game
        self.round_suit = None # init when we start a round
        self.turn = None # init when we start a round
        self.player_order = []
        self.center = [None, None, None, None]

        #self.player_points = {}
        self.player_cards = {}
        self.player_cards_state = {} # a card is either True or False for revealed or hidden
        self.player_won_cards = {}
        self.player_won_cards_state = {}

        # used in rounds to keep track of who played what
        self.cards_played_by = {}
    
    ########## Helper functionality ##########

    # Return the player whose turn it is
    def get_turn_player(self):
        return self.player_order[self.turn]
    
    ########## Core transition mechanics for game states ##########

    # Prepare the game after we are waiting for players and want to begin
    # Called after we have all four players
    def init_game(self):
        # ugh
        #self.player_points = {}
        self.player_cards = {}
        self.player_cards_state = {} # a card is either True or False for revealed or hidden
        self.player_won_cards = {}
        self.player_won_cards_state = {}

        print('initializing game')
        # initialize random conditions
        self.game_suit = random.choice(['E', 'C', 'O', 'B'])
        # self.round_suit remains None until someone places a card
        random.shuffle(self.player_order)
        
        # split card and initialize card-related data structures
        card_split = split_cards(gen_cards())
        for n in range(4):
            player_cards = card_split[n]
            player = self.player_order[n]

            self.player_cards[player] = player_cards

            self.player_cards_state[player] = {}
            self.player_won_cards_state[player] = {}

            # a thing of note: once we use a card we REMOVE from the datastructure so no 'invalid' state
            for card in player_cards:
                self.player_cards_state[player][card] = False
            
            self.player_won_cards[player] = []
        
        # initialize temporal data
        self.turn = 0
        self.round_num = 0 # there will be 12 rounds total

        self.cards_played_by = {}
    
    # this should only be called when 
    def increment_state(self):
        print('trying to increment state')
        if self.state == 'WAITING':
            if len(self.player_order) == 4:
                self.init_game()
                self.state = 'ROUNDS'

                print('Starting Game')
            else:
                print('Need four players, have {}'.format(len(self.player_order)))
        # if we are still in the same round
        elif self.state == 'ROUNDS':
            pass
        # if we are going to a new round
        elif self.state == 'TERMINAL':
            # back to the beginning
            self.init_game()
            self.state = 'ROUNDS'

            print('Restarting Game')
        else:
            print('Unknown conditions, not in WAITING, ROUNDS, or TERMINAL states')
    
    ########## Game action transitions taken by players #########
    def restart_game(self):
        self.__init__()
        # now waiting for people

    def reset_game(self):
        self.init_game()

    # reset for when you just finished a game
    def play_again(self):
        if self.state == 'TERMINAL':
            self.increment_state()
        else:
            print('Cannot play again until game is over')
    
    # Add a player if we are in the WAITING state
    def add_player(self, player_id):
        if self.state == 'WAITING':
            if len(self.player_order) >= 4:
                print('cannot add since >=4 players (' + str(len(self.player_order)) + ')')
                return
            elif player_id in self.player_order:
                print('two players have the same id')
            else:
                self.player_order.append(player_id)
                #self.player_points[player_id] = 0
                self.player_cards[player_id] = None # init when we start the game
                self.player_cards_state[player_id] = None #init when we start the game
                self.player_won_cards[player_id] = None # init when we start the game
                # bruh
                if len(self.player_order) == 4:
                    self.increment_state()
        else:
            print('Can only add players in the WAITING state.') # LOL
    
    # Plays a card that player_id (player) has
    def play_card(self, player_id, card):
        if self.round_num >= 12:
            self.state = 'TERMINAL'
            print('game over')

        if card in self.player_cards[player_id] and player_id in self.player_order:
            if self.player_order[self.turn] == player_id:
                if self.center[self.turn] != None:
                    print('Somehow this turn already happened')
                else:
                    self.center[self.turn] = card

                    self.player_cards[player_id].remove(card)
                    del self.player_cards_state[player_id][card]
                    self.cards_played_by[card] = player_id

                    if self.round_suit is None:
                        self.round_suit = card[-1] # last element is always suit
                    
                    self.turn += 1

                    # it's been filled
                    if not None in self.center:
                        self.turn = 0
                        self.round_num += 1
                        
                        winning_card = get_winning_card(self.center, self.round_suit, self.game_suit)
                        winning_player = self.cards_played_by[winning_card]
                        self.cards_played_by = {}

                        for won_card in self.center:
                            #if CARD_VALUE[won_card] > 0 # we can do this in the gui to save space
                            self.player_won_cards[player_id].append(won_card)
                            self.player_won_cards_state[player_id][won_card] = False
                        
                        # new round new cards
                        self.center = [None, None, None, None]

                        # re-order round player order to start with winner
                        winning_player_index = 0
                        for index in range(4):
                            if self.player_order[index] == winning_player:
                                winning_player_index = index
                                break
                        self.player_order = self.player_order[winning_player_index:] + self.player_order[:winning_player_index]

                        # if points don't work it's ok we don't need them that much
                        # get the points for the winner and add the cards to his/her pile
                        # total_points = 0
                        # for card in self.center:
                        #     total_points += CARD_VALUE[card][0]
                        #     self.player_won_cards[winning_player].append(card)
                        # self.player_points[winning_player] += total_points
                        
            else:
                print('It\s not {}\'s turn'.format(player_id))
        else:
            print('Player \'{}\' nonexistent or card {} not held'.format(player_id, card))
    
    # Reveal a card the player with player_id has (precondition that he/she has it)
    # this is a toggle method so it will hide if revealed
    def reveal_card(self, player_id, card):
        if card in self.player_cards[player_id]:
            self.player_cards_state[player_id][card] = not self.player_cards_state[player_id][card]
        else:
            print('{} does not have card {} or doesn\'t exist'.format(player_id, card))
    
    # reveal a card that the player with player_id has already won (because graphics differ)
    # this is a toggle method so it will hide if revealed
    def reveal_won_card(self, player_id, card):
        if card in self.player_won_cards[player_id]:
            self.player_won_cards_state[player_id][card] = not self.player_won_cards_state[player_id][card]
        else:
            print('{} has not won card {} or doesn\'t exist'.format(player_id, card))

########## Below are helpful methods used above ##########

# Return the card of the two that wins
# rs is the round suit and gs is the game suit
def card_beats(challenger, defender, rs, gs):
    v1, s1 = challenger.split('_')
    v2, s2 = defender.split('_')
    if s1 == s2:
        return challenger if CARD_VALUE[v1] > CARD_VALUE[v2] else defender
    elif s1 == gs and s2 != gs:
        return challenger
    elif  s2 == gs and  s1 != gs:
        return defender
    elif  s1 == rs and  s2 !=rs:
        return challenger
    elif  s2 == rs and  s1 != rs:
        return defender
    else:
        # understand that this won't happen in get_winning_card
        return None # neither was able to follow the rs

# Return the card out of a card list that wins from beginning to end
def get_winning_card(cards_list, rs, gs):
    winning_card = cards_list[0]
    for card in cards_list:
        winning_card = card_beats(card, winning_card, rs, gs)
    return winning_card

# Card generation code
def gen_cards():
    cards = [value + '_' + suit for value in VALUES for suit in SUITS]
    random.shuffle(cards)
    return cards
# Card splitting will be helpful you'll see
def split_cards(cards):
    return cards[:12], cards[12:24], cards[24:36], cards[36:]