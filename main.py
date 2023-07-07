import math
import time
import _pyinstaller_hooks_contrib
import pygame
import os
import sys
import json
pygame.font.init()
pygame.mixer.init()


def getResourcePath(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        base_path = os.path.abspath(".")
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

FPS = 60
ScreenWidth = 1280
ScreenHeight = 720
Title = "Basic Mario 2"
icon : pygame.surface = pygame.image.load(getResourcePath(str.__add__('Assets/', "icon.png")))
windowColor = (39, 21, 13)
pygame.init()
run = True
entities = []
BGs = []

window = pygame.display.set_mode((ScreenWidth, ScreenHeight))
pygame.display.set_caption(Title)
pygame.display.set_icon(icon)

bulletChance = 20
IsGameOver = False

import pickle

GameStarted = False
Highscore = 0
game_state = {
    'highscore' : Highscore,
}

def save_game_state(game_state, file_name):
    try:
        with open(file_name, 'wb') as file:
            pickle.dump(game_state, file)
            print("Game state saved successfully!")
    except IOError:
        print("Error: Unable to save game state.")

# Load game state
def load_game_state(file_name):
    try:
        if os.path.getsize(file_name) > 0:
            with open(file_name, 'rb') as file:
                game_state = pickle.load(file)
                print("Game state loaded successfully!")
                return game_state
        else:
            return {'highscore': Highscore}
    except (IOError, pickle.UnpicklingError):
        print("Error: Unable to load game state.")
        return {'highscore': Highscore}

def main():
    global run
    global entities
    global Highscore
    global game_state
    global GameStarted
    GameStarted = False
    run = True
    entities = []
    clock = pygame.time.Clock()

    pygame.mixer.music.load(getResourcePath(str.__add__('Assets/', "music1.mp3")))
    pygame.mixer.music.set_volume(.5)
    pygame.mixer.music.play(9999, 0, 2000)

    window.fill((0,0,0))

    addTEXT("text", "a game made by DEVENILLA", (ScreenWidth/2, ScreenHeight/2-50), 5, 7, (255, 255, 255), (0,0,0))

    for ENTITY in entities:
        ENTITY.draw()

    pygame.display.update()

    time.sleep(2.7)

    entities = []

    game_state = load_game_state('save_game.pickle')
    Highscore = game_state['highscore']

    addHIGHSCORE_TIMER("name", (640, 100), 0, 5,  (0, 255, 255), (0,0,0))

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                start()

        for ENTITY in entities:
            if not BGs.__contains__(ENTITY):
                ENTITY.fixedUpdate(player, entities)

        surface: pygame.surface = pygame.image.load(getResourcePath(str.__add__('Assets/', "start_screen.png")))
        window.blit(surface, (0, 0))


        for ENTITY in entities:
            ENTITY.draw()

        pygame.display.update()

    quit()

def playSound(name : str, volume : float):
    soundPath = getResourcePath(str.__add__('Assets/', name+".wav"))
    sound: pygame.mixer.Sound = pygame.mixer.Sound(soundPath)
    sound.set_volume(volume)
    sound.play(0)

def start():
    global run
    global IsGameOver
    global bulletChance
    global entities
    global BGs
    global GameStarted
    playSound("select", 1)
    GameStarted = True
    run = True
    IsGameOver = False
    entities = []
    clock = pygame.time.Clock()
    bulletChance = 120
    vignette = addBG("vignette", ["vignette"])
    BGs.append(vignette)
    BG = addBG("background", ["bg1", "bg2"])
    BG.converted = True
    BGs.append(BG)
    addHPBG("hp", ["health_0", "health_1", "health_2", "health_3"])
    addTIMER("name", (78, 37), 0, 3,  (255, 255, 255), (0,0,0))
    addHIGHSCORE_TIMER("name", (78, 60), 0, 3,  (0, 255, 255), (0,0,0))
    player = addPlayer("player", ["dev", "dev_run1", "dev_run2", "dev_run3"], (0, 0), (1, 1), (0, 0), 0)
    groundChecker = addEntity("checker", ["ground_checker"], (0, 0), (1, 12), (0, 0), 0)
    platform = addPlatform("platform", ["platform"], (0, 0), (5, 3), (0, 0), 0)

    player.platform = platform
    player.checker = groundChecker
    platform.player = player

    while run:
        clock.tick(FPS)

        player.platform = platform
        player.checker = groundChecker
        platform.player = player

        handleOrbs()
        bulletChance = handleBullets(player, bulletChance)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and IsGameOver:
                    reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.isGrounded():
                    player.tryJump()

        for ENTITY in entities:
            if not BGs.__contains__(ENTITY):
                ENTITY.fixedUpdate(player, entities)

        BG.animate(.05)

        if not IsGameOver:
            render(vignette)
        else:
            renderWithoutVignette()

        save_game_state(game_state, 'save_game.pickle')

    quit()

def quit():
    tick = 9

def hurtPlayer(play):
    p : player = play
    if p.tick >= 30:
        playSound("hit", .3)
        p.hp -= 1
        if p.hp <= 0:
            gameOver()
            return

        for ENTITY in entities:
            if ENTITY.name == "bullet": entities.remove(ENTITY)
            else : ENTITY.onPlayerDamage(player)

    p.rect.centerx = ScreenWidth / 2
    p.rect.centery = ScreenHeight / 2 - 100
    p.platform.alpha = 255
    pygame.mouse.set_pos(ScreenWidth / 2, ScreenHeight / 2)

def gameOver():
    global IsGameOver
    IsGameOver = True
    clock = pygame.time.Clock()

    playSound("death", 1)
    for i in range(7):
        BG = addBG("end", [str.__add__("end_screen_", str(int(i + 1)))])
        BG.converted = False
        BGs.append(BG)
        renderWithoutVignette()


def handleOrbs():
    if IsGameOver: return
    if random.randrange(0, 50) == 5:
        addOrb("orb", ["orb"], (random.randrange(-600, 600), random.randrange(-300, 300)), (2, 2), (0, 0), 0,
               player, platform)


def handleBullets(p, bb):
    if IsGameOver: return
    b = bb
    if random.randrange(0, b) == 5:
        addBullet(p)
        if b > 35:
            b -= random.randrange(1, 3)
    return b


def addEntity(name, image, position, scale, flipped, angle):
    ENTITY = entity(name, image, position, scale, flipped, angle, len(entities) - 1)
    entities.append(ENTITY)
    return ENTITY


def addBG(name, image):
    ENTITY = bg(name, image, True, len(entities) - 1)
    entities.append(ENTITY)
    return ENTITY

def addHPBG(name, image):
    ENTITY = healthBg(name, image, len(entities) - 1)
    entities.append(ENTITY)
    return ENTITY

def addTEXT(name, string, pos, angle, size, color, bgColor):
    ENTITY = text(name, string, pos, angle, size, len(entities) - 1, color, bgColor)
    entities.append(ENTITY)
    return ENTITY
def addTIMER(name, pos, angle, size, color, bgColor):
    ENTITY = timer(name, "", pos, angle, size, len(entities) - 1, color, bgColor)
    entities.append(ENTITY)
    return ENTITY
def addHIGHSCORE_TIMER(name, pos, angle, size, color, bgColor):
    ENTITY = hstimer(name, "", pos, angle, size, len(entities) - 1, color, bgColor)
    entities.append(ENTITY)
    return ENTITY

def addPlayer(name, image, position, scale, flipped, angle):
    ENTITY = player(name, image, position, scale, flipped, angle, len(entities) - 1)
    entities.append(ENTITY)
    return ENTITY


def addOrb(name, image, position, scale, flipped, angle, _player, _platform):
    ENTITY = orb(name, image, position, scale, flipped, angle, len(entities) - 1)
    entities.append(ENTITY)
    ENTITY.player = _player
    ENTITY.platform = _platform
    return ENTITY


def addBullet(_player):
    c = random.randrange(0, 4)
    s = 2
    playSound("laser", .1)
    if c == 0:  # up
        pos = (random.randrange(-600, 600), 400)
        ENTITY = beam("bullet", ["beam", "beam_1", "beam_2", "beam_3"], (pos.__getitem__(0), -400), (s, 50), (0, 0), 0, len(entities) - 1)
        ENTITY.pos = pos
        ENTITY.ang = 0
        ENTITY.f = (0, 0)
        entities.append(ENTITY)
        ENTITY.player = _player
    elif c == 1:  # down
        pos = (random.randrange(-600, 600), -400)
        ENTITY = beam("bullet", ["beam", "beam_1", "beam_2", "beam_3"], pos, (s, 50), (0, 0), 0, len(entities) - 1)
        ENTITY.pos = pos
        ENTITY.ang = 180
        ENTITY.f = (0, 0)
        entities.append(ENTITY)
        ENTITY.player = _player
    elif c == 2:  # right
        pos = (800, random.randrange(-350, 350))
        ENTITY = beam("bullet", ["beam", "beam_1", "beam_2", "beam_3"], (-800, pos.__getitem__(1)), (s, 50), (0, 0), 270, len(entities) - 1)
        ENTITY.pos = pos
        ENTITY.ang = 270
        ENTITY.f = (1, 1)
        entities.append(ENTITY)
        ENTITY.player = _player
    elif c == 3:  # left
        pos = (-800, random.randrange(-350, 350))
        ENTITY = beam("bullet", ["beam", "beam_1", "beam_2", "beam_3"], pos, (s, 50), (0, 0), 90, len(entities) - 1)
        ENTITY.pos = pos
        ENTITY.ang = 90
        ENTITY.f = (1, 1)
        entities.append(ENTITY)
        ENTITY.player = _player


def addPlatform(name, image, position, scale, flipped, angle):
    ENTITY = platform(name, image, position, scale, flipped, angle, len(entities) - 1)
    entities.append(ENTITY)
    return ENTITY


def render(vignette):
    # ADD BACKGROUND
    window.fill(windowColor)

    # RENDER OBJECTS
    for ENTITY in entities:
        if ENTITY != vignette:
            ENTITY.draw()

    #vignette.draw()

    pygame.display.update()


def renderWithoutVignette():
    # ADD BACKGROUND
    window.fill(windowColor)

    # RENDER OBJECTS
    for ENTITY in entities:
        ENTITY.draw()

    pygame.display.update()


def reset():
    start()


import random

import pygame
import os


class entity:
    name = "new entity"
    images: list = ["template"]
    imageIndex = 0
    flipped = [0, 0]
    angle = 0
    rect: pygame.Rect = None
    idx = 0

    # when we create a mew Entity
    def __init__(self, name, images, position, scale, flipped, angle, idx):
        self.name = name
        self.images = images
        self.idx = idx
        surface: pygame.surface = pygame.image.load(
            getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[self.imageIndex]), ".png")))))
        scale = (surface.get_width() * scale.__getitem__(0), surface.get_height() * scale.__getitem__(1))

        xpos = position.__getitem__(0) + ScreenWidth / 2 - surface.get_width() / 2
        ypos = position.__getitem__(1) + ScreenHeight / 2 - surface.get_height() / 2

        self.rect = pygame.Rect(xpos, ypos, scale.__getitem__(0), scale.__getitem__(1))
        self.flipped = [flipped.__getitem__(0), flipped.__getitem__(1)]
        self.angle = angle
        self.start()
        self.update()

    def update(self):
        if not run: return
        tick = 0

    def onPlayerDamage(self, player):
        tick=0

    def start(self):
        if not run: return
        self.angle = self.angle

    # runs without a fixed number of times
    def draw(self):
        if not run: return
        surface: pygame.surface = pygame.image.load(
            getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[self.imageIndex]), ".png")))))
        # scale
        surface = pygame.transform.scale(surface, self.rect.size)
        surface = pygame.transform.flip(surface, self.flipped.__getitem__(0), self.flipped.__getitem__(1))

        # rotation
        surface = pygame.transform.rotate(surface, self.angle)

        
        # draw
        window.blit(surface, (self.rect.x, self.rect.y))

    # runs with a fixed number of times
    def fixedUpdate(self, player, entities):
        if not run: return
        tick = 0

    def animate(self, amount = 1):
        if int(self.imageIndex + amount) >= len(self.images):
            self.imageIndex = 0
        else:
            self.imageIndex += amount


