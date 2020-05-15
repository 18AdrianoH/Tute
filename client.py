# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server
import pygame as pg
import sys

# WIDTH = 500
# HEIGHT = 500
# COLOR_WHITE = (255, 255, 255)

# class Sprite:
#     pass
# class Card(Sprite):
#     pass

# window = pg.display.set_mode((WIDTH, HEIGHT))
# pg.display.set_caption("client")

# client_id = 0

# def draw(window, color):
#     window.fill(color)
#     pg.display.update()

# def main():
#     running = True
#     while running:
#         draw(window, COLOR_WHITE)
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 running = False
#                 pg.display.quit()
#                 pg.quit()
# main()

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.0.0.211"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = self.connect()
        print(self.id)

    def connect(self):
        try:
            self.client.connect((server, port))
            return self.client.recv(2048).decode(encoding="utf-8")
        except:
            print("Failed to Connect")
        pass

net = Network()
