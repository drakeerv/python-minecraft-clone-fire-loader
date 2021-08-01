import time
import random

version = "1.0"
title = "Blocks"
description = "Switches holding block randomly."
author = "drakeerv"

def start(game):
    pass

def update(game):
    game.holding = random.randint(1, len(game.world.block_types) - 1)