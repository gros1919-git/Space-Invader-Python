""" Space Invader Project Made in Python in 2023 by David Jeantin after reading Tonikaku Cawaii """

import os
import configparser
import pygame

class TileSheet:
    """ Class for selecting a signle or multiple sprite inside a sheet containing multiple sprite """

    def __init__(self, fname, alpha=True, resize=True, new_W=0, new_H=0) -> None:
        self.fullImage = pygame.image.load(os.path.abspath(fname)) # loading the sheet
        self.baseWidth, self.baseHeight = self.fullImage.get_width(), self.fullImage.get_height() # Initial width and height of the sheet

        # Transforming surface before use:
        self.fullImage = self.fullImage.convert() # Converting the Surface before it is blitted many times makes blitting faster.
        if alpha: # To work with sheet that have transparency
            self.fullImage = self.fullImage.convert_alpha() 

        self.rectSheet = self.fullImage.get_rect() # The object we will use to blit from

        if resize:  # resizing sheet surface
            if new_W>0 and new_H>0: # protection
                self.resize(new_W, new_H)

        self.colorImage = pygame.Surface(self.fullImage.get_size()).convert_alpha() # Surface used for the color
        
    def getSize(self): # return current size of sheet
        return (self.fullImage.get_width(), self.fullImage.get_height())
    
    def getBaseSize(self): # return initial size of sheet
        return (self.baseWidth, self.baseHeight)
    
    def changeColor(self, color: pygame.Color):
        self.colorImage.fill(color)

    def resize(self, new_W, new_H): # resize the full sheet image according to the screen resolution
        self.fullImage = pygame.transform.scale(self.fullImage, (new_W, new_H))
        
    def blit(self, wind: pygame.display, pos: tuple, _area: pygame.Rect, color: pygame.Color): # To get alien sprite, player sprite in other classes...
        self.changeColor(color)
        self.fullImage.blit(self.colorImage, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
        pygame.Surface.blit(wind, self.fullImage, pos, area=_area)
        # first arg = window, second arg = sheet surface, third arg = the position of the sprite in the window, area= the localisation of the sprite we want inside the sheet
        # self.fullImage.blit does not work so it has to be pygame.Surface.blit

class Object():
    """ Represent any object in Game"""

    def __init__(self, sheet: TileSheet, basePosX, basePosY, baseWidth, baseHeight, color: pygame.Color) -> None:
        new_w, new_h = sheet.getSize()[0], sheet.getSize()[1]
        old_w, old_h = sheet.getBaseSize()[0], sheet.getBaseSize()[1]

        # Calculation the position and width / height of the object inside the resized sheet
        self.posX, self.posY = self.basePosX * new_w / old_w, self.basePosY * new_h / old_h # this is to obtain posX in the resized sheet
        self.sx, self.sy = self.baseWidth * new_w / old_w, self.baseHeight * new_w / old_w # width and height of the sprite

        self.rect_sprite = pygame.Rect(self.posX, self.posY, self.sx, self.sy) # the rect representing the area inside the resized sheet where the sprite of the object is located

        self.objX, self.objX = 0, 0 # position to blit the object in the window
        
        self.color = color

    def getSize(self):
        return self.sx, self.sy
    
    def setPos(self, x, y):
        self.objX, self.objY = x, y

    def getPos(self):
        return self.objX, self.objY
 
    def draw(self, tilesheet: TileSheet, wind: pygame.display) -> None: # drawing on a specific position the object in the window
        tilesheet.blit(wind, pos=(self.getPos()[0] - self.sx/2, self.getPos()[1] - self.sy/2), _area=self.rect_sprite, color=self.color)

class Obstacle(Object):
    """ Class for obstacles """

    def __init__(self, sheet: TileSheet, color: pygame.Color) -> None:
        self.config = configparser.ConfigParser()
        self.initConfig()
        super().__init__(sheet, self.basePosX, self.basePosY, self.baseWidth, self.baseHeight, color)

    def initConfig(self):
        self.config.read('params.txt')
        # Reminder! Below is the original position of the sprite before the sprite was resized
        self.basePosX = int(self.config.get('Obstacles', 'OBS_X'))
        self.basePosY = int(self.config.get('Obstacles', 'OBS_Y'))
        self.baseWidth = int(self.config.get('Obstacles', 'OBS_WIDTH'))
        self.baseHeight = int(self.config.get('Obstacles', 'OBS_HEIGHT'))

class Player(Object):
    """ Class for player """

    def __init__(self, sheet: TileSheet, color: pygame.Color) -> None:
        self.config = configparser.ConfigParser()
        self.speed = 10
        self.initConfig()
        super().__init__(sheet, self.basePosX, self.basePosY, self.baseWidth, self.baseHeight, color)

    def initConfig(self):
        self.config.read('params.txt')
        self.basePosX = int(self.config.get('Player', 'PLAYER_X'))
        self.basePosY = int(self.config.get('Player', 'PLAYER_Y'))
        self.baseWidth = int(self.config.get('Player', 'PLAYER_WIDTH'))
        self.baseHeight = int(self.config.get('Player', 'PLAYER_HEIGHT'))

    def movePlayer(self, new_Pos_X):
        self.setPos(new_Pos_X, self.objY)

    def getSpeed(self):
        return self.speed

class Game:
    """ Launch the game and initialised parameters """
    
    def __init__(self) -> None: 
        pygame.init()
        self.config = configparser.ConfigParser()
        self.initConfig()

        # parameters
        self.screen = pygame.display.set_mode((self.BASE_WIDTH*self.N, self.BASE_HEIGHT*self.N))
        self.clock = pygame.time.Clock()
        self.running = True
        self.sheet = TileSheet('sheet.png', True, True, (self.N - 1) * self.BASE_WIDTH, (self.N - 1) * self.BASE_HEIGHT)
        
        # characters
        color = pygame.Color(0, 255, 0)
        self.player = Player(self.sheet, color)
        self.player.setPos(self.BASE_WIDTH*self.N/2, (4.2/5)*self.BASE_HEIGHT*self.N)

        self.obs = []
        idxOBS = 1
        for i in range(0, 4):
            obs1 = Obstacle(self.sheet, color)
            obs1.setPos(idxOBS * self.BASE_WIDTH*self.N/5, (3.7/5)*self.BASE_HEIGHT*self.N)
            self.obs.append(obs1)
            idxOBS += 1
        
        # Movement flags
        self.move_left = False
        self.move_right = False

    def initConfig(self):
        self.config.read('params.txt')
        self.BASE_WIDTH = int(self.config.get('Parameters', 'BASE_WIDTH'))
        self.BASE_HEIGHT = int(self.config.get('Parameters', 'BASE_HEIGHT'))
        self.N = int(self.config.get('Parameters', 'FACTOR'))


    def run(self) -> int: # game
        # pygame setup

        player_posX = self.player.getPos()[0]
        player_speed = self.player.getSpeed()

        while self.running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            player_pos_x = self.player.getPos()[0]
            player_speed = self.player.getSpeed()

            if keys[pygame.K_LEFT]:
                if player_pos_x - self.player.getSize()[0] - player_speed >= 0:
                    player_pos_x -= player_speed

            if keys[pygame.K_RIGHT]:
                if player_pos_x + self.player.getSize()[0] + player_speed < self.BASE_WIDTH * self.N:
                    player_pos_x += player_speed

            # Update player position
            self.player.movePlayer(player_pos_x)

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("black")

            # RENDER YOUR GAME HERE
            self.player.draw(self.sheet, self.screen)
            for obs in self.obs:
                obs.draw(self.sheet, self.screen)

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.clock.tick(60)  # limits FPS to 60

        pygame.quit()

        return 0 # Everything went good

g = Game()
g.run()