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

    def __init__(self, sheet: TileSheet, basePosX, basePosY, baseWidth, baseHeight, color: pygame.Color, wind_res, objX_init=0, objY_init=0) -> None:
        new_w, new_h = sheet.getSize()[0], sheet.getSize()[1]
        old_w, old_h = sheet.getBaseSize()[0], sheet.getBaseSize()[1]
        self.wind_res = wind_res # tuple containing width, height of the window we are displaying

        # Calculation the position and width / height of the object inside the resized sheet
        self.posX, self.posY = basePosX * new_w / old_w, basePosY * new_h / old_h # this is to obtain posX in the resized sheet (different from where we need to blit in the window)
        self.sx, self.sy = baseWidth * new_w / old_w, baseHeight * new_w / old_w # width and height of the sprite
        self.rect_sprite = pygame.Rect(self.posX, self.posY, self.sx, self.sy) # the rect representing the area inside the resized sheet where the sprite of the object is located
        self.posX, self.posY = objX_init, objY_init # position to blit the object in the window
        self.color = color

    def getSize(self):
        return self.sx, self.sy
    
    def getRect(self):
        return self.rect_sprite
    
    def setPos(self, x, y):
        self.posX, self.posY = x, y

    def getPos(self):
        return self.posX, self.posY
 
    def draw(self, tilesheet: TileSheet, wind: pygame.display) -> None: # drawing on a specific position the object in the window
        tilesheet.blit(wind, pos=(self.getPos()[0] - self.sx/2, self.getPos()[1] - self.sy/2), _area=self.rect_sprite, color=self.color)

    def draw_debugging(self, tilesheet: TileSheet, wind: pygame.display, rect) -> None: # drawing with a rect as a paramter
        posX = rect.left
        posY = rect.top
        width = rect.width
        height = rect.height
        tilesheet.blit(wind, pos=(posX - width/2, posY - height/2), _area=rect, color=self.color)

class ObjectArray(): # Array of Object
    def __init__(self, basePosX, basePosY, baseWidth, baseHeight, color: pygame.Color, wind_res) -> None:
        self.tab = []
        self.basePosX = basePosX
        self.basePosY = basePosY
        self.baseWidth = baseWidth
        self.baseHeight = baseHeight
        self.color = color
        self.wind_res = wind_res

    def add(self, sheet: TileSheet, objX_init, objY_init):
        self.tab.append(Object(sheet, self.basePosX, self.basePosY, self.baseWidth, self.baseHeight, self.color, self.wind_res, objX_init, objY_init))

    def remove(self, obj):
        self.tab.pop(obj)

    def draw(self, tilesheet: TileSheet, wind: pygame.display):
        if len(self.tab) > 0:
            for obj in self.tab:
                obj.draw(tilesheet, wind)

class ObstacleArray(ObjectArray):
    """ Class for obstacles """

    def __init__(self, sheet: TileSheet, color: pygame.Color, wind_res) -> None:
        self.config = configparser.ConfigParser()
        self.rects_tab = [] # Rects of the obstacle inside the actual display window
        self.initConfig()
        super().__init__(self.basePosX, self.basePosY, self.baseWidth, self.baseHeight, color, wind_res)
        idxOBS = 1
        for i in range(0, 4):
            self.add(sheet, idxOBS * self.wind_res[0]/5, (3.7/5)*self.wind_res[1])
            idxOBS += 1
            # Obtaining rects for the collision:
            rect = pygame.Rect(self.tab[len(self.tab)-1].getPos()[0], self.tab[len(self.tab)-1].getPos()[1], self.tab[0].getSize()[0], self.tab[0].getSize()[1]) # self.tab[0] because all the objects inside self.tab are the same
            self.rects_tab.append(rect)

    def getRects(self):
        return self.rects_tab

    def initConfig(self):
        self.config.read('params.txt')
        # Reminder! Below is the original position of the sprite before the sprite was resized
        self.basePosX = int(self.config.get('Obstacles', 'OBS_X'))
        self.basePosY = int(self.config.get('Obstacles', 'OBS_Y'))
        self.baseWidth = int(self.config.get('Obstacles', 'OBS_WIDTH'))
        self.baseHeight = int(self.config.get('Obstacles', 'OBS_HEIGHT'))

    def draw(self, tilesheet: TileSheet, wind: pygame.display): # Overload to debug the collision problem, the sprite of obstcles do not appear the same place as they should so getrects doesn't give the correct result
        i = 0
        if len(self.tab) > 0:
            for obj in self.tab:
                obj.draw_debugging(tilesheet, wind, self.rects_tab[i])
                i += 1

