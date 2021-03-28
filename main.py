#Coursework Game
import pygame as pg
from random import *
from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        #initialise game window etc.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("My Game")
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()


    def load_data(self):
        global img_dir
        #load highscore
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img') #sets folder wher images are found
        file = open(path.join(self.dir, HS_FILE), 'r')
        highScores = file.readlines()
        list = []
        for score in highScores:   # reads current highscore from text file
            list.append(score)
        try:
            self.highscore = int(list[0])
        except:
            self.highscore = 0

        #load spritesheet for game
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        #load background_image image
        self.background_image = pg.image.load(path.join(img_dir, "bg.jpg")).convert()
        #load start screen image
        self.start_screen = pg.image.load(path.join(img_dir, "start screen.jpg")).convert()
        #load game over image
        self.gameover_screen = pg.image.load(path.join(img_dir, "go screen.jpg")).convert()
        #load sounds
        self.snd_dir = path.join(self.dir, 'snd')
        self.flying_sound = pg.mixer.Sound(path.join(self.snd_dir, "flysound.wav"))


    def new(self):
        #Start a new game
        self.score = 0
        #Creating Sprite Groups
        self.all_sprites = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.bottom_platforms = pg.sprite.Group()
        self.top_platforms = pg.sprite.Group()
        self.scores = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        #Instantiating the Player, the first two obstacles, the bottom platform and the first score-point
        self.player = Player(self)
        self.bottom_platform = BottomPlatform(0, HEIGHT-40, WIDTH, 40)
        self.top_platform = TopPlatform(0, -40, WIDTH, 40)
        #self.top_platform = BottomPlatform(0, -40, WIDTH, 40)
        o = Obstacle(self, 350, 200)
        o_2 = Obstacle(self, 600, 400)
        #adding all objects to their respective sp rite groups
        self.bottom_platforms.add(self.bottom_platform)

        self.top_platforms.add(self.top_platform)

        self.all_sprites.add(self.player)
        self.all_sprites.add(o)
        self.all_sprites.add(o_2)

        self.obstacles.add(o)
        self.obstacles.add(o_2)

        #load music for the game
        pg.mixer.music.load(path.join(self.snd_dir, "throughspace.ogg"))
        #keeping track of the last time an enemy spawned

        self.run()


    def run(self):
        #Game Loop
        pg.mixer.music.play(loops=-1) #makes music loop forever
        self.playing = True
        while self.playing:           #main game loop
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)


    def update(self):
        global FPS
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        #Game Loop - Update
        self.all_sprites.update()
        self.bottom_platform.update()
        self.scores.update()
        self.powerups.update()
        self.top_platforms.update()
        for sprite in self.enemies:
            sprite.update()

        #check if player hits bottom platform only while falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.bottom_platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top + 1
                self.player.vel.y = 0

        #checks if player hits the top of the screen while flying
        if self.player.vel.y < 0:
            hits8 = pg.sprite.spritecollide(self.player, self.top_platforms, False)
            if hits8:
                self.player.pos.y = hits8[0].rect.bottom + 50
                self.player.vel.y = 0

        #checks for collions between player and any obstacle - if so, die!
        hits2 = pg.sprite.spritecollide(self.player, self.obstacles, False, pg.sprite.collide_mask)
        if hits2:
            FPS = 60
            self.playing = False

        #checks for collision  between player and enemies
        hits7 = pg.sprite.spritecollide(self.player, self.enemies, False, pg.sprite.collide_mask)
        if hits7:
            self.playing = False

        #if player reaches first third of screen, all sprites moved
        if self.player.rect.right >= WIDTH / 3 and self.player.vel.x > 0:
            self.player.pos.x -= max(abs(self.player.vel.x), 2)
            for obs in self.obstacles:
                obs.rect.right -= max(abs(self.player.vel.x), 2)
                if obs.rect.right <= WIDTH -1100:
                    obs.kill()
            for score in self.scores:
                score.rect.right -= max(abs(self.player.vel.x), 2)
                if score.rect.right <= WIDTH -1100:
                    score.kill()
            for pow in self.powerups:
                pow.rect.right -= max(abs(self.player.vel.x), 2)
                if pow.rect.right <= WIDTH -1100:
                    pow.kill()
            for mob in self.enemies:
                mob.rect.right -= max(abs(self.player.vel.x), 2)
                if mob.rect.right <= WIDTH -1100:
                    mob.kill()


        #spawns new obstacles off side of screen
        while len(self.obstacles) < 4:
            o = Obstacle(self, self.player.rect.right + 900,  randrange(50, 500))
            for i in self.obstacles:
                hits4 = pg.sprite.spritecollide(i, self.obstacles, False)
                if hits4:
                    o.kill()
            self.all_sprites.add(o)
            self.obstacles.add(o)


        #rect overlaps another score
        for i in self.scores:
            hits4 = pg.sprite.spritecollide(i, self.powerups, False)
            if hits4:
                i.kill()


        #collision detection between player and scores
        for score in self.scores:
            hits5 = pg.sprite.collide_rect(self.player, score)
            if hits5:
                self.score += 1
                FPS += 5
                score.obs.kill()
                score.kill()

        #checks collision between player and powerup
        for pow in self.powerups:
            hits6 = pg.sprite.collide_rect(self.player, pow)
            hits7 = pg.sprite.spritecollide(pow, self.obstacles, False)
            #adds 3 to score and kills obstacle which is assigned to the powerup
            if hits6 and not hits7:
                self.score += 3
                pow.kill()
                o = Obstacle(self, self.player.rect.right + 1500,  randrange(50, 500))
                self.all_sprites.add(o)
                self.obstacles.add(o)
                o2 = Obstacle(self, self.player.rect.right + 1250,  randrange(50, 500))
                self.all_sprites.add(o2)
                self.obstacles.add(o2)


    def events(self):
        #Game Loop - Events
        for event in pg.event.get():
            #check for window close
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False


    def draw(self):
         #Game Loop - Draw
         self.screen.fill(BLACK)
         self.screen.blit(self.background_image, [0, 0])
         self.all_sprites.draw(self.screen)
         self.powerups.draw(self.screen)
         self.bottom_platforms.draw(self.screen)
         self.top_platforms.draw(self.screen)
         self.screen.blit(self.player.image, self.player.rect)
         self.draw_text(str(self.score), 30, WHITE, WIDTH - 40, 15) #adds score to in-game view

         pg.display.flip()


    def draw_text(self, text, size, colour, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


    def show_start_screen(self):
         pg.mixer.music.load(path.join(self.snd_dir, "menumusic.ogg"))
         pg.mixer.music.play(loops=-1)
         self.screen.blit(self.start_screen, [0, 0])
         self.draw_text("highscore: " + str(self.highscore),  25, BLACK, WIDTH/2, 100)
         pg.display.flip()
         self.wait_for_key()
         pg.mixer.music.fadeout(500)


    def show_go_screen(self):
         if not self.running:
            return
         pg.mixer.music.load(path.join(self.snd_dir, "menumusic.ogg"))
         pg.mixer.music.play(loops=-1)
         self.screen.blit(self.gameover_screen, [0, 0])
         self.draw_text("score: " + str(self.score), 30, BLACK, WIDTH/2, HEIGHT/2+120)
         if self.score > self.highscore:
             self.highscore = self.score
             self.draw_text("NEW HIGHSCORE", 30, BLACK, WIDTH/2, HEIGHT/2 + 50)
             with open(path.join(self.dir, HS_FILE), 'w') as f:
                 f.write(str(self.score))
         else:
             self.draw_text("highscore: " + str(self.highscore), 30, BLACK, WIDTH/2, HEIGHT/2 + 50)
         pg.display.flip()
         self.wait_for_key()
         pg.mixer.music.fadeout(500)


    def wait_for_key(self):
        #simple method that waits for mouse to be cliked
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.MOUSEBUTTONUP:
                    waiting = False


g = Game()
g.show_start_screen()
while g.running:
    pg.event.get()
    g.new()
    g.show_go_screen()

pg.quit()
