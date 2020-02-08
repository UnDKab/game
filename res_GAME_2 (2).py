import pygame
from pygame import *
import sqlite3
import os
import random

enemy = ''
fight = False  # Короче, это були для сражений
atc_btn_active = False
prepare_fight = True
turn = True
gg_wp = True
act_btn_active = False

base_hp = 25

base_atc = 4

counted = 0

fight_id = 0  # А вот элемент проверки участия в бою

# размеры объектов
GAME_WIDTH = 1600
GAME_HEIGHT = 900
DISPLAY = (
    GAME_WIDTH, GAME_HEIGHT)
BACKGROUND_COLOR = '#006400'

PLATFORM_WIDTH = 22
PLATFORM_HEIGHT = 22
PLATFORM_COLOR = "#FF6222"

ENEMY_WIDTH = 18
ENEMY_HEIGHT = 18
ENEMY_COLOR = '#8B0000'

BOSS_WIDTH = 47
BOSS_HEIGHT = 70

PORTAL_WIDTH = 18
PORTAL_HEIGHT = 18
PORTAL_COLOR = '#0554f2'

MOVE_SPEED = 8
WIDTH = 16
HEIGHT = 18
COLOR = "#888888"


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.startX = x
        self.startY = y
        self.image = Surface((WIDTH, HEIGHT))
        self.image = image.load('data/GG.png')
        self.rect = Rect(x, y, WIDTH,
                         HEIGHT)

    def update(self, left, right, up, down, platforms, portals, enemys, count, boss):
        if left:
            self.xvel = -MOVE_SPEED
            self.image = image.load('data/GG_left.png')
        if right:
            self.xvel = MOVE_SPEED
            self.image = image.load('data/GG.png')
        if up:
            self.yvel = -MOVE_SPEED
        if down:
            self.yvel = MOVE_SPEED

        if not (
                left or right):
            self.xvel = 0
        if not (up or down):
            self.yvel = 0

        self.rect.y += self.yvel
        count = count
        self.collide(0, self.yvel, platforms, portals, enemys, count, boss)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms, portals, enemys, count, boss)
        return image

    def collide(self, xvel, yvel, platforms, portals, enemys, count, boss):
        for p in portals:
            if sprite.collide_rect(self, p):
                if count == 1:
                    count += 1
                    level_search(count)
                else:
                    count -= 1
                    level_search(count)

        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком

                if xvel > 0:  # если движется вправо
                    self.rect.right = p.rect.left  # то не движется вправо

                if xvel < 0:  # если движется влево
                    self.rect.left = p.rect.right  # то не движется влево

                if yvel > 0:  # если падает вниз
                    self.rect.bottom = p.rect.top  # то не падает вниз

                if yvel < 0:  # если движется вверх
                    self.rect.top = p.rect.bottom  # то не движется вверх

        for p in enemys:
            if sprite.collide_rect(self, p):
                global fight
                fight = True
                print('aeee')
                global enemy
                enemy = p
        # for p in boss:
        # if sprite.collide_rect(self, p):
        # битва с боссом


class Button:  # Клик
    def __init__(self, btn_coord_x, btn_coord_y):
        self.btn_coord_x = btn_coord_x
        self.btn_coord_y = btn_coord_y


class Atack_button(Button):  # Агрессивный клик
    def __init__(self):
        super().__init__(btn_coord_x=90, btn_coord_y=540)

    def load_image(self, name='Attack_button.jpg'):
        if not atc_btn_active:
            fullname = os.path.join('data', name)
            atc_btn_image = pygame.image.load(fullname).convert()
            return atc_btn_image
        else:
            fullname = os.path.join('data', 'Attack_button_pressed.jpg')
            atc_btn_image = pygame.image.load(fullname).convert()
            return atc_btn_image


