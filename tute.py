import random

########## Constants #########

FACES = ('B', 'E', 'C', 'O')
VALUES = ('A', 'R', 'C', 'S', '9', '8', '7', '6', '5', '4', '3', '2')

CARD_ORDER = {'A' : 11,'3' : 10,'R' : 9,'C' : 8,'S' : 7,'9' : 6, '8' : 5, '7' : 4, '6' : 3, '5' : 2, '4' : 1, '3' : 0}
CARD_VALUE = {'A' : 11,'3' : 10,'R' : 4,'C' : 3,'S' : 2,'9' : 0, '8' : 0, '7' : 0, '6' : 0, '5' : 0, '4' : 0, '3' : 0}

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
def to_dict(game):
    pass
# return a tute game from a dict representation of the game
def from_dict(game):
    pass
# serialize a game dict into bits to be sent
def serialize(game):
    pass
# desertialize bits into a game dict
def deserialize(bits):
    pass

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

        self.player_points = {}
        self.player_cards = {}
        self.player_cards_state = {} # a card is either True or False for revealed or hidden
        self.player_won_cards = {}
        self.player_won_cards_state = {}

        # used in rounds to keep track of who played what
        self.cards_played_by = None

        self.round_finised = None
        self.turn_finished = None
    
    ########## Helper functionality ##########

    # Return the player whose turn it is
    def get_turn_player(self):
        return self.player_order[self.turn]
    
    ########## Core transition mechanics for game states ##########

    # Prepare the game after we are waiting for players and want to begin
    # Called after we have all four players
    def init_game(self):
        # initialize random conditions
        self.game_suite = random.choice(['E', 'C', 'O', 'B'])
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
        self.round_finised = False
        self.turn_finished = False

        self.cards_played_by = {}
    
    # this should only be called when 
    def increment_state(self):
        if self.state == 'WAITING':
            if len(self.player_order) == 4:
                self.init_game()
                self.state = 'ROUNDS'

                print('Starting Game')
            else:
                raise InvalidAction('Need four players, have {}'.format(len(self.player_order)))
        # if we are still in the same round
        elif self.state == 'ROUNDS':
            if self.round_num < 12:
                if self.round_finised:
                    # get who won
                    winning_card = get_winning_card(self.center, self.round_suit, self.game_suit)
                    winning_player = cards_played_by[winning_card]
                    
                    # get the points for the winner and add the cards to his/her pile
                    total_points = 0
                    for card in self.center:
                        total_points += CARD_VALUE[card]
                        self.player_won_cards[winning_player].append(card)
                    self.player_points[winning_player] += total_points

                    # new round new cards
                    self.center = [None, None, None, None]

                    # re-order round player order to start with winner
                    winning_player_index = 0
                    for index in range(4):
                        if self.player_order[index] == winning_player:
                            winning_player_index = index
                            break
                    self.player_order = self.player_order[winning_player_index:] + self.player_order[:winning_player_index]

                    # next round
                    self.round += 1
                    self.turn = 0

                    self.round_finished = False
                    self.turn_finished = False

                elif self.turn_finished:
                    # next turn
                    self.turn += 1
                    self.turn_finished = False

                else:
                    raise InvalidAction('Need to finish turn or round')
            else:
                self.state = 'TERMINAL'

                print('Game over')
                for player in players:
                    print('{} got {} points before 40\'s, 20\'s and Tute'.format(player, self.player_points[player]))
        # if we are going to a new round
        elif self.state == 'TERMINAL':
            # back to the beginning
            self.init_game()
            self.state = 'ROUNDS'

            print('Restarting Game')
        else:
            raise InvalidState("Unknown conditions, not in WAITING, ROUNDS, or TERMINAL states")
    
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
            raise InvalidAction('Cannot play again until game is over')
    
    # Add a player if we are in the WAITING state
    def add_player(self, player_id):
        if self.state == 'WAITING':
            if len(self.player_order) == 4:
                raise InvalidAction('Already have four players.')
            elif player_id in player_order:
                raise InvalidAction('Player already joined.')
            else:
                self.player_order.append(player_id)
                self.player_points[player_id] = 0
                self.player_cards[player_id] = None # init when we start the game
                self.player_cards_state[player_id] = None #init when we start the game
                self.player_won_cards[player_id] = None # init when we start the game
        else:
            raise InvalidAction('Can only add players in the WAITING state.')
    
    # Plays a card that player_id (player) has
    def play_card(self, player_id, card):
        assert self.state in self.play_states # make sure we are in a round
        assert self.players[self.player_index] == player_id # make sure the right player is going (i.e. their turn)
        self.player_cards[player].remove(card_str)

        # add card to the center
        self.center[self.center_index] = card_str
        self.center_index += 1

        # if it's the first card played it determines the face for the round
        if self.round_face = None:
            self.round_face = card_str[2] # 3rd thing is the face
    
    # Reveal a card the player with player_id has (precondition that he/she has it)
    # this is a toggle method so it will hide if revealed
    def reveal_card(self, player_id, card):
        if card in self.player_cards[player_id]:
            self.player_cards_state[player_id][card] = not self.player_cards_state[player_id][card]
        else:
            raise InvalidAction('{} does not have card {}'.format(player_id, card))
    
    # reveal a card that the player with player_id has already won (because graphics differ)
    # this is a toggle method so it will hide if revealed
    def reveal_won_card(self, player_id, card):
        if card in self.player_won_cards[player_id]:
            self.player_won_cards_state[player_id][card] = not self.player_won_cards_state[player_id][card]
        else:
            raise InvalidAction('{} has not won card {}'.format(player_id, card))

########## Below are helpful methods used above ##########

# Return the card of the two that wins
# rs is the round suit and gs is the game suit
def card_beats(challenger, defender, rs, gs):
    v1, s1 = challenger.split('_')
    v2, s2 = defender.split('_')
    if f1 == f2:
        return challenger if CARD_VALUE[v1] > CARD_VALUE[v2] else defender
    elif f1 == gs and f2 != gs:
        return challenger
    elif  f2 == gs and  f1 != gs:
        return defender
    elif  f1 == rs and  f2 !=rs:
        return challenger
    elif  f2 == rs and  f1 != rs:
        return defender
    else:
        # understand that this won't happen in get_winning_card
        return None # neither was able to follow the rs

# Return the card out of a card list that wins from beginning to end
def get_winning_card(cards_list, rs, gs):
    winning_card = cards_list[0]
    for card in cards_list
        if card_beats(card, winning_card, rs, gs):
            winning_card = card
    return winning_card

# Card generation code
def get_cards():
    cards = [face + '_' + value for face in FACES for value in VALUES]
    random.shuffle(cards)
    return cards
# Card splitting will be helpful you'll see
def split_cards(cards):
    return cards[:12], cards[12:24], cards[24:36], cards[36:]