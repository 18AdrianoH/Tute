# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server

# this game will have a simple gui where you see your cards and whats on the table
# packets sent and recieved will be encrypted
# it will have basic timers to make sure people don't take too long
# and it will have a simple installer to install python and the necessary dependencies on mac, windows, or linux

#import pygame as pg
import socket

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

# TODO left off right after 3 will now do 4
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
            self.client.connect(self.addr)
        except Exception as exc:
            print("Failed to Connect, exception information below.")
            print(str(exc))
        return self.client.recv(2048).decode(encoding="utf-8")
    
    def send(self, data):
        try:
            self.client.send(data.encode(encoding="utf-8"))
        except socket.error as err:
            print(err)
        return self.client.recv(2048).decode()

net = Network()
sent = net.send("hello, this is a message from the client")
print(sent)