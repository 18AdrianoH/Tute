import pickle
import random
import enum

FACES = ("B", "E", "C", "O")
VALUES = ("A", "R", "C", "S", "9", "8", "7", "6", "5", "4", "3", "2")

# Tute states are
# WAITING # waiting for players
# WAITING_P1 # waiting for player 1 to play
# WAITING_P2 # waiting for player 2 to play
# WAITING_P3 # waiting for player 3 to play
# WAITING_P4 # waiting for player 4 to play
# TERMINAL # game has ended players now count points, can restart game now
class Tute:
    def __init__(self, players):
        ############################ STATE MACHINE #######################
        self.state = "WAITING" # initially in waiting state
        self.round_num = 0
        # play states are always randomized
        self.play_states = ["WAITING_P1", "WAITING_P2", "WAITING_P3", "WAITING_P4"]
        random.shuffle(play_states) # decide order of play
        # if we want to re-initialize just use previous players
        self.players = [None, None, None, None] if players is None else players
        self.player_index = 0
        self.play_state_index = 0
        ############################
        self.player_cards = {}
        self.game_face = random.choice(["E", "C", "O", "B"])
        self.round_face = None
        self.center = [None, None, None, None]
        self.center_index = 0
        self.player_won_cards = {}
        self.player_revealed_cards = {}
    
    # add a player if a player with that id is not already present
    def add_player(self, player_id):
        num_player = 0 # i.e. player 1
        for player in self.players:
            if player is not None:
                if player == player_id: # assume "player" is a string
                    return False
                # else
                num_player += 1
        
        assert num_player < 4 # lul

        index = 0 # for player inside the players array
        insert_index = 0
        for player in self.play_states:
            player_num = int(player[-1]) - 1
            if player_num == num_player:
                insert_index = index
                break
            index += 1
        
        self.players(insert_index) = player_id
        self.player_cards[player_id] = None # later change to their cards
        self.player_won_cards[player_id] = []
        self.player_revealed_cards[player_id] = {}
        return True
    
    # return if the first (challenger) is > defender
    # format is as defined above
    # game_face is the face we are using in the game
    # return None if neither wins (we'll let the first player instead in that case)
    def compare_key_strings(self, challenger, defender):
        val1, face1 = challenger.split("_")
        val2, face2 = defender.split("_")
        if face1 == face2:
            assert val1 != val2 # whoopsies
            return card_type_order[face1] > card_type_order[face2]
        elif face1 == self.game_face and face2 != self.game_face:
            return True # challenger win
        elif face2 == self.game_face and face1 != self.game_face:
            return False # defender win
        elif face1 == self.round_face and face2 != self.round_face:
            return True # challenger win
        elif face2 == self.round_face and face1 != self.round_face:
            return False # defender win
        else:
            # neither is game_face and neither is round_face so we will return none
            # in practice this will never be returned as you'll see below
            # in this case the first card down wins
            return None

    # will go from card 0 (first placed) to card n (of length n card_list) (last placed) and return the index
    # for the card that wins
    def get_winner(self):
        assert len(card_list) > 0
        winner = 0
        for i in range(1,len(card_list)):
            if compare_key_strings(card_list[i], card_list[winner]e):
                winner = i
        return i

    def get_cards(self):
        cards = [face + "_" + value for face in FACES for value in VALUES]
        random.shuffle(cards)
        return cards

    def split_cards(self, cards):
        # there are a total of 48 cards
        return cards[:12], cards[12:24], cards[24:36], cards[36:]
    
    # start the game after we are waiting for players
    # called after we have all four players
    def start_game(self):
        assert not players.contains(None) # will have the four names of the four people
        assert self.state == "WAITING"
        self.state = self.play_states[0]
        self.round_num = 1 # start at 1
        # self.state is now WAITING_PX for some X so taking [-1] is the last element
        self.player_index = int(self.state[-1]) - 1 # will always index by one so -1
        self.play_state_index = 0
        
        cards_tuple = self.split_cards(self.get_cards)
        i = 0
        for player in player_cards:
            player_cards[player] = cards_tuple[i]
            for card in player_cards:
                player_revealed_cards[player][card] = False
            i += 1
    
    # this should only be called when 
    def increment_state(self):
        # if we are still in the same round
        if self.play_state_index < 3:
            self.play_state_index += 1
            self.player_index = int(self.state[-1]) - 1
        # if we are going to a new round
        elif self.round_num < 12: # 12 rounds at the last round it will be over
            # determine winner and give cards to players
            winner_index = self.get_winner() # remember that self.playes is in this wrder
            winner_id = self.players[winnder_index] # this might be used later
            print("{} won".format(winner_id))

            # give the center cards to winner_id
            for card in center:
                assert not card is None #lul
                self.player_won_cards[winner_id].append(card)

            # everything before winner id now goes to the back cyclically for players
            # and for waiting array (playstates)
            # now order is based on the winner
            self.players = self.players[:winner_index] + self.players[winner_index:]
            self.play_states = self.play_states[:winner_index] + self.play_state_index[winner_index:]

            # set up next round
            self.round_num += 1
            self.play_state_index = 0
            self.state = self.play_states[0]
            self.center_index = 0
            self.center = [None, None, None, None]
            self.round_face = None
        else:
            # this is basically all that needs to be done, now players 
            self.state = "TERMINAL" # we will be in the terminal state
    
    # for the next game
    def reset_game(self):
        self.__init__(self.players) # list of names
    
    # should only be able to play card_str that is there -> in client
    def play_card(self, player_id, card_str):
        assert self.state in self.play_states # make sure we are in a round
        assert self.players[self.player_index] == player_id # make sure the right player is going (i.e. their turn)
        self.player_cards[player].remove(card_str)

        # add card to the center
        self.center[self.center_index] = card_str
        self.center_index += 1

        # if it's the first card played it determines the face for the round
        if self.round_face = None:
            self.round_face = card_str[2] # 3rd thing is the face

#################### deprecated code below ##################

# the size is very small so an array should be fine
# def generate_deck():
#     array = [Card(val, suit) for val in range(1,13) for suit in SUITS]
#     random.shuffle(array)
#     return array
    
class Suits(enum.Enum):
    bastos = 0
    copas = 1
    espadas = 2
    oros = 3

class TuteState(enum.Enum):
    waiting_to_start = 0 # waiting for 4 players to connect and be added to data structures
    waiting_for_game = 1 # waiting for players to acknowledge readiness for beginning of game
    playing_game = 2 # playing game; after playing game will go back to waiting_for_game
    end_scores = 3 # show who won and maybe some stats
    end_winner = 7 # show the winner
    # after end_winner go to waiting_for game
    
class Player:
    def __init__(self, id):
        # your id is a string
        assert type(id) == str
        self.id = id

        self.cards = []
    
    def has(self, card):
        return card in self.cards

class Card:
    # suits that are possible in Tute are: bastos, copas, espadas, oros
    def __init__(self, value, suit):
        self.value = value
        assert type(value) == int
        self.suit = suit
        assert type(suit) == Suits

        self.front_image = pygame.image.load("./cartas-españolas/"+str(self.suit.value)+"_"+str(self.value)+".jpg")
        self.back_image = pygame.image.load("./cartas-españolas/back.jpg")
    
    def is_ace(self):
        return self.value == 1

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value and self.suit == other.suit