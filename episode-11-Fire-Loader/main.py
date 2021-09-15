# TODO
# 1. readthedocs
# 2. controller

import math
import ctypes
import random
import pyglet
import os

pyglet.options["shadow_window"] = False
pyglet.options["debug_gl"] = False

import pyglet.gl as gl

import matrix
import shader
import camera

import block_type
import texture_manager

import world

import hit

lines = ["--- Welcome to Fire Loader ---", "Developed by drakeerv", "Modified from obiwac", "--- Starting---", ""]
[print(line) for line in lines]
del lines

mods = []
mods_imported = []

if os.path.isdir("mods"):
	mods = [os.path.join("mods", f[1], "main.py").replace(".py", "") for f in [[os.listdir(os.path.join("mods", d)), d] for d in os.listdir("mods") if os.path.isdir(os.path.join("mods", d))] if "main.py" in f[0]]
	mods_imported = [__import__(m.replace("\\", "."), fromlist=[""]) for m in mods]

for module in mods_imported:
	print(f"Mod initialized: {(module.title if hasattr(module, 'title') else 'Undefined')}, Version: {(module.version if hasattr(module, 'version') else 'Undefined')} (By: {(module.author if hasattr(module, 'author') else 'Undefined')})")

print("")

class Window(pyglet.window.Window):
	def __init__(self, **args):
		super().__init__(**args)

		# create world

		self.world = world.World()
		
		# create shader

		self.shader = shader.Shader("vert.glsl", "frag.glsl")
		self.shader_sampler_location = self.shader.find_uniform(b"texture_array_sampler")
		self.shader.use()

		# pyglet stuff

		pyglet.clock.schedule_interval(self.update, 1.0 / 10000)
		self.mouse_captured = False

		# camera stuff

		self.camera = camera.Camera(self.shader, self.width, self.height)

		# misc stuff

		self.holding = 5

		# mod start

		for module in mods_imported:
			if hasattr(module, "start"):
				try: module.start(self)
				except Exception as e: print(e)
	
	def update(self, delta_time):
		# print(f"FPS: {1.0 / delta_time}")

		if not self.mouse_captured:
			self.camera.input = [0, 0, 0]

		self.camera.update_camera(delta_time)

		for module in mods_imported:
			if hasattr(module, "update"):
				try: module.update(self)
				except Exception as e: print(e)
	
	def on_draw(self):
		self.camera.update_matrices()

		# bind textures

		gl.glActiveTexture(gl.GL_TEXTURE0)
		gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.world.texture_manager.texture_array)
		gl.glUniform1i(self.shader_sampler_location, 0)

		# draw stuff

		gl.glEnable(gl.GL_DEPTH_TEST)
		gl.glEnable(gl.GL_CULL_FACE)

		gl.glClearColor(0.0, 0.0, 0.0, 0.0)
		self.clear()
		self.world.draw()

		gl.glFinish()

		for module in mods_imported:
			if hasattr(module, "draw"):
				try: module.draw(self)
				except Exception as e: print(e)
	
	# input functions

	def on_resize(self, width, height):
		print(f"Resize {width} * {height}")
		gl.glViewport(0, 0, width, height)

		self.camera.width = width
		self.camera.height = height

		for module in mods_imported:
			if hasattr(module, "resize"):
				try: module.resize(self)
				except Exception as e: print(e)

	def on_mouse_press(self, x, y, button, modifiers):
		if not self.mouse_captured:
			self.mouse_captured = True
			self.set_exclusive_mouse(True)

			for module in mods_imported:
				if hasattr(module, "capture"):
					try: module.capture(self)
					except Exception as e: print(e)

			return

		# handle breaking/placing blocks

		def hit_callback(current_block, next_block):
			if button == pyglet.window.mouse.RIGHT: self.world.set_block(current_block, self.holding)
			elif button == pyglet.window.mouse.LEFT: self.world.set_block(next_block, 0)
			elif button == pyglet.window.mouse.MIDDLE: self.holding = self.world.get_block_number(next_block)
		
		hit_ray = hit.Hit_ray(self.world, self.camera.rotation, self.camera.position)

		while hit_ray.distance < hit.HIT_RANGE:
			if hit_ray.step(hit_callback):
				break

		for module in mods_imported:
			if hasattr(module, "mouse_press"):
				try: module.mouse_press(self)
				except Exception as e: print(e)
	
	def on_mouse_motion(self, x, y, delta_x, delta_y):
		if self.mouse_captured:
			sensitivity = 0.004

			self.camera.rotation[0] += delta_x * sensitivity
			self.camera.rotation[1] += delta_y * sensitivity

			self.camera.rotation[1] = max(-math.tau / 4, min(math.tau / 4, self.camera.rotation[1]))

			for module in mods_imported:
				if hasattr(module, "mouse_motion"):
					try: module.mouse_motion(self)
					except Exception as e: print(e)
	
	def on_mouse_drag(self, x, y, delta_x, delta_y, buttons, modifiers):
		self.on_mouse_motion(x, y, delta_x, delta_y)
	
	def on_key_press(self, key, modifiers):
		if not self.mouse_captured:
			return

		if   key == pyglet.window.key.D: self.camera.input[0] += 1
		elif key == pyglet.window.key.A: self.camera.input[0] -= 1
		elif key == pyglet.window.key.W: self.camera.input[2] += 1
		elif key == pyglet.window.key.S: self.camera.input[2] -= 1

		elif key == pyglet.window.key.SPACE : self.camera.input[1] += 1
		elif key == pyglet.window.key.LSHIFT: self.camera.input[1] -= 1
		elif key == pyglet.window.key.LCTRL : self.camera.target_speed = camera.SPRINTING_SPEED

		elif key == pyglet.window.key.G:
			self.holding = random.randint(1, len(self.world.block_types) - 1)

		elif key == pyglet.window.key.O:
			self.world.save.save()

		elif key == pyglet.window.key.ESCAPE:
			self.mouse_captured = False
			self.set_exclusive_mouse(False)

		for module in mods_imported:
			if hasattr(module, "keyboard_press"):
				try: module.keyboard_press(self)
				except Exception as e: print(e)
	
	def on_key_release(self, key, modifiers):
		if not self.mouse_captured:
			return

		if   key == pyglet.window.key.D: self.camera.input[0] -= 1
		elif key == pyglet.window.key.A: self.camera.input[0] += 1
		elif key == pyglet.window.key.W: self.camera.input[2] -= 1
		elif key == pyglet.window.key.S: self.camera.input[2] += 1

		elif key == pyglet.window.key.SPACE : self.camera.input[1] -= 1
		elif key == pyglet.window.key.LSHIFT: self.camera.input[1] += 1
		elif key == pyglet.window.key.LCTRL : self.camera.target_speed = camera.WALKING_SPEED

		for module in mods_imported:
			if hasattr(module, "keyboard_release"):
				try: module.keyboard_release(self)
				except Exception as e: print(e)

class Game:
	def __init__(self):
		self.config = gl.Config(major_version = 3, depth_size = 16)
		self.window = Window(config = self.config, width = 800, height = 600, caption = "Minecraft clone (Fire Loader)", resizable = True, vsync = False)
	
	def run(self):
		pyglet.app.run()

if __name__ == "__main__":
	game = Game()
	game.run()