class bg(entity):
    name = "new entity"
    images: list = ["template"]
    tick = 0
    idx = 0
    converted = True

    # when we create a mew Entity
    def __init__(self, name, images, converted, idx):
        self.name = name
        self.images = images
        self.idx = idx
        self.converted = converted

    # runs without a fixed number of times
    def draw(self):
        if not run: return
        surface: pygame.surface = pygame.image.load(
            getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[int(self.imageIndex)]), ".png")))))
        
        # draw
        if self.converted:
            surface = surface.convert(surface)

        window.blit(surface, (0, 0))

class healthBg(bg):
    name = "new entity"
    images: list = ["template"]
    tick = 0
    idx = 0

    # when we create a mew Entity
    def __init__(self, name, images, idx):
        self.name = name
        self.images = images
        self.idx = idx

    def fixedUpdate(self, player, entities):
        if player.hp >= 3:
            self.imageIndex = 3
        else:
            self.imageIndex = player.hp

    # runs without a fixed number of times
    def draw(self):
        if not run: return
        surface: pygame.surface = pygame.image.load(
            getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[self.imageIndex]), ".png")))))

        surface = pygame.transform.scale_by(surface, 10)

        # draw
        window.blit(surface.convert_alpha(), (0, 0))


class player(entity):
    speed = 5
    sprintSpeed = 10
    jumpForce = -15
    gravity = 1
    xVelocity = 0
    yVelocity = 0
    wasGrounded = False
    checker: entity = None
    platform: platform = None
    animationTick = 0
    jumpTimes = 1
    hp = 3
    tick = 0

    prevX = 0
    prevY = 0

    def start(self):
        self.hp = 3

    def onPlayerDamage(self, player):
        self.tick = 0

    def fixedUpdate(self, player, entities):
        if not run: return

        self.tick += .5

        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_a]:
            self.flipped[0] = True
            if keys_pressed[pygame.K_LSHIFT]:
                self.xVelocity = -self.sprintSpeed
            else:
                self.xVelocity = -self.speed
        elif keys_pressed[pygame.K_d]:
            self.flipped[0] = False
            if keys_pressed[pygame.K_LSHIFT]:
                self.xVelocity = self.sprintSpeed
            else:
                self.xVelocity = self.speed
        elif not keys_pressed[pygame.K_d] and not keys_pressed[pygame.K_a]:
            if self.xVelocity > 0:
                self.xVelocity -= 1
            elif self.xVelocity < 0:
                self.xVelocity += 1

        if keys_pressed[pygame.K_SPACE] and self.isGrounded():
            self.tryJump()

        if not self.isGrounded():
            self.yVelocity += self.gravity
            self.wasGrounded = False
        elif self.isGrounded():
            self.jumpTimes = 1
            if self.yVelocity > 0: self.yVelocity = 0

        self.moveSteps(self.xVelocity, 0)
        self.moveSteps(0, self.yVelocity)

        if self.xVelocity != 0:
            if self.animationTick >= 2:
                self.animate()
                self.animationTick = 0
            else:
                self.animationTick += 1
        else:
            self.imageIndex = 0

        if self.rect.centerx > ScreenWidth + self.rect.size.__getitem__(
                0) / 2 or self.rect.centerx < 0 - self.rect.size.__getitem__(
            0) / 2 or self.rect.y > ScreenHeight:
            hurtPlayer(player)

    def tryJump(self):
        if not run: return
        if self.jumpTimes > 0:
            playSound("jump", .3)
            self.yVelocity = self.jumpForce
            self.jumpTimes -= 1

    def isGrounded(self):
        if not run: return
        self.checker.rect.x = self.rect.x + self.rect.size.__getitem__(0) / 2
        self.checker.rect.y = self.rect.y + self.rect.size.__getitem__(1) / 2
        if self.checker.rect.colliderect(self.platform.rect):
            return True
        return False

    def moveSteps(self, xSteps, ySteps):
        if not run: return
        self.rect.x += xSteps
        # if self.rect.colliderect(self.platform.rect):
        #    self.rect.x -= xSteps

        self.rect.y += ySteps
        while self.rect.colliderect(self.platform.rect) and self.isGrounded():
            self.rect.y -= 1

    def draw(self):
        if not run: return
        surface: pygame.surface = pygame.image.load(
            getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[self.imageIndex]), ".png")))))
        # scale
        surface = pygame.transform.scale(surface, self.rect.size)
        surface = pygame.transform.flip(surface, self.flipped.__getitem__(0), self.flipped.__getitem__(1))

        # rotation
        surface = pygame.transform.rotate(surface, self.angle)

        if self.tick < 30 and (self.tick % 5 == 0 or self.tick % 5 == 1 or self.tick % 5 == 2):
            surface = self.create_white_surf(surface, 255)
        
        # draw
        window.blit(surface, (self.rect.x, self.rect.y))

    def create_white_surf(self, surf, alpha):
        mask = pygame.mask.from_surface(surf)
        white_surface = mask.to_surface()
        white_surface.set_colorkey((0, 0, 0))
        white_surface.set_alpha(alpha)
        return white_surface