class LaserBeam(ObjectArray): # Laser beam object
    def __init__(self, basePosX, basePosY, baseWidth, baseHeight, color: pygame.Color, wind_res) -> None:
        super().__init__(basePosX, basePosY, baseWidth, baseHeight, color, wind_res)

    def checkCollisions(self, rects_obs, point: tuple): # To add: also test collisions with aliens
        # Check for obstacles:
        for r in rects_obs:
            print("checking point collision " + str(point) + " with rect = " + str(r))
            if r.collidepoint(point):
                print("Collision with obstacle")
                print("\n\n\n")
                return True
        print("\n\n\n")
        return False
    
    def update(self, speed, rects_obs): # Modifying the position of the objects to display on screen and deleting the ones we don't need to draw anymore
        for obj in self.tab:
            if obj.getPos()[1] - speed >= 0: # We continue to move the laser shot until we touch something or we are out of the display
                if not self.checkCollisions(rects_obs, (obj.getPos()[0], obj.getPos()[1] - speed)):
                    obj.setPos(obj.getPos()[0], obj.getPos()[1] - speed)
                else: 
                    self.tab.remove(obj)
            else: # If the object is out of the range of the display window we remove it (to add: if we touch an obstacle, we must remove the shot too)
                self.tab.remove(obj)

class Player(Object):
    """ Class for player """

    def __init__(self, sheet: TileSheet, color: pygame.Color, wind_RES) -> None:
        self.config = configparser.ConfigParser()
        self.initConfig()
        super().__init__(sheet, self.basePosX, self.basePosY, self.baseWidth, self.baseHeight, color, wind_RES)
        self.shots = LaserBeam(self.laserX, self.laserY, self.laserWidth, self.laserHeight, color, wind_RES) # Array containing the different X and Y positions of where the user pressed space to shot a beam

    def initConfig(self):
        self.config.read('params.txt')
        self.speed = int(self.config.get('Player', 'SPEED'))
        self.basePosX = int(self.config.get('Player', 'PLAYER_X'))
        self.basePosY = int(self.config.get('Player', 'PLAYER_Y'))
        self.baseWidth = int(self.config.get('Player', 'PLAYER_WIDTH'))
        self.baseHeight = int(self.config.get('Player', 'PLAYER_HEIGHT'))
        self.laserX = int(self.config.get('Player', 'LASER_X'))
        self.laserY = int(self.config.get('Player', 'LASER_Y'))
        self.laserWidth = int(self.config.get('Player', 'LASER_WIDTH'))
        self.laserHeight = int(self.config.get('Player', 'LASER_HEIGHT'))

    def getSpeed(self):
        return self.speed
    
    def getLaserRects(self):
        return self.shots.getRects()

    def update(self, sheet, laser_beam_shot, rects_obs): # Update player position and laser beam position
        # Check key pressed to handle player movement & update player pos
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            if self.objX - self.sx - self.speed >= 0:
                self.objX -= self.speed

        if keys[pygame.K_RIGHT]:
            if self.objX + self.sx + self.speed < self.wind_res[0]:
                self.objX += self.speed
        
        if laser_beam_shot: # New shot
            self.shots.add(sheet, objX_init = self.getPos()[0], objY_init = self.getPos()[1] - 5)

        self.shots.update(self.speed, rects_obs)

    def draw(self, tilesheet: TileSheet, wind: pygame.display) -> None: # Overloading
        self.shots.draw(tilesheet, wind) # We automatically remove the shots that have touched an obstacle or are out of the display window
        tilesheet.blit(wind, pos=(self.getPos()[0] - self.sx/2, self.getPos()[1] - self.sy/2), _area=self.rect_sprite, color=self.color)

class Game:
    """ Launch the game and initialised parameters """
    
    def __init__(self) -> None: 
        pygame.init()
        self.config = configparser.ConfigParser()
        self.initConfig()

        # parameters
        self.wind_res = (self.BASE_WIDTH*self.N, self.BASE_HEIGHT*self.N)
        self.screen = pygame.display.set_mode(self.wind_res)
        pygame.display.set_caption("Space Indavers")
        self.clock = pygame.time.Clock()
        self.running = True
        self.sheet = TileSheet('sheet.png', True, True, (self.N - 1) * self.BASE_WIDTH, (self.N - 1) * self.BASE_HEIGHT)
        color = pygame.Color(0, 255, 0)

        # player
        self.player = Player(self.sheet, color, self.wind_res)
        self.player.setPos(self.BASE_WIDTH*self.N/2, (4.2/5)*self.BASE_HEIGHT*self.N)

        # aliens


        # static sprites
        self.obs = ObstacleArray(self.sheet, color, self.wind_res)

    def initConfig(self):
        self.config.read('params.txt')
        self.BASE_WIDTH = int(self.config.get('Parameters', 'BASE_WIDTH'))
        self.BASE_HEIGHT = int(self.config.get('Parameters', 'BASE_HEIGHT'))
        self.N = int(self.config.get('Parameters', 'FACTOR'))

    def run(self) -> int: # game
        shot_key_pressed = False
        while self.running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        shot_key_pressed = True

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("black")

            # RENDER YOUR GAME HERE
            self.player.update(self.sheet, shot_key_pressed, self.obs.getRects()) 
            shot_key_pressed = False # We shoot only when user press the space bar      
            self.player.draw(self.sheet, self.screen)
            self.obs.draw(self.sheet, self.screen)

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.clock.tick(5)  # limits FPS to 60

        pygame.quit()

        return 0 # Everything went good

g = Game()
g.run()