class Action_button(Button):
    def __init__(self):
        super().__init__(btn_coord_x=90, btn_coord_y=540)

    def load_image(self, name='action_button.jpg'):
        if not act_btn_active:
            fullname = os.path.join('data', name)
            act_btn_image = pygame.image.load(fullname).convert()
            return act_btn_image
        else:
            fullname = os.path.join('data/Attack_button_pressed.jpg')
            act_btn_image = pygame.image.load(fullname).convert()
            return act_btn_image


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = image.load('data/stone_wall_texture.jpg')
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image = image.load('data/Enemy.jpg')
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BOSS_WIDTH, BOSS_HEIGHT))
        self.image = image.load('data/boss.png')
        self.rect = pygame.Rect(x, y, BOSS_WIDTH, BOSS_HEIGHT)


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = image.load('data/portal-2-sprite-portal.png')
        self.rect = pygame.Rect(x, y, PORTAL_WIDTH, PORTAL_HEIGHT)


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + GAME_WIDTH / 2, -t + GAME_HEIGHT / 2

    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - GAME_WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - GAME_HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return Rect(l, t, w, h)


def level_search(count):
    global entities
    global platforms
    global hero
    global portals
    global enemys
    global boss
    global total_level_width
    global total_level_height
    level_1 = [
        "-----------------------------------------------------------------------------------------------------------",
        "-   @        ----@                                         -                                              -",
        "-                                     @                    -  @               -                        @  -",
        "-----      --------                                        -                  -                           -",
        "-                                                          -           @      -              --------------",
        "-                               0---------                 ------------------------------       -        @-",
        "-   -----------------------------                                                               -        --",
        "-                                                                       -                               @--",
        "-       -         @                           ------------                                      -----------",
        "-           -       ------------                                    -           -               - @       -",
        "-                                                                  -            -               --        -",
        "-      ---            -          @                                                                        -",
        "-                                       ------------------------                      -             ---   -",
        "-- @--------------           --          ------------------------                                         --",
        "--  ---                                 ------------------------                   -           -          -",
        "-                 -----------------------------------------------                               -----     -",
        "-    -        -    -------------       @ ------------------------                 -               ------ @-",
        "-                                       ------------------------         -                            -----",
        "-      -        -                       ------------------------                          -----------------",
        "-                                                                                                         -",
        "-          -                                                   @                                          -",
        "-   -     -----------------------------------------------------------------                               -",
        "-                                                                                                         -",
        "-       -                                                                                                 -",
        "-                   @                                                                                     -",
        "-   -                                   -----------------------------------------------------------       -",
        "-      -------------------------------                                                                    -",
        "-                             -               -                     -                                     -",
        "-                                                                          -             -                -",
        "-        @      -        @                         -                                                      -",
        "-                             -                              @                         -                  -",
        "-         -                                -                       -                                      -",
        "-                                  @                      -                                               -",
        "-                      -                                                   @      -                       -",
        "-       @                               -                                                                 -",
        "-             -                                              -                                -           -",
        "-                  @       -                                                                              -",
        "-                                                                               -                         -",
        "-         -                          --------------------------------------------------------------       -",
        "-                  @                  -            -                                                      -",
        "-     -                               -                                                    ---            -",
        "-                 -                   -         @                      -                                  -",
        "-                                     -                                         ----                      -",
        "-        -                            -               -                                                   -",
        "-                       -------------------------------------------    -                                  -",
        "-            -                                                                                  @         -",
        "-                                                        -                                                -",
        "-     ---                           -  @        -                                        ---              -",
        "-                    -                                       -              -                             -",
        "-                         -                                                ---                 -          -",
        "-         @                              -              @                   -                             -",
        "-     -                                            -                        --             -              -",
        "-        -----------------                                                  @                             -",
        "-                                        -                                  --         -                  -",
        "-          -               -       @     -    -       --                                                  -",
        "-    --                                  -                                 --                             -",
        "-           ----                         -               ---                                              -",
        "-             ----                       --  @  @                                                      @  -",
        "-              -----------               -------                        --                          -------",
        "-   @                                    -                                                                -",
        "-                                        -               -----                           @                -",
        "-                 ------------------------                                           --                   -",
        "-    ---                                @-                       -                                        -",
        "-         @                              -                                                                -",
        "-          -          --------------------------------------------        ---------------------------------",
        "-                         -                                                                               -",
        "-    ---                   -     @                                                                        -",
        "-        -                -                        ----------------------------------------------------   -",
        "-        -       @        -                 @      -              -                     -                 -",
        "-@       -                --------------------------              -                     -                 -",
        "-        -                -                                       -      @              -                 -",
        "-        --               ------  ---                -                                                    -",
        "-         --              -     @  ---               -    @                    -                          -",
        "-          ---            -    -                     -                         -          @               -",
        "-            --           -    -----                 -                         -                          -",
        "-----------------------------0-----------------------------------------------------------------------------"]
    lexel_2 = [
        "-----------------------------------------------------------------------------------------------------------",
        "-                         -                                                ---                 -          -",
        "-         @                              -              @              @    -                             -",
        "-     -                                            -                        --             -    @   -     -",
        "-           --------------                                                  @                             -",
        "-                                        -                                  --         -     -            -",
        "-          -               -       @     -    -       --          @                                       -",
        "-    --                                  -                                 --               -             -",
        "-           ----                         -               ---                         -                    -",
        "-                                       ------------------------                                    ---   -",
        "-- @--------------                      ------------------------          -      -                       --",
        "--  ---                                 ------------------------                         -     -          -",
        "-                 -----------------------------------------------          @                    -----     -",
        "-         -       -------------       @ ------------------------                                  ------ @-",
        "-                    -                  ------------------------            -                         -----",
        "-    -                    -             ------------------------                          -----------------",
        "-      -                                         @                  -                                     -",
        "-                                       -               -                  -             -                -",
        "-        @      -        @                         -                                                      -",
        "-                             -     -                        @                   -     -               B --",
        "-         -                                -                       -                                     --",
        "-                                  @                      -                                              --",
        "-                      -                    -      -                       @      -          -         ----",
        "-       @                               -                                                            ------",
        "-             -                                 -            -                                -     ---   -",
        "-                  @       -        ----          -                   -                            --     -",
        "-                                              -                                -                ------   -",
        "-                               --             -                                        -------           -",
        "-                                                                                                         -",
        "-----------------------------------------------------------------------------------------------------------", ]

    entities = pygame.sprite.Group()
    platforms = []
    enemys = []
    boss = []
    portals = pygame.sprite.Group()
    hero = Player(555,
                  35)
    entities.add(hero)

    if count == 1:
        level = level_1
        total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
        total_level_height = len(level) * PLATFORM_HEIGHT  # высоту
    if count == 2:
        level = lexel_2
        total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
        total_level_height = len(level) * PLATFORM_HEIGHT  # высоту

    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == '@':
                enemy = Enemy(x, y)
                entities.add(enemy)
                enemys.append(enemy)
            if col == '0':
                portal = Portal(x, y)
                portals.add(portal)
            if col == 'B':
                bosss = Boss(x, y)
                entities.add(bosss)
                boss.append(bosss)

            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0


