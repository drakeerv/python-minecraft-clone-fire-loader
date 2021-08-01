from PIL import Image

import json
import math

version = "1.0"
title = "Picture"
description = "Creates pixel art from a picture."
author = "drakeerv"

settings = json.load(open("mods/image-settings.json"))

img = Image.open(f"mods/{settings.get('filename', 'image.png')}").convert("RGBA")
img = img.resize((settings.get("size", {}).get("width", img.size[0]), settings.get("size", {}).get("height", img.size[1])))

blocks = []
data = []

def closest_block(blocks, rgb):
    r, g, b = rgb
    color_diffs = []

    for block in blocks:
        color = block.get("color")
        cr, cg, cb = color
        color_diff = math.sqrt(abs(r - cr)**2 + abs(g - cg)**2 + abs(b - cb)**2)
        color_diffs.append((color_diff, block.get("id")))

    return min(color_diffs)[1]

def start(game):
    for id, block in enumerate([block for block in game.world.block_types if block]):
        if len(block.block_face_textures) == 1 and block.is_cube and not block.transparent and not block.glass:
            texture = Image.open(f"textures/{block.block_face_textures.get('all')}.png").convert("RGBA")
            color = Image.alpha_composite(Image.new("RGBA", texture.size, (255,255,255)), texture).convert("RGB").resize((1, 1)).getpixel((0, 0))
            blocks.append({"id": id, "color": color})

    for x in range(img.size[0]):
        data.append([])
        for y in range(img.size[1]):
            pixel = img.getpixel((x, y))

            if pixel[3] <= settings.get("opacity_threshold", 125):
                data[x].append(0)
            else:
                data[x].append(closest_block(blocks, pixel[:3]))

    for y in range(len(data)):
        data[y].reverse()

    if not settings.get("reverse", False):
        data.reverse()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            block = data[x][y]

            if block != 0:
                position = settings.get("position", {"x": 0, "y": 0, "z": 0})
                game.world.set_block([(x if not settings.get("rotate", False) else 0)+position["x"], y+position["y"], (x if settings.get("rotate", False) else 0)+position["z"]], block+1)

def update(game):
    pass