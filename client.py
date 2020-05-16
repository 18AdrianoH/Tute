# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server

# this game will have a simple gui where you see your cards and whats on the table
# packets sent and recieved will be encrypted
# it will have basic timers to make sure people don't take too long
# and it will have a simple installer to install python and the necessary dependencies on mac, windows, or linux

import pygame
import socket

WIDTH = 500
HEIGHT = 500
COLOR_WHITE = (255, 255, 255)

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "10.0.0.211"
        self.port = 5555
        self.id = self.connect()

    def connect(self):
        try:
            self.client.connect((self.server, self.port))
        except Exception as exc:
            print("Failed to Connect, exception information below.")
            print(str(exc))
        return self.client.recv(2048).decode(encoding="utf-8")
    
    def quit(self):
        self.client.close()
    
    def send(self, data):
        try:
            self.client.send(data.encode(encoding="utf-8"))
        except socket.error as err:
            print(err)
        return self.client.recv(2048).decode()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("client")

def draw(window, color):
    window.fill(color)
    pygame.display.update()

def main(client_id=0):
    net = Network()

    running = True
    while running:
        draw(window, COLOR_WHITE)
        for event in pygame.event.get():
            # user can quit just by closing the window
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()
                net.quit()
                pygame.quit()
            # we set it up for testing so that if you set up a space-bar you send a request
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                net.send("request from client with id {}".format(str(client_id)))
    
if __name__ == "__main__":
    main(client_id=0)