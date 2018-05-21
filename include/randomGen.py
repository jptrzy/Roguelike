import random
from opensimplex import OpenSimplex

class randomGenerator(object):
	def __init__(self, seed=False, scale=1.0):
		self.scale = scale
		self.reseed(seed)

	def reseed(self, seed=False):
		if seed:
			self.seed = seed
			self.oneDseed = seed * 1000000
		else:
			self.seed = random.randint(1, 4294967296)
			self.oneDseed = random.randint(1, 4294967296)

		self.generator = OpenSimplex(seed=self.seed)

		self.previous_trace = set()

	def noise2d(self, y, x, scale=1):
		return self.generator.noise2d(float(y)/self.scale/scale, float(x)/self.scale/scale)

	def noise1d(self, y, scale=1):
		return self.generator.noise2d(float(y)/self.scale/scale, float(self.oneDseed)/self.scale/scale)

	def noise3d(self, y, x, t, time_scale = 1, scale=1):
		return self.generator.noise3d(float(y)/self.scale/scale, float(x)/self.scale/scale, float(t)/time_scale)

	def get_closest_direction(self, y, x, retrace=False):
		closest_direction = (y+1, x+1)
		for i in [1, 0, -1]:
			for n in [1, 0, -1]:
				if not (i == 0 and n == 0):
					if self.noise2d(y+i, x+n) < self.noise2d(closest_direction[0], closest_direction[1]):
						if (y+i, x+n) not in self.previous_trace:
							closest_direction = (y+i, x+n)

		if closest_direction in self.previous_trace and not retrace:
			closest_direction = (y+random.randint(-1,1),x+random.randint(-1,1))

		self.previous_trace.add(closest_direction)
		return closest_direction

test = randomGenerator(seed=1)
