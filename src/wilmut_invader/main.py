# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pygame",
# ]
# ///
import asyncio

import pygame
import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


class Block(pygame.sprite.Sprite):
    """ This class represents the block. """

    def __init__(self, color):
        super().__init__()

        self.image = pygame.Surface([20, 15])
        self.image.fill(color)

        self.rect = self.image.get_rect()


class Player(pygame.sprite.Sprite):
    """ This class represents the Player. """

    def __init__(self):
        super().__init__()
        self.change_x = 0
        self.image = pygame.Surface([20, 20])
        self.image.fill(RED)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x += self.change_x
        right_side = SCREEN_WIDTH - self.rect.width
        if self.rect.x >= right_side:
            self.change_x = 0
            self.rect.x = right_side
        left_side = self.rect.width
        if self.rect.x <= left_side - self.rect.width:
            print(self.rect.x)
            self.change_x = 0
            # self.rect.x = SCREEN_WIDTH

    def go_left(self):
        self.change_x = -4

    def go_right(self):
        self.change_x = 4


class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet . """

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([4, 10])
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y -= 3


async def game_loop():
    # Initialize Pygame
    pygame.init()

    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

    # This is a list of every sprite. All blocks and the player block as well.
    all_sprites_list = pygame.sprite.Group()

    # List of each block in the game
    block_list = pygame.sprite.Group()

    # List of each bullet
    bullet_list = pygame.sprite.Group()

    for i in range(50):
        # This represents a block
        block = Block(BLUE)

        # Set a random location for the block
        block.rect.x = random.randrange(SCREEN_WIDTH)
        block.rect.y = random.randrange(350)

        # Add the block to the list of objects
        block_list.add(block)
        all_sprites_list.add(block)

    # Create a red player block
    player = Player()
    all_sprites_list.add(player)
    done = False
    clock = pygame.time.Clock()
    score = 0
    player.rect.y = 450

    # --- Main loop
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_RETURN or event.key == pygame.K_LCTRL:
                    bullet = Bullet()
                    bullet.rect.x = player.rect.x
                    bullet.rect.y = player.rect.y
                    all_sprites_list.add(bullet)
                    bullet_list.add(bullet)
            elif pygame.mouse.get_pressed()[0]:
                mouse_x, _ = pygame.mouse.get_pos()
                if mouse_x < int(SCREEN_WIDTH * 0.3):
                    player.go_left()
                elif mouse_x > int(SCREEN_WIDTH * 0.7):
                    player.go_right()
                else:
                    bullet = Bullet()
                    bullet.rect.x = player.rect.x
                    bullet.rect.y = player.rect.y
                    all_sprites_list.add(bullet)
                    bullet_list.add(bullet)

        all_sprites_list.update()
        for bullet in bullet_list:
            block_hit_list = pygame.sprite.spritecollide(bullet, block_list, True)

            # For each block hit, remove the bullet and add to the score
            for block in block_hit_list:
                bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)
                score += 1
                print(score)

            # Remove the bullet if it flies up off the screen
            if bullet.rect.y < -10:
                bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)

        # Clear the screen
        screen.fill(WHITE)

        # Draw all the spites
        all_sprites_list.draw(screen)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        clock.tick(60)

        await asyncio.sleep(0)

    pygame.quit()


def start():
    asyncio.run(game_loop())


if __name__ == '__main__':
    start()

