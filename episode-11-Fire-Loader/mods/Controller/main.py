import pyglet
import math

version = "1.0"
title = "Controller"
description = "Allows you to use a controller."
author = "drakeerv"

# http://code.nabla.net/doc/pyglet/api/pyglet/input/pyglet.input.Joystick.html

def start(game):
    game.joysticks = pyglet.input.get_joysticks()
    [joystick.open() for joystick in game.joysticks]

    game.x_move = False
    game.y_move = False
    game.z_move = False

def update(game):
    if not game.mouse_captured:
        return

    threshold = 0.2
    sensitivity = 0.004

    for joystick in game.joysticks:
        if joystick.x <= -threshold: game.camera.input[0] = -1; game.x_move = True
        elif joystick.x >= threshold: game.camera.input[0] = 1; game.x_move = True
        elif game.x_move: game.camera.input[0] = 0; game.x_move = False

        if joystick.buttons[9]: game.camera.input[1] = -1; game.z_move = True
        elif joystick.buttons[0]: game.camera.input[1] = 1; game.z_move = True
        elif game.z_move: game.camera.input[1] = 0; game.z_move = False

        if joystick.y <= -threshold: game.camera.input[2] = 1; game.y_move = True
        elif joystick.y >= threshold: game.camera.input[2] = -1; game.y_move = True
        elif game.y_move: game.camera.input[2] = 0; game.y_move = False

        if abs(joystick.rx) > threshold: game.camera.rotation[0] += joystick.rx * sensitivity
        if abs(joystick.ry) > threshold: game.camera.rotation[1] -= joystick.ry * sensitivity

        if max(abs(joystick.rx), abs(joystick.ry)) > threshold: game.camera.rotation[1] = max(-math.tau / 4, min(math.tau / 4, game.camera.rotation[1]))