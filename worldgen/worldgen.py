# -*- coding: utf-8 -*- 
from bearlibterminal import terminal
from include import randomgen
from tiles_data import tiles
import biome
import map_noise
import random

class world_tile(object):
	def __init__(self, y, x, biome):
		self.y = y
		self.x = x
		self.biome = biome
		self.tile = biome.default_tile

class world(object):
	def __init__(self, w_ylen, w_xlen, spawn_render_size, render_size, scale, circular_gradient_radius=6, center_coords=(0,0)):
		# w_ylen and w_xlen indicate map display size, not map size (map size is infinite)
		self.w_ylen = w_ylen
		self.w_xlen = w_xlen

		self.spawn_render_size = spawn_render_size
		self.render_size = render_size
		
		self.circular_gradient_radius = circular_gradient_radius
		self.scale = scale

		self.change_coords(center_coords)

		# list of all coordinates rendered by program
		self.rendered_coords=set()

		self.heightmap={}
		self.mountain_map = {}
		self.world_tiles = {}

		self.generator = randomGen.randomGenerator(seed=1)

		self.mode_list = [0, 1]
		# 0: biomes
		# 1: heightmap
		self.mode = 0
		self.zoom = 1

		self.create()

	def change_coords(self, center_coords):
		self.center_coords = center_coords
		# resets the topy and topx of map when center is changed
		self.center_y=center_coords[0]
		self.center_x=center_coords[1]

		# initiate coordinates with origin at center = (0,0)
		if self.w_xlen % 2 == 0: # if x_len is even
			self.w_top_x_coord = self.center_x - self.w_xlen / 2 + 1
		else:
			self.w_top_x_coord = self.center_x - self.w_xlen / 2

		if self.w_ylen % 2 == 0: # if y_len is even
			self.w_top_y_coord = self.center_y - self.w_ylen / 2 + 1
		else:
			self.w_top_y_coord = self.center_y - self.w_ylen / 2

		#           -2
		#           -1
		# ... -2 -1 0 1 2 ...
		#           1
		#           2

	def create(self):
		topy = self.center_y - self.spawn_render_size
		topx = self.center_x - self.spawn_render_size
		for i in range(self.spawn_render_size*2+1):
			for n in range(self.spawn_render_size*2+1):
				coord = (topy+i, topx+n)
				self.init_coord(coord)
				self.gen_heightmap(coord)
				self.gen_biomes(coord)

		# test
		self.gen_cross()

	def init_coord(self, coord):
		self.rendered_coords.add((coord[0], coord[1]))

	def gen_heightmap(self, coord):
		y=coord[0]
		x=coord[1]
		self.heightmap[coord]=map_noise.gen_map(y, x,
			scale=float(self.scale),
			generator=self.generator)

		# mountains
		self.heightmap[coord]+=map_noise.gen_mountain(y, x, self.scale, self.generator)

		# circular gradient
		self.heightmap[coord] = map_noise.circular_gradient(self.heightmap[coord], coord[0], coord[1], self.circular_gradient_radius, self.scale, self.generator)

	def gen_biomes(self, coord):
		height = self.heightmap[coord]
		y = coord[0]
		x = coord[1]
		if height < 0.2:
			self.world_tiles[coord] = world_tile(y, x, biome.void)
		elif height < 0.21:
			self.world_tiles[coord] = world_tile(y, x, biome.low_med_height)
		elif height < 0.27:
			self.world_tiles[coord] = world_tile(y, x, biome.med_height)
		elif height < 0.3:
			self.world_tiles[coord] = world_tile(y, x, biome.med_high_height)
		elif height < 0.4:
			self.world_tiles[coord] = world_tile(y, x, biome.high_height)
		else:
			self.world_tiles[coord] = world_tile(y, x, biome.peaks)

	# Generates a cross centered at y=0, x=0 for reference testing.
	def gen_cross(self):
		for y in range(-100, 100):
			self.world_tiles[(y, 0)] = world_tile(y, 0, biome.void)
		for x in range(-100, 100):
			self.world_tiles[(0, x)] = world_tile(0, x, biome.void)

	## dynamic map movement and render
	def move_from_increment(self, y_inc, x_inc):
		new_y = self.center_y + y_inc
		new_x = self.center_x + x_inc

		self.move((new_y, new_x))

	def move(self, new_coords):
		# shifts center to given coords; renders all chunks that aren't yet rendered
		self.change_coords(new_coords)
		
		topy = self.center_y - self.render_size
		topx = self.center_x - self.render_size

		for i in range(self.render_size*2+1):
			for n in range(self.render_size*2+1):
				coord = (topy+i, topx+n)
				if coord not in self.rendered_coords:
					self.init_coord(coord)
					self.gen_heightmap(coord)
					self.gen_biomes(coord)


	### temporary print functions for test
	def advance_mode(self):
		# move to next mode
		self.mode += 1
		if self.mode > len(self.mode_list) - 1:
			self.mode = 0

	def change_view_mode(self, mode_number):
		# mode 0: biomes
		# mode 1: heightmap
		self.mode = mode_number

	def print_(self, zoom=1):
		self.zoom=zoom
		if self.mode == 0:
			self.print_map()
		elif self.mode == 1:
			self.print_heightmap()

		terminal.color(terminal.color_from_argb(255,0,0,0))

		terminal.printf(0,0,str(self.center_y)+','+str(self.center_x))

		terminal.color(terminal.color_from_argb(255,0,0,0))

		terminal.printf(self.w_ylen/2, self.w_xlen/2, u"█")

		print ("Center is at: y=" + str(self.w_ylen/2+self.w_top_y_coord)+", x="+str(self.w_xlen/2+self.w_top_x_coord))

	def print_map(self):
		terminal.clear()
		for y in range(self.w_ylen):
			for x in range(self.w_xlen):
				try:
					if self.zoom == 1:
						coord_y = self.w_top_y_coord+y
						coord_x = self.w_top_x_coord+x
					else:
						# calculate zoomed coordinates (?)
						coord_y = ((self.w_top_y_coord+y) - self.center_y)/self.zoom + self.center_y
						coord_x = ((self.w_top_x_coord+x) - self.center_x)/self.zoom + self.center_x
					w_chunk = self.world_tiles[(coord_y, coord_x)]
					chunk_color = w_chunk.tile.color
					terminal.color(terminal.color_from_argb(255, chunk_color[0], chunk_color[1], chunk_color[2]))
					terminal.put(x, y, w_chunk.tile.icon)
				except KeyError: # chunk is not rendered
					terminal.color(terminal.color_from_argb(255, 0,0,0))
					terminal.put(x, y, u"█")

	def print_heightmap(self):
		terminal.clear()
		for y in range(self.w_ylen):
			for x in range(self.w_xlen):
				try:
					if self.zoom == 1:
						coord_y = self.w_top_y_coord+y
						coord_x = self.w_top_x_coord+x
					else:
						# calculate zoomed coordinates (?)
						coord_y = ((self.w_top_y_coord+y) - self.center_y)/self.zoom + self.center_y
						coord_x = ((self.w_top_x_coord+x) - self.center_x)/self.zoom + self.center_x
					scale_factor = int(self.heightmap[(coord_y, coord_x)]*255)
					terminal.color(terminal.color_from_argb(scale_factor, 255,255,255))
					terminal.put(x, y, u'█')
				except KeyError:
					pass

