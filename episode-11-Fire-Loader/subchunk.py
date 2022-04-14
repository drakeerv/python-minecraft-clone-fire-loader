SUBCHUNK_WIDTH  = 4
SUBCHUNK_HEIGHT = 4
SUBCHUNK_LENGTH = 4

import os

mods = []
mods_imported = []

if os.path.isdir("mods"):
	mods = [os.path.join("mods", f[1], "subchunk.py").replace(".py", "") for f in [[os.listdir(os.path.join("mods", d)), d] for d in os.listdir("mods") if os.path.isdir(os.path.join("mods", d))] if "subchunk.py" in f[0]]
	mods_imported = [__import__(m.replace("\\", "."), fromlist=[""]) for m in mods]

class SubchunkBaseImpl:
	def __init__(self, parent, subchunk_position):
		self.parent = parent
		self.world = self.parent.world

		self.subchunk_position = subchunk_position

		self.local_position = (
			self.subchunk_position[0] * SUBCHUNK_WIDTH,
			self.subchunk_position[1] * SUBCHUNK_HEIGHT,
			self.subchunk_position[2] * SUBCHUNK_LENGTH)

		self.position = (
			self.parent.position[0] + self.local_position[0],
			self.parent.position[1] + self.local_position[1],
			self.parent.position[2] + self.local_position[2])

		# mesh variables

		self.mesh_vertex_positions = []
		self.mesh_tex_coords = []
		self.mesh_shading_values = []

		self.mesh_index_counter = 0
		self.mesh_indices = []

		# set variables to read
		
		self.subchunk_width_r = SUBCHUNK_WIDTH
		self.subchunk_height_r = SUBCHUNK_HEIGHT
		self.subchunk_length_r = SUBCHUNK_LENGTH

	def add_face(self, face, pos, block_type):
		x, y, z = pos
		vertex_positions = block_type.vertex_positions[face].copy()

		for i in range(4):
			vertex_positions[i * 3 + 0] += x
			vertex_positions[i * 3 + 1] += y
			vertex_positions[i * 3 + 2] += z
		
		self.mesh_vertex_positions.extend(vertex_positions)

		indices = [0, 1, 2, 0, 2, 3]
		for i in range(6):
			indices[i] += self.mesh_index_counter
		
		self.mesh_indices.extend(indices)
		self.mesh_index_counter += 4

		self.mesh_tex_coords.extend(block_type.tex_coords[face])
		self.mesh_shading_values.extend(block_type.shading_values[face])

	def can_render_face(self, glass, block_number, position):
		return not (self.world.is_opaque_block(position)
			or (glass and self.world.get_block_number(position) == block_number))
	
	def update_mesh(self):
		self.mesh_vertex_positions = []
		self.mesh_tex_coords = []
		self.mesh_shading_values = []

		self.mesh_index_counter = 0
		self.mesh_indices = []

		for local_x in range(SUBCHUNK_WIDTH):
			for local_y in range(SUBCHUNK_HEIGHT):
				for local_z in range(SUBCHUNK_LENGTH):
					parent_lx = self.local_position[0] + local_x
					parent_ly = self.local_position[1] + local_y
					parent_lz = self.local_position[2] + local_z

					block_number = self.parent.blocks[parent_lx][parent_ly][parent_lz]

					if block_number:
						block_type = self.world.block_types[block_number]

						x, y, z = pos = (
							self.position[0] + local_x,
							self.position[1] + local_y,
							self.position[2] + local_z)
						
						

						# if block is cube, we want it to check neighbouring blocks so that we don't uselessly render faces
						# if block isn't a cube, we just want to render all faces, regardless of neighbouring blocks
						# since the vast majority of blocks are probably anyway going to be cubes, this won't impact performance all that much; the amount of useless faces drawn is going to be minimal

						if block_type.is_cube:
							if self.can_render_face(block_type.glass, block_number, (x + 1, y, z)): self.add_face(0, pos, block_type)
							if self.can_render_face(block_type.glass, block_number, (x - 1, y, z)): self.add_face(1, pos, block_type)
							if self.can_render_face(block_type.glass, block_number, (x, y + 1, z)): self.add_face(2, pos, block_type)
							if self.can_render_face(block_type.glass, block_number, (x, y - 1, z)): self.add_face(3, pos, block_type)
							if self.can_render_face(block_type.glass, block_number, (x, y, z + 1)): self.add_face(4, pos, block_type)
							if self.can_render_face(block_type.glass, block_number, (x, y, z - 1)): self.add_face(5, pos, block_type)
						
						else:
							for i in range(len(block_type.vertex_positions)):
								self.add_face(i, pos, block_type)


SubchunkMixins = []
for module in mods_imported:
	if hasattr(module, "SubchunkMixin"):
		SubchunkMixins.append(module.SubchunkMixin)
		print("Applying mixin to class subchunk.Subchunk")

class Subchunk(*SubchunkMixins, SubchunkBaseImpl):
	"""Subchunk class that handles subregions of a chunk"""
