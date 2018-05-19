class pathfinder(object):
	def __init__(self):
		pass

	class coord(object):
		def __init__(self, y, x, parent, g_cost, h_cost):
			self.y = y
			self.x = x
			self.parent = parent
			self.g_cost = g_cost
			self.h_cost = h_cost
			self.cost = self.g_cost + self.h_cost

	def find_path(self, start, end, map, max_checks=300):
		self.y1, self.x1 = start
		self.y2, self.x2 = end

		self.max_checks = max_checks
		self.checks = 0

		self.finished = {}
		self.scanned = {}

		self.scanned[start] = self.coord(self.y1, self.x1, 'start', 0, abs(self.y1 - self.y2) + abs(self.x1 - self.x2))

		# scan coord with lowest cost
		while True:
			try:
				lowest_cost = self.scanned[self.scanned.keys()[0]].cost
				lowest_cost_cord = self.scanned[self.scanned.keys()[0]]
			except IndexError:
				# unable to find any path
				return False

			for coord in self.scanned.values():
				if coord.cost < lowest_cost:
					lowest_cost = coord.cost
					lowest_cost_cord = coord

			scan_result = self.scan_adj(lowest_cost_cord, map)

			if scan_result is None and self.checks <= self.max_checks:
				pass
			else:
				if self.checks > self.max_checks:
					return False

				self.path = []
				currenttile = scan_result
				while True:
					try:
						self.path.append((currenttile.y, currenttile.x))
						currenttile = currenttile.parent
					except AttributeError:
						return self.path[::-1]

	def scan_adj(self, coord1, map):
		adjacent = [(0,1), (0,-1), (1,0), (1,1), (1,-1), (-1,0), (-1,1), (-1,-1)]
		for adj in adjacent:
			newy = coord1.y + adj[0]
			newx = coord1.x + adj[1]

			#scan coord
			if (newy, newx) == (self.y2, self.x2):
				return self.coord(newy, newx, coord1, coord1.g_cost + 1, abs(self.y1 - newy) + abs(self.x1 - newx))
			elif (newy, newx) in self.finished.keys():
				pass
			elif not map.check_passable(newy, newx):
				pass
			elif (newy, newx) in self.scanned.keys():
				if coord1.g_cost + 1 < self.scanned[(newy, newx)].g_cost:
					self.scanned[(newy, newx)].parent = coord1
			else:	
				h_cost = abs(self.y1 - newy) + abs(self.x1 - newx)
				coord2 = self.coord(newy, newx, coord1, coord1.g_cost + 1, h_cost)
				
				self.scanned[(newy, newx)] = coord2

		del self.scanned[(coord1.y, coord1.x)]
		self.finished[(coord1.y, coord1.x)] = coord1

		self.checks += 1

		return None

pathfind = pathfinder()