def main():
    global entities
    global platforms
    global hero
    global portals
    global count
    global enemys
    global boss
    global fight
    global prepare_fight
    global act_btn_active
    global atc_btn_active
    global turn
    global gg_wp
    global enemy
    global total_level_width
    global total_level_height
    pygame.init()
    pygame.display.set_caption('RPG GAME')
    screen = pygame.display.set_mode(DISPLAY, flags=pygame.FULLSCREEN)
    screen.fill(pygame.Color(BACKGROUND_COLOR))
    fon_surf = pygame.image.load('data/Grass_Export.jpg')
    fon_rect = fon_surf.get_rect()
    screen.blit(fon_surf, fon_rect)
    entities = pygame.sprite.Group()
    platforms = []
    count = 1
    atc_btn = Atack_button()
    act_btn = Action_button()

    level_search(count)

    running = True
    up = down = left = right = False

    timer = pygame.time.Clock()

    camera = Camera(camera_configure, total_level_width, total_level_height)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            if event.type == KEYDOWN and event.key == K_LEFT:
                left = True
            if event.type == KEYDOWN and event.key == K_RIGHT:
                right = True
            if event.type == KEYDOWN and event.key == K_UP:
                up = True
            if event.type == KEYDOWN and event.key == K_DOWN:
                down = True
            if event.type == KEYDOWN and event.key == K_0:
                if count == 1:
                    count += 1
                    level_search(count)
                else:
                    count -= 1
                    level_search(count)
            if event.type == KEYUP and event.key == K_RIGHT:
                right = False
            if event.type == KEYUP and event.key == K_LEFT:
                left = False
            if event.type == KEYUP and event.key == K_UP:
                up = False
            if event.type == KEYUP and event.key == K_DOWN:
                down = False
        if not fight:
            screen.blit(fon_surf, fon_rect)
            hero.update(left, right, up, down, platforms, portals,
                        enemys, count, boss)
            camera.update(hero)
            for e in entities:
                screen.blit(e.image, camera.apply(e))
            for e in portals:
                screen.blit(e.image, camera.apply(e))
        else:
            if prepare_fight:
                enemy_count = random.randint(1, 3)
                count = 1
                enemies = []
                for _ in range(enemy_count):
                    stats = [random.randint(15, 20), random.randint(1, 4), count]
                    count += 1
                    enemies.append(stats)
                prepare_fight = False
                global base_hp, base_atc
                main_player_hp = base_hp
                main_player_atc = base_atc

            screen.fill((0, 0, 0))
            screen.blit(atc_btn.load_image(), (90, 510), area=None,
                        special_flags=0)
            screen.blit(act_btn.load_image(), (300, 510), area=None,
                        special_flags=0)
            for i in range(len(enemies)):
                if enemies[i][0] > 0:
                    pygame.draw.rect(screen, pygame.Color('Red'),
                                     (210 + i * 100, 300, 40, 40), 2)
                    font_hp = pygame.font.SysFont('arial', 36)
                    enemy_hp = font_hp.render(str(enemies[i][0]), 1,
                                              (180, 0, 0))
                    screen.blit(enemy_hp, (50 + i * 50, 100))
            font_hp = pygame.font.SysFont('arial', 36)
            hp_player = font_hp.render(str(main_player_hp), 1, (180, 0, 0))
            screen.blit(hp_player, (10, 50))
            pygame.display.flip()
            if not atc_btn_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    fight_coord_x = event.pos[0]
                    fight_coord_y = event.pos[1]
                    if 90 < fight_coord_x < 240 and 510 < fight_coord_y < 570:
                        atc_btn_active = True
            if atc_btn_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    fight_coord_x = event.pos[0]
                    fight_coord_y = event.pos[1]
                    for i in enemies:
                        if (fight_coord_x - 210) // 100 + 1 == i[
                            2] and 300 < fight_coord_y < 340 and i[0] > 0:
                            i[0] = i[0] - main_player_atc
                            atc_btn_active = False
                            turn = False
            if not act_btn_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    fight_coord_x = event.pos[0]
                    fight_coord_y = event.pos[1]
                    if 300 < fight_coord_x < 450 and 510 < fight_coord_y < 570:
                        act_btn_active = True
            if act_btn_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    fight_coord_x = event.pos[0]
                    fight_coord_y = event.pos[1]
                for i in enemies:
                    if (fight_coord_x - 210) // 100 + 1 == i[
                        2] and 300 < fight_coord_y < 340 and i[0] > 0:
                        i[0] = i[0] - 0
                        main_player_hp += (main_player_atc * 3)
                        act_btn_active = False
                        turn = False
            counted = 0
            for i in enemies:
                if i[0] > 0:
                    counted = 1
            if counted == 0:
                fight = False
                prepare_fight = True
                enemys.remove(enemy)
                base_atc += 1
                base_hp += 5

            if fight and not turn:
                for i in enemies:
                    if i[0] > 0:
                        main_player_hp = main_player_hp - i[1]
                turn = True
            if main_player_hp < 0:
                gg_wp = False
                fight = False
                turn = False
                fight = False
                prepare_fight = True
            elif not gg_wp:
                screen.fill((0, 0, 0))
                font_hp = pygame.font.SysFont('arial', 72)
                hp_player = font_hp.render('Game over', 1, (180, 0, 0))
                screen.blit(hp_player, (10, 50))
        pygame.display.flip()
        timer.tick(60)


if __name__ == "__main__":
    main()
