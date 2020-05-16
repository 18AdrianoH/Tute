import pickle
import random

SUITS = (
    "bastos", 
    "copas", 
    "espadas", 
    "oros"
    )

# the size is very small so an array should be fine
def generate_deck():
    array = [Card(val, suit) for val in range(1,13) for suit in SUITS]
    random.shuffle(array)
    return array

class Tute:
    def __init__(self):
        self.players = []
    
    # add a player if a player with that id is not already present
    def add_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return False
        # else
        player = Player(player_id)
        self.players.append(player)
        return True
    
    def give_out_hands():
        pass
    
class Player:
    def __init__(self, id):
        # your id is a string
        assert type(id) == str
        self.id = id

class Card:
    # suits that are possible in Tute are: bastos, copas, espadas, oros
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.cards = []
        assert self.suit in SUITS
    
    def is_ace(self):
        return self.value == 1

    def has(card):
        return card in self.cards

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value and self.suit == other.suit