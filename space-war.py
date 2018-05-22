# Imports
import pygame
import random

# Initialize game engine
pygame.init()

# Window
WIDTH = 1000
HEIGHT = 650
SIZE = (WIDTH, HEIGHT)
TITLE = "Space War"
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption(TITLE)

# Timer
clock = pygame.time.Clock()
refresh_rate = 60

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255,69,0)

#fonts
FONT_SM = pygame.font.Font("fonts/space_age.ttf",15)
FONT_MD = pygame.font.Font("fonts/space_age.ttf",25)
FONT_LG = pygame.font.Font("fonts/space_age.ttf",96)
FONT_XL = pygame.font.Font("fonts/Prisma.ttf", 96)


# Images
battleground = pygame.image.load('pics/battleground.png')
turtle_left = pygame.image.load('pics/turt.png')
turtle_right = pygame.transform.flip(turtle_left,1,0)
turtle_list = [turtle_left,turtle_right]

turtle_left_hurt = pygame.image.load('pics/turtle_hurt.png')
turtle_right_hurt = pygame.transform.flip(turtle_left_hurt,1,0)
turtle_hurt_list = [turtle_left_hurt,turtle_right_hurt]

background = pygame.image.load('pics/space.png')
ufo = pygame.image.load('pics/ufo.png')
big_ufo = pygame.image.load('pics/big_ufo.png')
shell = pygame.image.load('pics/shell.png')
yellow_beam = pygame.image.load('pics/yellow_beam.png')

fire = pygame.image.load('pics/fire.png')
fire2 = pygame.image.load('pics/fire2.png')
fire3 = pygame.image.load('pics/fire3.png')

flames = [fire,fire3,fire2]

metal = pygame.image.load('pics/metal.png')

boss = pygame.image.load('pics/boss.png')

#Sounds
cluck = pygame.mixer.Sound('sounds/cluck.ogg')
track = 'sounds/track.wav'
shoot = pygame.mixer.Sound('sounds/shoot.ogg')

#stages
START = 1
PLAYING = 2
WIN = 3
LOSE = 4
UPGRADE = 5
CLEARED = 6

# Game classes
class Ship(pygame.sprite.Sprite):

    def __init__(self, x, y, image_list):
        super().__init__()

        self.cooldown = [30,30]

        self.shield = 3
        self.speed = 4
        self.direc = 0

        self.image_list = image_list
        self.image = self.image_list[self.direc]
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def move_left(self):
        self.rect.x -= self.speed
        self.direc = 0

    def move_right(self):
        self.rect.x += self.speed
        self.direc = 1

    def shoot(self,player):
        las = Laser(yellow_beam)

        las.rect.centerx = self.rect.centerx
        las.rect.centery = self.rect.top

        if self.cooldown[0] == self.cooldown[1]:
            lasers.add(las)
            shoot.play()
            player.score -= 5
            self.cooldown[0] = 0

    def update(self):
        self.image = self.image_list[self.direc]


        if self.cooldown[0] != self.cooldown[1]:
            self.cooldown[0] += 1

        if self.rect.left <= 0:
            self.rect.left = 0

        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH

        hit_list = pygame.sprite.spritecollide(self,bombs,True)

        for hit in hit_list:
            self.shield -= 1
            
            if self.shield == 2:
                self.image_list = turtle_hurt_list

        hit_list = pygame.sprite.spritecollide(self,mobs,True)

        for hit in hit_list:
            self.shield = 0

        if self.shield == 0:
            self.kill()

class Laser(pygame.sprite.Sprite):

    def __init__(self, image):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()

        self.speed = 6

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom <= 0:
            self.kill()

class Mob(pygame.sprite.Sprite):
    def __init__(self, x, y, image,shield):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(image)
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.shield = shield
        self.speed = 5

    def update(self,lasers,player):
        hit_list = pygame.sprite.spritecollide(self,lasers,True,pygame.sprite.collide_mask)

        if len(hit_list) > 0:
            cluck.play()
            self.shield -= 1

        if self.shield <= 0:
            self.kill()
            player.score += 100
            cluck.play()

    def shoot(self):
        bomb = Bomb(flames)

        bomb.rect.centerx = self.rect.centerx
        bomb.rect.centery = self.rect.bottom
        bombs.add(bomb)

class Bomb(pygame.sprite.Sprite):

    def __init__(self, image_list):
        super().__init__()

        self.ticks = 0
        self.frame = 0
        self.image_list = image_list
        self.image = self.image_list[self.frame]

        self.rect = self.image.get_rect()

        self.speed = 6

    def update(self):
        self.ticks += 1
        self.frame = self.ticks//10

        if self.frame > 2:
            self.frame = 0
            self.ticks = 0

        self.image = self.image_list[self.frame]
        self.rect.y += self.speed
        if self.rect.top >= HEIGHT:
            self.kill()

class Fleet:

    def __init__(self,mobs):
        self.mobs = mobs
        self.bomb_rate = 60
        self.speed = 6
        self.moving_right = False

    def move(self):
        reverse = False

        if self.moving_right:
            for m in mobs:
                m.rect.x += self.speed
                if m.rect.right >= WIDTH:
                    reverse = True

        else:
            for m in mobs:
                m.rect.x -= self.speed
                if m.rect.left <= 0:
                    reverse = True

        if reverse:
            self.moving_right = not self.moving_right

            for m in mobs:
                m.rect.y += 32
                m.image = pygame.transform.flip(m.image,1,0)
                m.shoot()

    def choose_bomber(self):
        rand = random.randrange(0,self.bomb_rate)
        all_mobs = mobs.sprites()

        if len(all_mobs) > 0 and rand == 0:
            return random.choice(all_mobs)
        else:
            return None

    def update(self):
        self.move()

        bomber = self.choose_bomber()
        if bomber != None:
            bomber.shoot()

