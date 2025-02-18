# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pygame",
# ]
# ///
import asyncio
import math
import os
import sys
import pygame
import random

__version__ = '2025.2.8'

PYGAME_VERSION = pygame.version.ver

PY2 = int(sys.version.split('.').pop(0)) == 2

DEBUG = True

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

EVENT_RECOVER_USER = pygame.USEREVENT + 1
EVENT_DECREASE_TIME_SUPER = pygame.USEREVENT + 2
EVENT_SPEEDUP_ENEMIES = pygame.USEREVENT + 3
EVENT_PLAYER_RECOVER_INJURY = pygame.USEREVENT + 4
EVENT_GAME_OVER = pygame.USEREVENT + 5
EVENT_CREATE_ITEM = pygame.USEREVENT + 6
EVENT_PLAYER_BECOME_NORMAL = pygame.USEREVENT + 7

FPS = 60
OPTIMAL_MS_PER_TICK = int(1000 / FPS)

SHOTS = 50
LIVES = 5

BASE_ENEMY_VELOCITY = 0.3  # Adjust to speed up the base speed

if 'GAME_PATH' not in globals():
    GAME_PATH = os.path.dirname(os.path.realpath(__file__))


class ItemType:
    SLIME = 1
    LIFE = 2
    SUPER = 3


class Block(pygame.sprite.Sprite):
    """ This class represents the block. """

    def __init__(self, color):
        if PY2:
            super(Block, self).__init__()
        else:
            super().__init__()

        self.image = pygame.Surface([20, 15])
        self.image.fill(color)

        self.rect = self.image.get_rect()


class Enemy(pygame.sprite.Sprite):
    """ This class represents the block. """

    def __init__(self, image, game):
        if PY2:
            super(Enemy, self).__init__()
        else:
            super().__init__()
        self.game = game
        self.image = image
        self.image.set_colorkey((0, 0, 0, 255))
        self.rect = self.image.get_rect()
        random_extra_speed_factor = (random.randint(1, 30) / 100) + 1
        game_enemy_velocity = self.game.enemy_speedup_factor + 1
        self.enemy_velocity = BASE_ENEMY_VELOCITY * random_extra_speed_factor * game_enemy_velocity
        self.pos_y = self.rect.y
        self.pos_x = self.rect.x

    def reset_pos(self):
        self.rect.y = random.randrange(-1200, -20)
        self.rect.x = random.randrange(0, SCREEN_WIDTH)

    def update(self):
        self.pos_y += self.game.pace * self.enemy_velocity
        self.rect.y = self.pos_y
        self.rect.x = self.pos_x

        if self.pos_y > SCREEN_HEIGHT - 10:
            self.game.enemy_list.remove(self)
            self.game.all_sprites_list.remove(self)
            if self.game.super_time_secs_left > 0:
                return
            else:
                self.game.lives -= 1
                self.game.player.injury()


class Item(pygame.sprite.Sprite):
    """ This class represents the item. """

    def __init__(self, game, item_velocity=0.5, item_type=ItemType.SLIME):
        if PY2:
            super(Item, self).__init__()
        else:
            super().__init__()

        self.game = game
        self.item_type = item_type
        if item_type == ItemType.SLIME:
            self.image = self.game.IMG_EXTRA_SLIME
        if item_type == ItemType.LIFE:
            self.image = self.game.IMG_EXTRA_LIFE
        if item_type == ItemType.SUPER:
            self.image = self.game.IMG_EXTRA_SUPER

        self.rect = self.image.get_rect()
        self.item_velocity = item_velocity
        self.pos_y = self.rect.y
        self.pos_x = self.rect.x
        self.reset_pos()

    def reset_pos(self):
        self.rect.y = random.randint(-1200, -20)
        self.rect.x = random.randint(50, SCREEN_WIDTH-50)
        self.pos_y = self.rect.y
        self.pos_x = self.rect.x

    def update(self):
        self.pos_y += self.game.pace * self.item_velocity
        self.rect.y = self.pos_y
        self.rect.x = self.pos_x

        if self.pos_y > SCREEN_HEIGHT - 10:
            self.game.item_list.remove(self)
            self.game.all_sprites_list.remove(self)
            self.game.item_scheduled = False

    def player_caught(self):
        if self.item_type == ItemType.SLIME:
            self.game.shots_left += 30
        elif self.item_type == ItemType.LIFE:
            if self.game.lives < 5:
                self.game.lives += 1
        elif self.item_type == ItemType.SUPER and self.game.super_time_secs_left == 0:
            self.game.super_time_secs_left = 30
            self.game.player.become_super()
            pygame.time.set_timer(EVENT_DECREASE_TIME_SUPER, 1000)
            pygame.time.set_timer(EVENT_PLAYER_BECOME_NORMAL, 30000)
        self.game.item_scheduled = False


