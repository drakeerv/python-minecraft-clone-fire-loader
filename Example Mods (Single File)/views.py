from googleapiclient.discovery import build
import threading
import time
import random

version = "1.0"
title = "Views"
description = "Places a block for each view on a youtube video."
author = "drakeerv"

youtube = build("youtube", "v3", developerKey=input("Google API Key for 'Youtube Data API v3': "))
ch_request = youtube.channels().list(part="statistics", id="UCqJwk3U9c4AksI-tb7B045g")

def update_views(game):
    while True:
        ch_response = ch_request.execute()
        game.views = int(ch_response["items"][0]["statistics"]["viewCount"])
        time.sleep(5)

def start(game):
    game.blocks_placed = 0
    game.views = 0
    game.done_views = True

    t = threading.Thread(target=update_views, daemon=True, name="Update Views", args=(game,))
    t.start()

def update(game):
    if game.blocks_placed < game.views:
        while True:
            position = [random.randint(-64, 63), random.randint(0, 127), random.randint(-64, 63)]
            if game.world.get_block_number(position) == 0:
                game.world.set_block(position, random.randint(1, len(game.world.block_types) - 1))
                break
        game.blocks_placed += 1;
        game.done_views = False
    elif not game.done_views:
        print("Up to date on views")
        game.done_views = True