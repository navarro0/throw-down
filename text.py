import pygame
from pygame.locals import *

## Wrapper class to handle text objects
class Text(object):
    def __init__(self, string, pos, color=[255,255,255], size=16, right=False):
        ## Constructor
        self.font = pygame.font.Font("RES/FONT/FONT.ttf", size)
        self.y = pos[1]                                                 ## Top anchoring Y-coordinate
        self.color = color                                              ## Color tuple
        self.text = string                                              ## Text string to draw
        self.height = self.font.get_height()                            ## Height of font
        self.renderable = self.font.render(self.text, True, self.color) ## Renderable text object
        self.width = self.renderable.get_width()                        ## Width of rendered text

        ## Anchors the text to the x-coordinate for right-justification
        if right:
            self.x = pos[0] - self.width
        else:
            self.x = pos[0]

    def draw(self, surface):
        ## Draw the rendered text object to the target surface
        surface.blit(self.renderable, (self.x, self.y))

    def update(self, string):
        ## Only re-render and update the text if the string has changed at all
        if string != None and string != self.text:
            self.text = string
            self.renderable = self.font.render(self.text, False, self.color)
            self.width = self.renderable.get_width()
