import os
import pyglet

import pyglet.gl as gl

mods = []
mods_imported = []

if os.path.isdir("mods"):
	mods = [os.path.join("mods", f[1], "texture_manager.py").replace(".py", "") for f in [[os.listdir(os.path.join("mods", d)), d] for d in os.listdir("mods") if os.path.isdir(os.path.join("mods", d))] if "texture_manager.py" in f[0]]
	mods_imported = [__import__(m.replace("\\", "."), fromlist=[""]) for m in mods]

class TextureManagerBaseImpl:
	def __init__(self, texture_width, texture_height, max_textures):
		self.texture_width = texture_width
		self.texture_height = texture_height

		self.max_textures = max_textures

		self.textures = []

		self.texture_array = gl.GLuint(0)
		gl.glGenTextures(1, self.texture_array)
		gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.texture_array)

		gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

		gl.glTexImage3D(
			gl.GL_TEXTURE_2D_ARRAY, 0, gl.GL_RGBA,
			self.texture_width, self.texture_height, self.max_textures,
			0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
	
	def generate_mipmaps(self):
		gl.glGenerateMipmap(gl.GL_TEXTURE_2D_ARRAY)
	
	def add_texture(self, texture):
		if not texture in self.textures:
			self.textures.append(texture)

			texture_image = pyglet.image.load(f"textures/{texture}.png").get_image_data()
			gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.texture_array)

			gl.glTexSubImage3D(
				gl.GL_TEXTURE_2D_ARRAY, 0,
				0, 0, self.textures.index(texture),
				self.texture_width, self.texture_height, 1,
				gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,
				texture_image.get_data("RGBA", texture_image.width * 4))

TextureManagerMixins = []
for module in mods_imported:
	if hasattr(module, "TextureManagerMixin"):
		TextureManagerMixins.append(module.TextureManagerMixin)
		print("Applying mixin to class texture_manager.TextureManager")

class TextureManager(*TextureManagerMixins, TextureManagerBaseImpl):
	"""Texture Manager class"""