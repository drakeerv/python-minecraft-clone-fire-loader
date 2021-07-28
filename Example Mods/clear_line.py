version = "1.0"
title = "Clear"
description = "Clear World"

def start(game):
    game.blocks_to_remove = []

    for x in range(-64, 64):
        for y in range(127):
            for z in range(-64, 64):
                game.blocks_to_remove.append([x,y,z])

def update(game):
    while True:
        try: position = game.blocks_to_remove.pop(0)
        except: break
        if game.world.get_block_number(position) != 0:
            game.world.set_block(position, 0)
            break