import random
import math

def random_number_in_interval(min, max, bias_to_min=1):
	if bias_to_min == "infinity":
		return min
	else:
		return min + (max - min)*(random.random()**bias_to_min)

def random_integer_in_interval(min, max, bias_to_min=1):
	return round(random_number_in_interval(min, max, bias_to_min))