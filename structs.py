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

class Suits(enum.Enum):
    bastos = 0
    copas = 1
    espadas = 2
    oros = 3

# Tute waits for all players to connect while waiting for game
# it will not start until you have four players and
# once you are playing game 
class TuteState(enum.Enum):
    waiting_for_game = 0
    playing_game = 1

# game state goes from
# initialization: picks a random suit, gives out 12 cards to each player, 
class GameState(enum.Enum):
    initialization = 0


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

        self.front_image = self.load_image("./cartas-españolas/"+str(self.suit.value)+"_"+str(self.value)+".jpg")
        self.back_image = pygame.image.load("./cartas-españolas/back.jpg")
    
    def is_ace(self):
        return self.value == 1

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value and self.suit == other.suit