class platform(entity):
    player = None
    alpha = 255

    def start(self):
        if not run: return
        self.alpha = 255
        pygame.mouse.set_pos(self.rect.center)



    def fixedUpdate(self, player, entities):
        if not run: return
        if self.alpha <= 0:
            self.rect.x = 1000000
            return
        self.rect.x = pygame.mouse.get_pos().__getitem__(0) - self.rect.size.__getitem__(0) / 2
        self.rect.y = pygame.mouse.get_pos().__getitem__(1) - self.rect.size.__getitem__(1) / 2
        self.alpha -= 1

    def reset(self):
        self.alpha = 255

    def draw(self):
        if not run: return
        if self.alpha <= 0:
            return
        surface: pygame.surface = pygame.image.load(
            getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[self.imageIndex]), ".png")))))
        # scale
        surface = pygame.transform.scale(surface, self.rect.size)
        surface = pygame.transform.flip(surface, self.flipped.__getitem__(0), self.flipped.__getitem__(1))

        # rotation
        surface = pygame.transform.rotate(surface, self.angle)

        # alpha
        surface.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)

        # draw
        window.blit(surface, (self.rect.x, self.rect.y))


class orb(entity):
    player = None
    platform = None
    dir = 0

    def __init__(self, name, images, position, scale, flipped, angle, idx):
        self.name = name
        self.images = ["orb1", "orb2","orb3","orb4","orb5"]
        self.idx = idx
        surface: pygame.surface = pygame.image.load(
            getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[4]), ".png")))))
        scale = (surface.get_width() * scale.__getitem__(0), surface.get_height() * scale.__getitem__(1))

        xpos = position.__getitem__(0) + ScreenWidth / 2 - surface.get_width() / 2
        ypos = position.__getitem__(1) + ScreenHeight / 2 - surface.get_height() / 2

        self.rect = pygame.Rect(xpos, ypos, scale.__getitem__(0), scale.__getitem__(1))
        self.flipped = [flipped.__getitem__(0), flipped.__getitem__(1)]
        self.angle = angle
        self.imageIndex = 0
        self.start()
        self.update()

    def start(self):
        self.dir = random.randrange(-2, 3)

    def fixedUpdate(self, player, entities):
        if not run: return
        if self.rect.colliderect(player.rect):
            player.platform.reset()
            playSound("pickup", .3)
            entities.remove(self)
        self.rect.y += self.dir

        self.rect.scale_by(1, 1)

        if self.imageIndex < 4:
            self.imageIndex+=.2

        if self.rect.centerx > ScreenWidth + self.rect.size.__getitem__(
                0) / 2 or self.rect.centerx < 0 - self.rect.size.__getitem__(
            0) / 2 or self.rect.y + self.rect.size.__getitem__(1) < 0 or self.rect.y > ScreenHeight:
            entities.remove(self)


    def animate(self):
        if self.imageIndex + 1 >= len(self.images):
            self.imageIndex = 0
        else:
            self.imageIndex += 1

    def draw(self):
        if not run: return
        image = getResourcePath(str.__add__('Assets/', str(str.__add__(str(self.images[int(self.imageIndex)]), ".png"))))

        surface: pygame.surface = pygame.image.load(image)
        # scale
        surface = pygame.transform.scale(surface, self.rect.size)
        surface = pygame.transform.flip(surface, self.flipped.__getitem__(0), self.flipped.__getitem__(1))

        # rotation
        surface = pygame.transform.rotate(surface, self.angle)

        

        # draw
        window.blit(surface, (self.rect.x, self.rect.y))