#sprite groups
player = pygame.sprite.GroupSingle()
mobs = pygame.sprite.Group()
lasers = pygame.sprite.Group()
bombs = pygame.sprite.Group()

# Game loop
done = False

#music
pygame.mixer.music.load(track)
pygame.mixer.music.play()

#helper functions
def get_monsters(mobs):
    global boss_health
    mob1 = Mob(150,80,ufo,1)
    mob2 = Mob(300,80,ufo,1)
    mob3 = Mob(450,80,ufo,1)
    mob4 = Mob(600,80,ufo,1)
    mob5 = Mob(750,80,ufo,1)
    mob6 = Mob(150,0,big_ufo,3)
    mob7 = Mob(300,0,big_ufo,3)
    mob8 = Mob(450,0,big_ufo,3)
    mob9 = Mob(600,0,big_ufo,3)
    mob10 = Mob(750,0,big_ufo,3)
    boss_man = Mob(450,0,boss,30)

    mob_options = [mob1,mob2,mob3,mob4,mob5,mob6,mob7,mob8,mob9,mob10]
    
    if level == len(mob_options) + 1:
        mobs.add(boss_man)
        
    else:
        for i in range(0,level):
            mobs.add(mob_options[i])

def reset_monsters():
    global mobs,fleet

    mobs.empty()
    get_monsters(mobs)
    
    fleet = Fleet(mobs)

def reset_player():
    global ship

    ship = Ship(WIDTH/2, HEIGHT - 75,turtle_list)
    player.add(ship)
    player.score = 0

def setup():
    global stage,level,score_req,max_lvl
    stage = START
    level = 1
    score_req = 300
    max_lvl = 10

    lasers.empty()
    bombs.empty()

    reset_player()

    reset_monsters()

def upgrade(choice):
    if choice == "q":
        ship.speed += 10
    else:
        ship.cooldown[1] -= 5
        if ship.cooldown[1] <= 0:
            ship.cooldown[1] = 1
        ship.cooldown[0] = ship.cooldown[1]

def show_stats(player):
    score_text = FONT_SM.render(str(player.score),1,WHITE)
    lvl_text = FONT_SM.render("Level: " + str(level),1,WHITE)
    speed = FONT_SM.render("Speed: " + str(ship.speed),1,WHITE)
    reload = FONT_SM.render("Reload Time: " + str(60/ship.cooldown[1]) + "/s",1,WHITE)

    x = 25
    for i in range(0,ship.shield):
        screen.blit(shell,[x,50])
        x += 50
    screen.blit(score_text, [32,32])
    screen.blit(lvl_text,[800,32])
    screen.blit(speed,[800,50])
    screen.blit(reload,[790,68])


def title_screen():
    screen.blit(battleground,[0,0])
    title_text = FONT_XL.render("Space War!", 1, WHITE)
    screen.blit(title_text, [WIDTH//2 - 275, 80])

def end_screen():
    text1 = FONT_XL.render("You Win!", 1, WHITE)
    text2 = FONT_XL.render("Press 'r' to restart",1,WHITE)
    if ship.shield <= 0:
        text1 = FONT_XL.render("You Died!", 1, WHITE)
    screen.blit(text1, [WIDTH//2 - 250, 80])
    screen.blit(text2, [WIDTH//2 - 430, 250])

def upgrade_screen():
    screen.blit(metal,[200,300])
    text1 = FONT_MD.render("UPGRADE!", 1, ORANGE)
    text2 = FONT_MD.render("'Q' for speed.",1,ORANGE)
    text3 = FONT_MD.render("'E' for bullet reload.",1,ORANGE)

    screen.blit(text1, [WIDTH//2 - 50, 310])
    screen.blit(text2, [WIDTH//2 - 200, 375])
    screen.blit(text3, [WIDTH//2 - 200, 450])

setup()
while not done:
    # Event processing (React to key presses, mouse clicks, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if stage == START:
                if event.key == pygame.K_SPACE:
                    stage = PLAYING
            if stage == PLAYING:
                if event.key == pygame.K_SPACE:
                    ship.shoot(player)
            if stage == LOSE or stage == WIN:
                if event.key == pygame.K_r:
                    setup()
            if stage == UPGRADE:
                if event.key == pygame.K_q:
                    upgrade("q")
                    score_req  = score_req * 2
                    stage = PLAYING
                if event.key == pygame.K_e:
                    upgrade("e")
                    score_req  = score_req * 2
                    stage = PLAYING

    if stage == PLAYING:
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_LEFT]:
            ship.move_left()
        elif pressed[pygame.K_RIGHT]:
            ship.move_right()

    #processing
    if stage == PLAYING:
        player.update()
        mobs.update(lasers,player)
        bombs.update()
        fleet.update()
        lasers.update()

        if ship.shield <= 0:
            stage = LOSE
        if len(mobs) == 0:
            stage = CLEARED
        if player.score >= score_req:
            stage = UPGRADE

    # Drawing code
    screen.fill(BLACK)
    screen.blit(background,[0,0])

    player.draw(screen)
    bombs.draw(screen)
    lasers.draw(screen)
    mobs.draw(screen)
    show_stats(player)

    if stage == UPGRADE:
        upgrade_screen()

    if stage == START:
        title_screen()

    if stage == CLEARED:
        level += 1
        if level > max_lvl + 1:
            stage = WIN
        else:
            reset_monsters()
            stage = PLAYING

    if stage == LOSE or stage == WIN:
        end_screen()


    # Update screen (Actually draw the picture in the window.)
    pygame.display.flip()

    # Limit refresh rate of game loop
    clock.tick(refresh_rate)

# Close window and quit
pygame.quit()
