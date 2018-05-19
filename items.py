### items
class item(object):
	def __init__(self, name, weight, desc):
		self.name = name
		self.weight = weight
		self.desc = desc

class weapon(item):
	def __init__(self, name, weight, desc):
		item.__init__(self, name, weight, desc)

class consumable(item):
	def __init__(self, name, weight, desc):
		item.__init__(self, name, weight, desc)

axe = weapon('axe', 10)