class text(entity):
    t: str = "new text"
    pos = (0, 0)
    color = (240, 240, 240)
    size = 1
    bgColor = (115, 117, 117)

    def __init__(self, name, text, position, angle, size, idx, color=(240, 240, 240), bgColor=(115, 117, 117)):
        self.name = name
        self.t = text
        self.pos = position
        self.angle = angle
        self.idx = idx
        self.size = size

    def fixedUpdate(self, player, entities):
        if not run: return

    def draw(self):
        if not run: return
        fontPath = getResourcePath(str.__add__('Assets/', "small_bold_pixel-7.ttf"))
        fontObj = pygame.font.Font(fontPath, 16*self.size)
        textSurfaceObj = fontObj.render(self.t, True, self.color)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = self.pos
        textSurfaceObj = pygame.transform.rotate(textSurfaceObj, self.angle)
        window.blit(textSurfaceObj, textRectObj)

def setHighscore(var : int):
    global Highscore
    Highscore = var
    game_state["highscore"] = var
    save_game_state(game_state, 'save_game.pickle')

class timer(text):
    ticks = 0

    def start(self):
        self.ticks = 0

    def time_convert(self, sec):
        mins = sec // 60
        sec = sec % 60
        hours = mins // 60
        mins = mins % 60
        return "{0}:{1}:{2}".format(int(hours), int(mins), int(sec))

    def fixedUpdate(self, player, entities):
        if not run: return
        if IsGameOver: return
        global Highscore
        global game_state
        self.ticks += 1
        time_lapsed = int(self.ticks/FPS)
        if Highscore <= time_lapsed:
            setHighscore(time_lapsed)
        self.t = self.time_convert(time_lapsed)
