# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pygame",
# ]
# ///
import asyncio
import math
import sys
import pygame
import random

PY2 = int(sys.version.split('.').pop(0)) == 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


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


class Player(pygame.sprite.Sprite):
    """ This class represents the Player. """

    def __init__(self, image, game):
        if PY2:
            super(Player, self).__init__()
        else:
            super().__init__()
        self.game = game
        self.change_x = 0
        self.image = image
        self.image.set_colorkey((0, 0, 0, 255))
        self.rect = self.image.get_rect()

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
        self.change_x = -2 * self.game.pace

    def go_right(self):
        self.change_x = 2 * self.game.pace


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


def is_far_away(x1, y1, current_pos_list):
    far_away = True
    for x2, y2 in current_pos_list:
        if xy_distance(x1, y1, x2, y2) < 50:
            far_away = False
    return far_away


def start_music():
    pygame.mixer.music.load("sfx/rainingbullets_smaller.ogg")
    pygame.mixer.music.play(-1)


class Game:

    def __init__(self):
        self.done = False
        self.clock = pygame.time.Clock()
        self.pace = 0  # The tick between frames to keep consistent speed across devices
        self.stage = 'intro'

        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

        self.BG_IMAGE = pygame.image.load('img/background.png')
        self.BG_INTRO = pygame.image.load('img/intro.png').convert()
        self.IMG_WILMA = pygame.image.load('img/wilma.png').convert()
        self.IMG_DANIEL = pygame.image.load('img/daniel.png').convert()
        self.IMG_SLIME = pygame.image.load('img/slimeshot.png').convert()

        self.SFX_SHOT = pygame.mixer.Sound("sfx/fart.ogg")
        self.score_font = pygame.font.Font('fonts/my.ttf', 60)

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
        # This is a list of every sprite. All blocks and the player block as well.
        self.all_sprites_list = pygame.sprite.Group()

        # List of each block in the game
        self.enemy_list = pygame.sprite.Group()

        # List of each bullet
        self.bullet_list = pygame.sprite.Group()

        current_enemy_positions = []
        for i in range(20):
            block = Enemy(self.IMG_DANIEL, self)

            # Set a random location for enemy far away from each others
            while True:
                x, y = random.randint(30, SCREEN_WIDTH - 30), random.randint(60, 350)
                if is_far_away(x, y, current_enemy_positions):
                    block.rect.x = x
                    block.rect.y = y
                    current_enemy_positions.append((x, y))
                    break
            # Add the block to the list of objects
            self.enemy_list.add(block)
            self.all_sprites_list.add(block)

        self.player = Player(self.IMG_WILMA, self)
        self.all_sprites_list.add(self.player)
        self.score = 0
        self.player.rect.y = 400
        start_music()
        self.stage = 'run_first_game'

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
                    self.SFX_SHOT.play()
                    bullet = Bullet(self.IMG_SLIME, self)
                    bullet.rect.x = self.player.rect.x + 30
                    bullet.rect.y = self.player.rect.y
                    self.all_sprites_list.add(bullet)
                    self.bullet_list.add(bullet)
            elif pygame.mouse.get_pressed()[0]:
                mouse_x, _ = pygame.mouse.get_pos()
                if mouse_x < int(SCREEN_WIDTH * 0.3):
                    self.player.go_left()
                elif mouse_x > int(SCREEN_WIDTH * 0.7):
                    self.player.go_right()
                else:
                    self.SFX_SHOT.play()
                    bullet = Bullet(self.IMG_SLIME, self)
                    bullet.rect.x = self.player.rect.x
                    bullet.rect.y = self.player.rect.y
                    self.all_sprites_list.add(bullet)
                    self.bullet_list.add(bullet)

        self.all_sprites_list.update()
        for bullet in self.bullet_list:
            block_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_list, True)

            # For each block hit, remove the bullet and add to the score
            for block in block_hit_list:
                self.bullet_list.remove(bullet)
                self.all_sprites_list.remove(bullet)
                self.score += 10

            # Remove the bullet if it flies up off the screen
            if bullet.rect.y < -10:
                self.bullet_list.remove(bullet)
                self.all_sprites_list.remove(bullet)

        # Clear the screen
        self.screen.fill(WHITE)

        # Set background
        self.screen.blit(self.BG_IMAGE, (0, 0))
        pygame.display.update()

        # Draw all the spites
        self.all_sprites_list.draw(self.screen)

        # Put scores
        text_surface = self.score_font.render(str(self.score), True, (255, 0, 0))
        self.screen.blit(text_surface, (SCREEN_WIDTH - 150, 5))

    def tick(self):
        # get ms between updates
        self.pace = self.clock.tick(60) / 10


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

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
        game.tick()
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    if not PY2:
        asyncio.run(game_loop())