class Player(pygame.sprite.Sprite):
    """ This class represents the Player. """

    def __init__(self, image, game):
        if PY2:
            super(Player, self).__init__()
        else:
            super().__init__()
        self.game = game
        self.org_image = image.copy()
        self.image = image.copy()
        self.image.set_colorkey((0, 0, 0, 255))
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.added_velocity = 0

    def injury(self):
        self.game.SFX_OUCH.play()
        color_image = pygame.Surface(self.image.get_size()).convert_alpha()
        color_image.fill((250, 0, 0))
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.time.set_timer(EVENT_PLAYER_RECOVER_INJURY, 500)
        print('Injury')

    def restore_player_from_injury(self):
        if self.game.super_time_secs_left > 0:
            return
        self.image = self.org_image.copy()
        self.image.set_colorkey((0, 0, 0, 255))
        pygame.time.set_timer(EVENT_PLAYER_RECOVER_INJURY, 0)
        print('Restore from injury')

    def player_become_normal(self):
        pygame.time.set_timer(EVENT_PLAYER_BECOME_NORMAL, 0)
        self.added_velocity = 0
        self.image = self.org_image.copy()
        self.image.set_colorkey((0, 0, 0, 255))
        print('Became normal')

    def become_super(self):
        self.game.SFX_SUPER.play()
        self.added_velocity = 2
        color_image = pygame.Surface(self.image.get_size()).convert_alpha()
        color_image.fill((0, 196, 0))
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        print('Became super')

    def update(self):
        self.rect.x += self.change_x
        right_side = SCREEN_WIDTH - self.rect.width
        if self.rect.x >= right_side:
            self.change_x = 0
            self.rect.x = right_side
        left_side = self.rect.width
        if self.rect.x <= left_side - self.rect.width:
            self.change_x = 0

    def go_left(self):
        self.change_x = (-2 - self.added_velocity) * self.game.pace

    def go_right(self):
        self.change_x = (2 + self.added_velocity) * self.game.pace