def main():
	size = (254,254)

	terminal.open()
	terminal.set("window: title = 'World gen. test', fullscreen=false, resizeable=false, cellsize=3x3; font: FSEX300.ttf, size=4x4")
	terminal.set("window: size="+str(size[0])+'x'+str(size[1]))
	terminal.composition(terminal.TK_ON)

	terminal.refresh()

	test_world = world(size[0], size[1], spawn_render_size=100, render_size=100, scale=20)
	
	test_world.print_heightmap()
	terminal.refresh()

	uinput = terminal.read()

	test_world.print_map()
	terminal.refresh()

	move = {terminal.TK_RIGHT : [0, 20],
		terminal.TK_DOWN : [20, 0],
		terminal.TK_LEFT : [0, -20],
		terminal.TK_UP : [-20, 0]}

	zoom_factors = [8, 2, 1, 0.5, 0.25] # bigger factor means bigger zoom
	zoom = 1
	i=1

	while True:
		if terminal.has_input():
			uinput=terminal.read()

			if uinput == terminal.TK_0:
				return

			if uinput in move.keys():
				movey = move[uinput][0]
				movex = move[uinput][1]

				test_world.move_from_increment(movey, movex)
				test_world.print_(zoom)
				terminal.refresh()

			elif uinput == terminal.TK_TAB:
				test_world.advance_mode()
				test_world.print_(zoom)
				terminal.refresh()

			elif uinput == terminal.TK_Z:
				current_index = zoom_factors.index(zoom)
				current_index += 1
				if current_index > len(zoom_factors)-1:
					current_index = 0

				zoom = zoom_factors[current_index]
				test_world.print_(zoom)
				terminal.refresh()

		# anim test
		# test_world.generator = OpenSimplex(seed=i)
		# i+=1
		# test_world.create()
		# test_world.print_(zoom)
		# terminal.refresh()


		



main()