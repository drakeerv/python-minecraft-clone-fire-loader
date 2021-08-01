version = "1.0"
title = "Pallete"
description = "Creates a pick block pallete at the top of the map."
author = "drakeerv"

def start(game):
    for z in range(1, (len(game.world.block_types) - 1)):
        game.world.set_block([0, 127, z-64], z)

def update(game):
    pass