class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet . """

    def __init__(self, image, game):
        if PY2:
            super(Bullet, self).__init__()
        else:
            super().__init__()
        self.game = game
        self.image = image
        self.image.set_colorkey((0, 0, 0, 255))
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y -= 2 * self.game.pace


def xy_distance(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


def is_far_away(x1, y1, current_pos_list, screen_margins=50):
    far_away = True
    for x2, y2 in current_pos_list:
        if xy_distance(x1, y1, x2, y2) < 50:
            far_away = False
        if x1 < screen_margins or x1 >= SCREEN_WIDTH - screen_margins:
            far_away = False
    return far_away


def start_music():
    pygame.mixer.music.load(GAME_PATH + "/sfx/rainingbullets_smaller.ogg")
    pygame.mixer.music.play(-1)


class Game:

    def __init__(self):
        self.done = False
        self.clock = pygame.time.Clock()
        self.pace = 0  # The tick between frames to keep consistent speed across devices
        self.lives = LIVES
        self.shots_left = SHOTS
        self.score = 0
        self.stage = 'intro'
        self.game_over_scheduled = False
        self.item_scheduled = False
        self.enemy_speedup_factor = 0
        self.super_time_secs_left = 0

        if sys.platform == 'darwin':
            self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SCALED | pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

        # Adding GAME_PATH to ensure work regardless running as package using e.g. UV or a script, rather than using CWD
        print('Current game path: ' + GAME_PATH)
        self.BG_IMAGE = pygame.image.load(GAME_PATH + '/img/background.png')
        self.BG_INTRO = pygame.image.load(GAME_PATH + '/img/intro.png').convert()
        self.BG_GAME_OVER = pygame.image.load(GAME_PATH + '/img/game_over.png').convert()
        self.IMG_WILMA = pygame.image.load(GAME_PATH + '/img/wilma.png').convert()
        self.IMG_DANIEL = pygame.image.load(GAME_PATH + '/img/daniel.png').convert()
        self.IMG_ALFONS = pygame.image.load(GAME_PATH + '/img/alfons.png').convert()
        self.IMG_FIA = pygame.image.load(GAME_PATH + '/img/fia.png').convert()
        self.IMG_SLIME = pygame.image.load(GAME_PATH + '/img/slimeshot.png').convert()
        self.IMG_POOP = pygame.image.load(GAME_PATH + '/img/poopshot.png').convert_alpha()
        self.IMG_HEART = pygame.image.load(GAME_PATH + '/img/heart.png').convert_alpha()
        self.IMG_EXTRA_SLIME = pygame.image.load(GAME_PATH + '/img/extra_slime.png').convert_alpha()
        self.IMG_EXTRA_LIFE = pygame.image.load(GAME_PATH + '/img/extra_life.png').convert_alpha()
        self.IMG_EXTRA_SUPER = pygame.image.load(GAME_PATH + '/img/superw.png').convert_alpha()

        self.SFX_SHOT = pygame.mixer.Sound(GAME_PATH + "/sfx/fart.ogg")
        self.SFX_BIG_SHOT = pygame.mixer.Sound(GAME_PATH + "/sfx/bigfart.ogg")
        self.SFX_SUPER = pygame.mixer.Sound(GAME_PATH + "/sfx/powerup.ogg")
        self.SFX_OUCH = pygame.mixer.Sound(GAME_PATH + "/sfx/ouch.ogg")
        self.SFX_GAME_OVER = pygame.mixer.Sound(GAME_PATH + "/sfx/gameover.ogg")
        self.OH_NO = pygame.mixer.Sound(GAME_PATH + "/sfx/oh_no.ogg")
        self.SFX_LETS_GO = pygame.mixer.Sound(GAME_PATH + "/sfx/lets_go.ogg")
        self.score_font = pygame.font.Font(GAME_PATH + '/fonts/my.ttf', 60)
        self.shots_font = pygame.font.Font(GAME_PATH + '/fonts/my.ttf', 18)
        self.super_left_font = pygame.font.Font(GAME_PATH + '/fonts/my.ttf', 20)
        self.debug_font = pygame.font.SysFont("Arial", 12)

    def intro(self, events):
        self.screen.fill(WHITE)
        self.screen.blit(self.BG_INTRO, (0, 0))
        pygame.display.update()
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
                if event.key == pygame.K_RETURN or event.key == pygame.K_LCTRL or event.key == pygame.K_SPACE:
                    self.stage = 'init_first_game'
            elif pygame.mouse.get_pressed()[0]:
                self.stage = 'init_first_game'

    def init_first_game(self):
        self.lives = LIVES
        self.score = 0
        self.shots_left = SHOTS

        self.SFX_LETS_GO.play()
        # This is a list of every sprite. All blocks and the player enemy as well.
        self.all_sprites_list = pygame.sprite.Group()

        # List of each enemy in the game
        self.enemy_list = pygame.sprite.Group()

        # List of each item in the game
        self.item_list = pygame.sprite.Group()

        # List of each bullet
        self.bullet_list = pygame.sprite.Group()

        for i in range(15):
            enemy = self.create_falling_enemy()
            # Add the enemy to the list of objects
            self.enemy_list.add(enemy)
            self.all_sprites_list.add(enemy)

        self.player = Player(self.IMG_WILMA, self)

        self.all_sprites_list.add(self.player)
        self.player.rect.y = 400
        start_music()
        self.stage = 'run_first_game'

        pygame.time.set_timer(EVENT_SPEEDUP_ENEMIES, 15000)
        # TODO: Need to resolve this compatible with pygame 1.9.2a0, expects 2 args

    def create_falling_enemy(self, image=None):
        if not image:
            image = random.choice([self.IMG_DANIEL, self.IMG_ALFONS, self.IMG_FIA])
        enemy = Enemy(image, self)
        # Set a random location for enemy far away from each others
        for attempt in range(50):
            x, y = self.get_random_x_above_view(), self.get_random_y_above_view()
            if is_far_away(x, y, [(_.pos_x, _.pos_y) for _ in self.enemy_list.sprites()]):
                enemy.pos_x = x
                enemy.pos_y = y
                break
        return enemy

    def create_falling_item(self):
        pygame.time.set_timer(EVENT_CREATE_ITEM, 0)
        self.item_scheduled = False
        velocity = random.randint(40, 60) / 100
        random_pick = random.randint(1, 100)
        # 20% chance for slime
        # 80% chance nothing
        if 0 <= random_pick <= 40:
            item_type = ItemType.SLIME
        elif 40 <= random_pick <= 50:
            item_type = ItemType.LIFE
        elif 50 <= random_pick <= 99:
            item_type = ItemType.SUPER
        else:
            return None
        item = Item(self, item_velocity=velocity, item_type=item_type)
        return item

    def get_random_y_above_view(self):
        # return random.randint(60, 350)
        return random.randint(50, 1600) * -1

    def get_random_x_above_view(self):
        return random.randint(30, SCREEN_WIDTH - 30)

    def run_first_game(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
                if event.key == pygame.K_LEFT:
                    self.player.go_left()
                if event.key == pygame.K_RIGHT:
                    self.player.go_right()
                if event.key == pygame.K_RETURN or event.key == pygame.K_LCTRL or event.key == pygame.K_SPACE:
                    self.player_shoot()
            elif pygame.mouse.get_pressed()[0]:
                mouse_x, _ = pygame.mouse.get_pos()
                if mouse_x < int(SCREEN_WIDTH * 0.3):
                    self.player.go_left()
                elif mouse_x > int(SCREEN_WIDTH * 0.7):
                    self.player.go_right()
                else:
                    self.player_shoot()
            elif event.type == EVENT_PLAYER_RECOVER_INJURY:
                self.player.restore_player_from_injury()
            elif event.type == EVENT_GAME_OVER:
                pygame.time.set_timer(EVENT_GAME_OVER, 0)
                self.stage = 'game_over'
            elif event.type == EVENT_CREATE_ITEM:
                item = self.create_falling_item()
                # Only create falling item of random says so
                if item:
                    self.item_list.add(item)
                    self.all_sprites_list.add(item)
            elif event.type == EVENT_DECREASE_TIME_SUPER:
                self.decrease_super_time_left()
            elif event.type == EVENT_SPEEDUP_ENEMIES:
                random_factor = random.randint(5, 20) / 100
                self.enemy_speedup_factor += random_factor
            elif event.type == EVENT_RECOVER_USER:
                self.player.restore_player_from_injury()
            elif event.type == EVENT_PLAYER_BECOME_NORMAL:
                self.player.player_become_normal()

        self.all_sprites_list.update()
        for bullet in self.bullet_list:
            # This removes the enemy from the enemy_list
            enemy_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_list, True)

            # For each enemy hit, remove the bullet and add to the score, and have a new enemy
            for _ in enemy_hit_list:
                self.bullet_list.remove(bullet)
                self.all_sprites_list.remove(bullet)
                self.score += 10
                enemy = self.create_falling_enemy()
                self.enemy_list.add(enemy)
                self.all_sprites_list.add(enemy)

            # Remove the bullet if it flies up off the screen
            if bullet.rect.y < -10:
                self.bullet_list.remove(bullet)
                self.all_sprites_list.remove(bullet)

        item_hit_list = pygame.sprite.spritecollide(self.player, self.item_list, True)
        for item in item_hit_list:
            item.player_caught()

        self.draw_background()

        # Draw all the spites
        self.enemy_list.update()
        self.item_list.update()
        self.all_sprites_list.draw(self.screen)

        self.draw_scores()
        self.draw_lives()
        self.draw_shots_left()
        self.draw_super_time_left()

        if DEBUG:
            self.draw_debug()

        if self.lives < 1 and not self.game_over_scheduled:
            self.game_over_scheduled = True
            pygame.time.set_timer(EVENT_GAME_OVER, 1000)

        # Ensure new items get created
        if not self.item_scheduled:
            self.item_scheduled = True
            pygame.time.set_timer(EVENT_CREATE_ITEM, random.randint(5000, 10000))

        pygame.display.update()

    def game_over(self, events):
        if self.game_over_scheduled:
            self.SFX_GAME_OVER.play()
        self.game_over_scheduled = False
        self.enemy_speedup_factor = 0
        self.screen.fill(BLACK)
        self.screen.blit(self.BG_GAME_OVER, (0, 0))
        text_surface = self.score_font.render('Score ' + str(self.score), True, (255, 0, 0))
        self.screen.blit(text_surface, (125, 300))
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
                if event.key == pygame.K_RETURN or event.key == pygame.K_LCTRL or event.key == pygame.K_SPACE:
                    self.stage = 'init_first_game'
            elif pygame.mouse.get_pressed()[0]:
                self.stage = 'init_first_game'

    def player_shoot(self):
        if self.super_time_secs_left > 0:
            self.SFX_BIG_SHOT.play()
            bullet = Bullet(self.IMG_POOP, self)
            bullet.rect.x = self.player.rect.x + 30
            bullet.rect.y = self.player.rect.y - 30
            self.all_sprites_list.add(bullet)
            self.bullet_list.add(bullet)
            return
        if self.shots_left == 0:
            self.OH_NO.play()
            return
        if self.shots_left > 0:
            self.shots_left -= 1
        self.SFX_SHOT.play()
        bullet = Bullet(self.IMG_SLIME, self)
        bullet.rect.x = self.player.rect.x + 30
        bullet.rect.y = self.player.rect.y
        self.all_sprites_list.add(bullet)
        self.bullet_list.add(bullet)

    def draw_background(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.BG_IMAGE, (0, 0))

    def draw_scores(self):
        # Put scores
        text_surface = self.score_font.render(str(self.score), True, (255, 0, 0))
        self.screen.blit(text_surface, (SCREEN_WIDTH - 200, 5))

    def draw_lives(self):
        life = self.IMG_HEART
        for idx, live in enumerate(range(self.lives)):
            self.screen.blit(life, (50 + idx * 30, 20))

    def draw_shots_left(self):
        shot = self.IMG_SLIME
        x = 280
        y = 25
        shot.set_colorkey((0, 0, 0, 255))
        self.screen.blit(shot, (x, y))
        text_surface = self.shots_font.render('x ' + str(self.shots_left), True, (0, 0, 0))
        self.screen.blit(text_surface, (x + 23, y))

    def draw_super_time_left(self):
        if not self.super_time_secs_left:
            return
        text_surface = self.super_left_font.render(str(self.super_time_secs_left), True, (0, 0, 0))
        self.screen.blit(text_surface, (5, 440))

    def draw_debug(self):
        fps = int(self.clock.get_fps())
        text = __version__ + ' [' + PYGAME_VERSION + '] FPS: ' + str(fps)
        text_surface = self.debug_font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (5, 2))

    def decrease_super_time_left(self):
        self.super_time_secs_left -= 1
        if self.super_time_secs_left <= 0:
            pygame.time.set_timer(EVENT_DECREASE_TIME_SUPER, 0)
            pygame.time.set_timer(EVENT_PLAYER_BECOME_NORMAL, 1000)

    def tick(self):
        # Pace is based on ratio from optimal duration, e.g. pase = 1 = perfect, pase = 0.5 = half speed
        # This to compensate for slower devices but keep same velocity of sprites
        self.pace = self.clock.tick(FPS) / OPTIMAL_MS_PER_TICK


async def game_loop():
    pygame.init()
    game = Game()

    # MAIN LOOP
    while not game.done:
        events = pygame.event.get()

        if game.stage == 'intro':
            game.intro(events)
        elif game.stage == 'init_first_game':
            game.init_first_game()
        elif game.stage == 'run_first_game':
            game.run_first_game(events)
        elif game.stage == 'game_over':
            game.game_over(events)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
        game.tick()
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    if not PY2:
        asyncio.run(game_loop())
