# -*- coding: utf-8 -*- 
from tiles_data import tiles

class biome(object):
	def __init__(self, name, desc, default_tile):
		self.name = name
		self.desc = desc
		self.default_tile = default_tile

void = biome("Voidlands.", "Vast expanse of inhabitable void.", tiles.w_void)
low_height = biome('█', 'low height', tiles.w_low_height)
low_med_height = biome(u'█', 'low med height', tiles.w_low_med_height)
med_height = biome(u'█', 'med height', tiles.w_med_height)
med_high_height = biome(u'█', 'med high height', tiles.w_med_high_height)
high_height = biome(u'█', 'high height', tiles.w_high_height)
peaks = biome(u'█', 'peaks', tiles.w_peaks)
rivers = biome(u'█', 'rivers', tiles.w_rivers)