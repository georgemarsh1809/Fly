#Sprite classes for Run
from settings import *
import pygame as pg
vec = pg.math.Vector2
from os import path
from random import *



class Player(pg.sprite.Sprite):
    def __init__(self, game):
        #initialises all attributes for the player, sets vectors for gravity and movement and creates image
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        super().__init__()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.pos = vec(-25, HEIGHT-150)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)


    def load_images(self):
        #different images for different frames of different animations
        self.standing_frames = [self.game.spritesheet.get_image(0, 1559, 216, 101),
                                self.game.spritesheet.get_image(0, 1456, 216, 101)]

        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

        self.walking_frames_r = [self.game.spritesheet.get_image(0, 1456, 216, 101)]

        for frame in self.walking_frames_r:
            frame.set_colorkey(BLACK)

        self.walking_frames_l = []

        for frame in self.walking_frames_r:
            self.walking_frames_l.append(pg.transform.flip(frame, True, False))
            frame.set_colorkey(BLACK)

        self.jumping_frame = self.game.spritesheet.get_image(382, 510, 182, 123)
        self.jumping_frame.set_colorkey(BLACK)


    def jump(self):
        self.vel.y = -PLAYER_JUMP_POWER
        self.jumping = True


    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        self.acc.x = PLAYER_ACC
        if keys[pg.K_SPACE]:
            self.jump()
        else:
            self.jumping = False

        #apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        #equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        self.rect.midbottom = self.pos


    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        #animations
        #while standing still:
        if not self.walking and not self.jumping:
            if now - self.last_update > 500:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        #while walking:
        if self.walking:
            if now - self.last_update > 300:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        #if jumping
        if self.jumping:
            self.image = self.jumping_frame

        self.mask = pg.mask.from_surface(self.image)


class Spritesheet:
    #utility class for loading/parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, w, h):
        #grab an image out of spritesheets
        image = pg.Surface((w, h))
        image.blit(self.spritesheet, (0, 0), (x, y, w, h))
        image = pg.transform.scale(image, (w//2, h//2))
        return image


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        super().__init__()
        images = [self.game.spritesheet.get_image(232, 1288, 200, 100)]
        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.game.powerups.update()
        if randrange(100) < POW_RATE:      #Creates an instance of a powerup, depending on a probability calculation
             p = PowerUp(self.game, self)
             self.game.all_sprites.add(p)
             self.game.powerups.add(p)
        if randrange(100) < ENEMY_FREQ:    #Creates an instance of a enemy, depending on a probability calculation
            e = Enemy(self.game)
            self.game.all_sprites.add(e)
            self.game.enemies.add(e)
        if randrange(100) < SCORE_FREQ:    #Creates an instance of a score, depending on a probability calculation
             s = Score(self.game, self)
             self.game.all_sprites.add(s)
             self.game.scores.add(s)


class Score(pg.sprite.Sprite):
    def __init__(self, game, obs):
        #initialises all attributes for scores
        super().__init__()
        self.game = game
        self.obs = obs
        self.image = self.game.spritesheet.get_image(829, 0, 66, 84)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.obs.rect.centerx
        self.rect.y = self.obs.rect.top - 50


class BottomPlatform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        #bottom platformm that goes above screen to stop player going outside boundaries of window
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(DARK_GREY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class TopPlatform(pg.sprite.Sprite):
    #top platformm that goes above screen to stop player going outside boundaries of window
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.bottom = x
        self.rect.y = y


class PowerUp(pg.sprite.Sprite):
    def __init__(self, game, obs):
        #these are the score points that are worth 3
        super().__init__()
        self.game = game
        self.obs = obs
        self.image = self.game.spritesheet.get_image(820, 1805, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.obs.rect.centerx
        self.rect.y = self.obs.rect.top - 15

    def update(self):
        self.rect.bottom = self.obs.rect.top - 15
        if not self.game.obstacles.has(self.obs):
            self.kill()


class Enemy(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.load_image_enemy()
        super().__init__()
        self.image = pg.transform.flip(self.frames[0], True, False)
        self.rect = self.image.get_rect()
        self.rect.x = self.game.player.rect.right + 1000
        self.vx = -1
        self.rect.bottom = self.game.bottom_platform.rect.top -10

    def load_image_enemy(self):
        self.frames = [self.game.spritesheet.get_image(566, 510, 122, 139)]

        self.walk_frames = []

        for frame in self.frames:
            self.walk_frames.append(pg.transform.flip(frame, True, False))
            frame.set_colorkey(BLACK)

    def update(self):
        #keeps enemies moving
        self.rect.x += self.vx
        self.mask = pg.mask.from_surface(self.image)
