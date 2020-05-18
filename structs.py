import pickle
import random
import enum

# valores: as = 11, 3 = 10, rey (12) = 4, caballo (11) = 3, zeta (10) = 2
# los 40s y los 20s es cuando ganas una ronda y "cantas" un rey y un caballo del mismo palo
# (40s is mismo palo del de la ronda tambien y 20s es otro palo; pero igual tenes que ganar)
# tute es quatro reyes o quatro caballos -> ganas el juego completo

# antes de conectarse Tute tiene que mostrar:
# 1. cuantos jugadores hay
# 2. quien esta jugando

# cada junta de juegos se juegan tres juegos, pero si alguien tiene tute gana todo

# cada juego se:
# 1. se ponen jugadores a la sar al re-dedor de la mesa (la orden va a ser como un reloj)
# 2. se elige un palo a la sar (de una carta elijida a la sar)
# 3. se elije la mano a la sar 
# despues de reparten 12 cartas a cada uno
# y luego se juegan rondas hasta el fin del juego

# cada ronda se:
# 0. la mano es el que gano la mano anterior, si no se elije a la sar
# 1. la mano pone una carta elijiendo el palo
# 2. despues calquier carta puesta tiene que ser de ese palo y mas alta que la anterior
#    si no tenes mas alta que la anterior puede ser mas baja (pero tiene que ser del mismo palo)
#    si no tenes de ese palo tiene que ser del palo del juego total y ese palo tiene el valor maximo
#    si no tenes ese tampoco puede ser de cualquier palo y puede ser cualquier carta
# 3. el ganador se elige con estas reglas:
#    - de las del palo del juego gana la mas alta
#    - si no hay de ese palo, del palo de la ronda gana la mas alta
#        - siempre hay una de ese palo por que corresponde con la carta de la mano
# el que gana agarra las cuantro cartas y las pone en su pila de cartas usadas

# cosas importantes que pueda hacer el usuario:
# 1. leer sus cartas ganadas (pero no las de los otros)
# 2. tener un contador de cuantas cartas gano
# 3. tener un contador de cuantas cartas tiene
# 4. poder ver todas o casi todas sus cartas
# 5. ver las cartas del centro en el orden en que se pusieron
# 6. ver quien es la mano de la ronda

# Important notes for graphics:
# 1. each player sees themselves at the bottom
# the rest of the array from their index to the end and then around from the start to the one before them
# is filled in from left to top to right (i.e. clockwise)
# 2. whoever is playing will have their name in red, whereas everyone else will have their name in black

"""
Below, here, is a sort of ascii picture of what I envision

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

I might text for the pictures to expect at the end of the game but it should be very simple:
basically just a list in the middle of the screen.
"""

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

class GameState(enum.Enum):
    init_placing = 0 # pick a random order of players
    init_suit = 1 # pick a random suit
    init_shuffle = 2 # shuffle cards and give 12 out to each player
    init_hand = 3 # pick starting player
    setting_up_round = 4 # wait for round to start (round is started by previous winner, or if first round by hand)
    round = 5 # playing round
    end_scores = 6 # game is over and display scores (maybe some stats too)
    end_winner = 7 # display winner and update data structures

# where cards are since there are only a set number of such places
class CardPosition(enum.Enum):
    pass

# the size is very small so an array should be fine
def generate_deck():
    array = [Card(val, suit) for val in range(1,13) for suit in SUITS]
    random.shuffle(array)
    return array

class Tute:
    def __init__(self):
        self.players = []
        self.num_games = 3
    
    # add a player if a player with that id is not already present
    def add_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return False
        # else
        player = Player(player_id)
        self.players.append(player)
        return True
    
    

# there are three games in Tute
class Game:
    def __init__(self):
        pass
    def give_out_hands(self):
        pass
    pass
    
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