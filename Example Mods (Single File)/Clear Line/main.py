version = "1.0"
title = "Clear"
description = "Clear World."
author = "drakeerv"

def start(game):
    game.blocks_to_remove = []

    for x in range(-64, 64):
        for y in range(127):
            for z in range(-64, 64):
                if game.world.get_block_number([x,y,z]) != 0:
                    game.blocks_to_remove.append([x,y,z])

def update(game):
    try: position = game.blocks_to_remove.pop(0)
    except: return
    game.world.set_block(position, 0)