class hstimer(text):

    def time_convert(self, sec):
        mins = sec // 60
        sec = sec % 60
        hours = mins // 60
        mins = mins % 60
        return "{0}:{1}:{2}".format(int(hours), int(mins), int(sec))

    def fixedUpdate(self, player, entities):
        if not run: return
        global Highscore
        global game_state
        game_state = load_game_state('save_game.pickle')
        Highscore = game_state['highscore']
        if GameStarted:
            self.color = (255, 230, 0)
        else:
            self.color = (0, 255, 255)

        if GameStarted:
            self.t = self.time_convert(Highscore)
        else:
            self.t = "HIGHSCORE => " + str(self.time_convert(Highscore))

# Save game state
class bullet(entity):
    player = None
    speed = 15
    tick = 0

    def onPlayerDamage(self, player):
        entities.remove(self)

    def fixedUpdate(self, player, entities):
        if not run: return
        if not entities.__contains__(self): return
        self.player = player
        if self.tick > 5 * FPS:
            entities.remove(self)
        else:
            self.tick += 1
        if self.rect.colliderect(self.player):
            hurtPlayer(player)
            if entities.__contains__(self): entities.remove(self)
        if self.angle == 0:
            self.rect.y -= self.speed
        elif self.angle == 90:
            self.rect.x += self.speed
        elif self.angle == 180:
            self.rect.y += self.speed
        elif self.angle == 270:
            self.rect.x -= self.speed


class beam(entity):
    tick = 0
    max = 50

    pos = (0, 0)
    f = (0, 0)
    ang = 0

    summoned = False

    def onPlayerDamage(self, player):
        entities.remove(self)

    def fixedUpdate(self, player, entities):
        if not run: return
        if not entities.__contains__(self): return
        if self.tick >= self.max/2:
            if not self.summoned:
                playSound("shoot", .1)
                entities.append(bullet("bullet", ["crow"], self.pos, (2, 2), self.f, self.ang,
                                len(entities) - 1))
                self.summoned = True
            if self.tick >= self.max:
                entities.remove(self)
            else:
                if (self.tick > self.max-4):
                    self.imageIndex+=1
                self.tick+=1
        else:
            self.tick += 1
            self.summoned = False


if __name__ == "__main__":
    main()
