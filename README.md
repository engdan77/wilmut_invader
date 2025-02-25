# 👾 Wilmut Invader 👾

_Work in progress_



<center>🚀 Tap <a href="https://engdan77.github.io/wilmut_invader/">HERE</a> to play the browser version ▶️ </center>



## The plot of the game

Wilmut living a pieceful life on the mountain referred as "bärget" close to Huskvarna ⛰️.. until the family becomes cursed and she has to use her slime to protect herself 🦠 as the family members multiplies and becomes faster she has to fight 💪🏻 ... 

## How to play

⬅️     Left key to move left.. or click left part of touch screen
➡️     Right key to move right .. or click right part of touch screen
☄️     Shoot using spacebar key .. or middle of the touch screen

## Items in game

🟩    Can of slime - gives you additional 30 slime balls as ammunition
❤️    Heart - gives you additional life
🟨    Super - will grant powers to throw giant 💩

## How can this game be run

- Handheld [Miyoo](https://miyooofficial.com/) devices (á la GameBoy) running [OnionOS](https://onionui.github.io/)
- Within modern web-browsers supporting [WebAssembly](https://webassembly.org/features/)
- As pure native [PyGame](https://www.pygame.org/) easily installable using [UV](https://astral.sh/blog/uv) as package manager

## Background for development







## Installation

For the below instructions the project/package manager UV you can install 
by following [these](https://docs.astral.sh/uv/getting-started/installation/) instructions.


### Port to Miiyo/OnionOS Game Console

Insert the microSD card containing the roms and from the project use the developed 
helper command use the target directory it being mounted at to have it port the game to this card,
eject and then re-insert into your console.

```shell
uv run src/wilmut_invader/build_onionos_port.py /Volumes/USB/
```

## Run the game

#### From the source

```shell
uvx --from git+https://github.com/engdan77/wilmut_invader.git wilmut-invader
```

## Software architecture

Class relationship

```mermaid
---
title: game class diagram
---
classDiagram
    class ItemType {
        + int SLIME
        + int LIFE
        + int SUPER
    }

    class Enemy {
        - __init__(self, image, game) None
        + reset_pos(self)
        + update(self)
    }

    class Item {
        - __init__(self, game, item_velocity, item_type) None
        + reset_pos(self)
        + update(self)
        + player_caught(self)
    }

    class Player {
        - __init__(self, image, game) None
        + injury(self)
        + restore_player_from_injury(self)
        + player_become_normal(self)
        + become_super(self)
        + update(self)
        + go_left(self)
        + go_right(self)
    }

    class Bullet {
        - __init__(self, image, game) None
        + update(self)
    }

    class Game {
        - __init__(self) None
        + intro(self, events)
        + init_first_game(self)
        + create_falling_enemy(self, image)
        + create_falling_item(self)
        + get_random_y_above_view(self)
        + get_random_x_above_view(self)
        + run_first_game(self, events)
        + game_over(self, events)
        + player_shoot(self)
        + draw_background(self)
        + draw_scores(self)
        + draw_lives(self)
        + draw_shots_left(self)
        + draw_super_time_left(self)
        + draw_debug(self)
        + decrease_super_time_left(self)
        + tick(self)
    }

    Enemy --|> `pygame.sprite.Sprite`

    Item --|> `pygame.sprite.Sprite`

    Player --|> `pygame.sprite.Sprite`

    Bullet --|> `pygame.sprite.Sprite`
    
    Game *-- Enemy
    
    Game *-- Item
    
    Game *-- Player
    
    Game *-- Bullet
    
    Game --> ItemType
    
    Item --> ItemType
```

