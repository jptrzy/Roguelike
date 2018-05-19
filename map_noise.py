import random
import math

def gen_map(y, x, scale, generator):
	# takes a coordinate and returns height at coord
		output = generator.noise2d(float(y)/scale, float(x)/scale)

		# interpolates a number [-1,1] to [0,1]
		return (output + 1)/2

def circular_gradient(height, y, x, radius, scale, generator):
	# takes a height and returns height with circular gradient
	dist = math.sqrt((y)**2+(x)**2)/20
	
	# exponential decay of height
	#o
	# o
	#    o
	#        o
	#                o
	#                             o
	
	height = ((math.e)**(-dist/float(radius)))*height
	return height

def gen_mountain(y, x, scale, generator):
	height = 0
	for i in range(3): #octaves
		d_h = generator.noise2d(float(y)/scale, float(x)/scale)
		d_h = (d_h + 1)/2
		d_h *= 1.0/((i+1.0)**2)
		height += d_h

	height = (height)/1.5

	# makes mountains steeper
	height = height * height
	return height

