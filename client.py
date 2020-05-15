# un juego de tute para jugar online con la familia
# client has some basic functionality for displaying cards and helping you make choices which are then sent to the server
import pygame as pg
import sys

WIDTH = 500
HEIGHT = 500
COLOR_WHITE = (255, 255, 255)

class Sprite:
    pass
class Card(Sprite):
    pass

window = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("client")

client_id = 0

def draw(window, color):
    window.fill(color)
    pg.display.update()

def main():
    running = True
    while running:
        draw(window, COLOR_WHITE)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.display.quit()
                pg.quit()
main()