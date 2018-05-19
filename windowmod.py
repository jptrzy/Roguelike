# -*- coding: utf-8 -*- 
from bearlibterminal import terminal
from message import *
import math

"""
main windows: 
	world display (layers 0 to 100):
		terrain (1)
		constructs (2)
		mobs (3)

		x : 16 to x_len - 16
		y : 0 to y_len - 14

	message window (layer 0):

		x : 16 to x_len - 16
		y : y_len - 15 to y_len

	left info panel (layer 0):

		character stats and name:
			x : 0 to 15
			y : 0 to 7

	right info panel:
		
		mob info:
			x : game_x_len - 16 to game_x_len
			y : 0 to game_y_len - 25

	main display panel: layer 150


overlayed info panel (layer 180):
	x : game_x_len - 16 to game_x_len
	y : 0 to game_y_len

borders: layer 200

popup windows: layer 201+

"""

class window(object):
	def __init__(self, ylen, xlen, y, x, layer=0, wtype='normal', multi_layer=False):
		self.y = y
		self.x = x
		self.ylen = ylen
		self.xlen = xlen
		self.layer = layer

		self.wtype = wtype
		self.multi_layer = multi_layer

		self.area = self.ylen * self.xlen

		if self.wtype == 'normal' and self.multi_layer:
			self.fx = window(ylen, xlen, y, x, self.layer + 1, wtype='fx')

	def put(self, y, x, text, color=(255,255,255,255)):
		terminal.layer(self.layer)

		if len(color) != 4:
			terminal.color(terminal.color_from_argb(255, color[0], color[1], color[2]))
		else:
			terminal.color(terminal.color_from_argb(color[0], color[1], color[2], color[3]))
			
		terminal.printf(self.x + x, self.y + y, text)

	def resize(self, y_len, x_len):
		self.clear()

		self.ylen = y_len
		self.xlen = x_len

		if self.wtype == 'normal' and self.multi_layer:
			self.fx.clear()
			self.fx.ylen = y_len
			self.fx.xlen = x_len

	def move(self, y, x):
		self.clear()
		self.y = y        # coordinates given in terms of smallest grid (4x4) size
		self.x = x
		if self.wtype == 'normal' and self.multi_layer:
			self.fx.clear()
			self.fx.y = y
			self.fx.x = x


	def wprint(self, y, x, text, color=(255,255,255,255)):
		terminal.layer(self.layer)

		if len(color) != 4:
			terminal.color(terminal.color_from_argb(255, color[0], color[1], color[2]))
		else:
			terminal.color(terminal.color_from_argb(color[0], color[1], color[2], color[3]))	

		terminal.printf(self.x + x, self.y + y, text)


	def clear(self):
		terminal.layer(self.layer)
		terminal.clear_area(self.x, self.y, self.xlen, self.ylen)

		if self.wtype == 'normal' and self.multi_layer:
			self.fx.clear()

	def w_clear(self, y, x, w=1, h=1):
		terminal.layer(self.layer)
		terminal.clear_area(self.x + x, self.y + y, w, h)

		if self.wtype == 'normal' and self.multi_layer:
			self.fx.clear(self, y, x, w, h)

	def fill(self, text=u'█', color=(255,0,0,0)):
		for y in range(self.ylen):
			for x in range(self.xlen):
				self.put(y, x, text, color)

	def get_occupied(self):
		# get set of all occupied coords
		occupied = set()
		for y in range(self.ylen):
			for x in range(self.xlen):
				occupied.add((self.y + y, self.x + x))
		return occupied

	def print_border(self):
		# print top and bottom sides
		for row in (0, self.ylen-1):
			for i in range(1, self.xlen-1):
				self.put(row, i, u'═')

		# print left and right sides
		for collumn in (0, self.xlen-1):
			for i in range(1, self.ylen-1):
				self.put(i, collumn, u'║')

		# print corners
		self.put(0, 0, u'╔')
		self.put(0, self.xlen-1, u'╗')
		self.put(self.ylen-1, 0, u'╚')
		self.put(self.ylen-1, self.xlen-1, u'╝')

class panel(object):
	def __init__(self, ylen, xlen, y, x):
		self.windows = [] # ordered from lowest layer to highest layer
		self.ylen = ylen
		self.xlen = xlen
		self.y = y
		self.x = x

	def add_win(self, wlayer):
		new_win = window(self.ylen, self.xlen, self.y, self.x, layer=wlayer)

		if len(self.windows) != 0:
			index = 0
			for i in range(len(self.windows)):
				if self.windows[i].layer >= wlayer:
					break
				else:
					index += 1
			self.windows.insert(index, new_win)
		else:
			self.windows.append(new_win)

		return new_win

	def del_win(self, wlayer):
		for window in self.windows:
			if window.layer == wlayer:
				window.clear()
				self.windows.remove(window)


	def clear(self):
		for swindow in self.windows:
			swindow.clear()

	def move(self, y, x):
		for swindow in self.windows:
			swindow.move(y, x)
		self.y = y
		self.x = x

	def resize(self, y_len, x_len):
		for swindow in self.windows:
			swindow.resize(y_len, x_len)

		self.ylen = y_len
		self.xlen = x_len

	def print_border(self):
		self.windows[-1].print_border()

	def get_occupied(self):
		# get set of all occupied coords
		occupied = set()
		for y in range(self.ylen):
			for x in range(self.xlen):
				occupied.add((self.y + y, self.x + x))
		return occupied

class panel_windows(object):
	def __init__(self):
		self.windows = []

	def add_win(self, window):
		if window not in self.windows:
			self.windows.append(window)

	def remove_win(self, window):
		if window in self.windows:
			self.windows.remove(window)

	def recalc_win(self, ylen, xlen, y, x, layer):
		self.window = window(ylen, xlen, y, x, layer)
		self.ylen = ylen
		self.xlen = xlen

	def recalc_borders(self):
		self.occupied = set()
		self.borders = [] # [(y, x, border_str), ... ]
		for window in self.windows:
			self.occupied = self.occupied | window.get_occupied()

		for y in range(self.ylen):
			for x in range(self.xlen):
				if (y, x) not in self.occupied:
					self.borders.append((y, x, self.get_border_string(y, x)))

	def print_borders(self, color=(255,255,255)):
		self.window.clear()
		for border in self.borders:
			self.window.put(border[0], border[1], border[2], color)


	def get_border_string(self, y, x):
		surrounded = self.get_surrounded(y, x)
		if surrounded == set(['top', 'bottom']):
			return u'║'
		if surrounded == set(['left', 'right']):
			return u'═'
		if surrounded == set(['right', 'bottom']):
			return u'╔'
		if surrounded == set(['left', 'bottom']):
			return u'╗'
		if surrounded == set(['top', 'left']):
			return u'╝'
		if surrounded == set(['top', 'right']):
			return u'╚'
		if surrounded == set(['top', 'bottom', 'left']):
			return u'╣'
		if surrounded == set(['top', 'bottom', 'right']):
			return u'╠'
		if surrounded == set(['top', 'left', 'right']):
			return u'╩'
		if surrounded == set(['bottom', 'left', 'right']):
			return u'╦'
		if surrounded == set(['top', 'bottom', 'right', 'left']):
			return u'╬'

	def get_surrounded(self, y, x):
		surrounded = set()
		if self.check_surrounded(y+1, x):
			surrounded.add('bottom')
		if self.check_surrounded(y, x+1):
			surrounded.add('right')
		if self.check_surrounded(y-1, x):
			surrounded.add('top')
		if self.check_surrounded(y, x-1):
			surrounded.add('left')
		return surrounded


	def check_surrounded(self, y, x):
		if (y, x) in self.occupied or not self.check_borders(y, x):
			return False
		return True

	def check_borders(self, y, x):
		if y <= self.ylen-1 and y >= 0 and x >= 0 and x <= self.xlen-1:
			return True
		return False

class popup(object): # this class only handles display!
	def __init__(self, ylen, xlen, y, x, activepopups):
		self.ylen = ylen
		self.xlen = xlen
		self.y = y
		self.x = x
		self.activepopups = activepopups
		self.layer = activepopups + 200
		self.window = window(self.ylen, self.xlen, self.y, self.x, self.layer, multi_layer=False)

	def window_init(self):
		self.window.clear()
		self.window.fill(color=(230,0,0,0))
		self.window.print_border()

	def window_remove(self):
		self.window.clear()
		self.activepopups -= 1

class text_popup(popup):
	def __init__(self, body_message, game_y_len, game_x_len, title=None, activepopups=0, bottom_blank_rows=0):
		self.body_message = body_message
		self.game_y_len = game_y_len
		self.game_x_len = game_x_len
		self.activepopups = activepopups
		self.title = title
		self.bottom_blank_rows = bottom_blank_rows

		'''
		small window:
		╔═══════════════════════════════════════════════╗
		║Enter name:                                    ║
		╚═══════════════════════════════════════════════╝

		large window:
		╔═══════════════════════════════════════════════╗
		║Example Example Example Example Example Example║
		║Example Example Example Example Example Example║
		║Example Example Example Example Example:       ║
		╚═══════════════════════════════════════════════╝

		very large window:
		╔═══════════════════════════════════════════════╗
		║[cont.] Example Example Example Example Example^
		║Example Example Example Example Example Example▒
		║Example Example Example Example Example Example▒
		║Example Example Example Example Example Example▒
		║Example Example Example Example Example Example█
		║Example Example Example Example Example:       ˅
		╚═══════════════════════════════════════════════╝
		
		If large, body overflows to next line and an extra blank line is added.
		'''

		self.body_row_list = []
		self.title_row_list = []
		self.body_row_length = 0
		self.title_row_length = 0
		self.row_width = 30
		self.max_rows = 21
		self.large_window = False

	def standard_initiate_window(self):
		# use this function to automatically add the title and body message
		# body_message can either be 'phrase', ['phrase', color], or [['phrase', color], ... ]
		if self.title != None:
			s_add_message(convert_phrase_to_list(self.title), self.row_width, self.add_new_title_row)

		try:
			self.body_message[1][1][1]
			s_add_message(custom_convert_phrase_to_list(self.body_message), self.row_width, self.add_new_body_row)
			# multiple colors
		except:
			# only one color
			try:
				self.body_message[1][1]
				s_add_message(convert_phrase_to_list(self.body_message[0], self.body_message[1]), self.row_width, self.add_new_body_row)
			except IndexError:
				s_add_message(convert_phrase_to_list(self.body_message, [200,200,200]), self.row_width, self.add_new_body_row)

		self.prepare_window()


	def prepare_window(self):
		if self.body_row_length == 1:
			if self.title == None:
				self.row_width = len(self.body_row_list[0])
			else:
				self.row_width = max(len(self.body_row_list[0]), len(self.title))

		self.body_row_display_length = min(self.body_row_length, self.max_rows-self.title_row_length)

		self.min_row = 0
		self.max_row = self.body_row_display_length - 1

		popup.__init__(self, self.body_row_display_length+2+self.title_row_length+self.bottom_blank_rows, self.row_width+2, self.game_y_len/2-(self.body_row_display_length+self.title_row_length+self.bottom_blank_rows+2)/2, self.game_x_len/2-(self.row_width+2)/2, self.activepopups)

	def add_new_body_row(self, row):
		self.body_row_list.append(row)
		self.body_row_length += 1

		if self.body_row_length + self.title_row_length > self.max_rows:
			self.large_window = True

	def add_new_title_row(self, row):
		self.title_row_list.append(row)
		self.title_row_length += 1

	def print_row(self, row, y_index):
		col_count = 0
		for data_pair in row:
			char = data_pair[0]
			color = data_pair[1]
			self.window.put(y_index, 1+col_count, char, color)
			col_count += 1

	def print_scroll(self):
		bar_length = self.body_row_display_length-2
		scroll_bar_length = int(round((float(bar_length) / self.body_row_length)*bar_length))+1

		self.window.put(1+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))
		self.window.put(1+self.title_row_length, self.row_width+1, '^')
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))
		self.window.put(self.body_row_display_length+self.title_row_length, self.row_width+1, u'˅')

		for i in range(bar_length):
			self.window.w_clear(2+i+self.title_row_length, self.row_width+1)
			self.window.put(2+i+self.title_row_length, self.row_width+1, u'█', color=(230,0,0,0))

		start_scroll_bar_index = int(math.ceil((float(self.min_row) / self.body_row_length)*bar_length))

		if start_scroll_bar_index + scroll_bar_length > bar_length:
			start_scroll_bar_index -= 1

		for i in range(scroll_bar_length):
			self.window.put(start_scroll_bar_index+i+2+self.title_row_length, self.row_width+1, u'█', color=(100,100,100))
	
	def print_body(self):
		for i in range(self.max_row - self.min_row + 1):
			row = self.body_row_list[self.min_row+i]
			self.print_row(row, i+1+self.title_row_length)

		if self.large_window:
			self.print_scroll()

	def print_title(self):
		for i in range(self.title_row_length):
			row = self.title_row_list[i]
			self.print_row(row, i+1)

	def refresh_window(self):
		self.window.clear()
		self.window.fill(color=(230,0,0,0))
		self.window.print_border()

		self.print_body()
		if self.title != None:
			self.print_title()

	def close(self):
		self.window.clear()
		self.activepopups -= 1

class scroll_selection_popup(text_popup):
	def __init__(self, title_message, selection_options, game_y_len, game_x_len, activepopups=0):
		"""
				╔═══════════════════════════════════════════════╗
				║TITLE MESSAGE (ex. PICK ONE: )                 ║
				║Option 16                                      ^
				║Option 17 Option 17 Option 17 Option 17 Option ▒
				║17  Option 17 Option 17  (highlighted)         ▒
				║Option 18                                      ▒
				║Option 19                                      █
				║Option 20                                      ˅
				╚═══════════════════════════════════════════════╝
		"""		
		self.selection_options = selection_options
		self.num_options = len(self.selection_options)
		text_popup.__init__(self, '', game_y_len, game_x_len, title=title_message, activepopups=activepopups, bottom_blank_rows=0)

		# new list to store option_class instances
		self.options = []
		# text data
		self.selection_rows = []

	class option_class(object):
		def __init__(self, string):
			self.string = string

	def init(self):
		self.option_index = 0
		self.initialize_window()
		self.refresh_window()
		terminal.refresh()

		self.proceed = True

		while self.proceed:
			while terminal.has_input() and self.proceed:
				self.get_next_char()

		# finished response
		self.close()
		terminal.refresh()

		if self.option_index == None:
			return None
		else:
			return self.selection_options[self.option_index]

	def get_next_char(self):
		char = terminal.read()
		if char in [terminal.TK_DOWN, terminal.TK_UP]:
			if char == terminal.TK_DOWN:
				if self.option_index + 1 < self.num_options:
					self.option_index += 1
					self.recalc_min_max_rows()
			else:
				if self.option_index - 1 >= 0:
					self.option_index -= 1
					self.recalc_min_max_rows()

		elif char == terminal.TK_ENTER:
			self.proceed = False
			return
		elif char == terminal.TK_ESCAPE:
			self.option_index = None
			self.proceed = False
			return

		self.refresh_window()
		terminal.refresh()

	def recalc_min_max_rows(self):
		selected_option = self.options[self.option_index]

		if selected_option.end_row < self.body_row_display_length:
			self.min_row = 0
			self.max_row = self.body_row_display_length - 1
		else:
			self.max_row = selected_option.end_row
			self.min_row = self.max_row - self.body_row_display_length + 1

	def initialize_window(self):
		# use this function to initialize window instead of the standard initialize function in parent class

		# add title
		s_add_message(convert_phrase_to_list(self.title), self.row_width, self.add_new_title_row)

		for option in self.selection_options:
			# option will be string
			new_option = self.option_class(option)
			new_option.start_row = self.body_row_length
			s_add_message(convert_phrase_to_list(option), self.row_width, self.add_new_body_row)
			new_option.end_row = self.body_row_length - 1
			self.options.append(new_option)

		self.prepare_window()

	def print_highlight(self, color=(230,0, 83, 216)):
		selection_option = self.options[self.option_index]
		highlight_min_row = selection_option.start_row
		highlight_max_row = selection_option.end_row

		for i in range(highlight_max_row - highlight_min_row + 1):
			y_index = i+1+self.title_row_length+highlight_min_row-self.min_row
			self.window.w_clear(y_index, 1, self.row_width, 1)
			self.window.wprint(y_index, 1, u'█'*self.row_width, color)

	def refresh_window(self):
		self.window.clear()
		self.window.fill(color=(230,0,0,0))
		self.window.print_border()

		self.print_highlight()
		self.print_body()

		if self.title != None:
			self.print_title()


class yes_or_no_popup(text_popup):
	def __init__(self, body_message, game_y_len, game_x_len, title=None, activepopups=0):
		text_popup.__init__(self, body_message, game_y_len, game_x_len, title=title, activepopups=activepopups, bottom_blank_rows=0)
		self.standard_initiate_window()

	def get_next_char(self):
		char = terminal.read()
		if char in [terminal.TK_DOWN, terminal.TK_UP]:
			if self.large_window:
				if char == terminal.TK_DOWN:
					if self.max_row+1 < self.body_row_length:
						self.max_row += 1
						self.min_row += 1
				else:
					if self.min_row-1 >= 0:
						self.min_row -= 1
						self.max_row -= 1

		char = str(unichr(terminal.state(terminal.TK_CHAR)))
		if char in ['y', 'Y']:
			self.proceed = False
			self.reply = True
		elif char in ['n', 'N']:
			self.proceed = False
			self.reply = False
		
		self.refresh_window()

	def init(self):
		self.reply = None
		self.window_init()
		self.refresh_window()
		terminal.refresh()

		self.proceed = True

		while self.proceed:
			while terminal.has_input() and self.proceed:
				self.get_next_char()

		# finished response
		self.close()
		terminal.refresh()
		return self.reply

class pure_text_popup(text_popup):
	def __init__(self, body_message, game_y_len, game_x_len, title=None, activepopups=0):
		text_popup.__init__(self, body_message, game_y_len, game_x_len, title=title, activepopups=activepopups)
		self.standard_initiate_window()
		self.init()

	def init(self):
		self.window_init()
		self.refresh_window()
		terminal.refresh()

		self.proceed = True

		while self.proceed:
			while terminal.has_input() and self.proceed:
				self.get_next_char()

		self.close()
		terminal.refresh()

	def get_next_char(self):
		char = terminal.read()
		if char == terminal.TK_ESCAPE:
			self.proceed = False
			return
		elif char == terminal.TK_ENTER:
			self.proceed = False
			return
		elif char in [terminal.TK_DOWN, terminal.TK_UP]:
			if self.large_window:
				if char == terminal.TK_DOWN:
					if self.max_row+1 < self.body_row_length:
						self.max_row += 1
						self.min_row += 1
				else:
					if self.min_row-1 >= 0:
						self.min_row -= 1
						self.max_row -= 1

		self.refresh_window()
		terminal.refresh()


class text_input_popup(text_popup):
	def __init__(self, body_message, game_y_len, game_x_len, title=None, activepopups=0, only_ascii=True):
		text_popup.__init__(self, body_message, game_y_len, game_x_len, title=title, activepopups=activepopups, bottom_blank_rows=1)
		self.standard_initiate_window()
		self.only_ascii = only_ascii

	def get_next_char(self):
		char = terminal.read()
		if char == terminal.TK_ESCAPE:
			self.proceed = False
			self.return_reply = False
			return
		elif char == terminal.TK_ENTER:
			self.proceed = False
			return
		elif char == terminal.TK_BACKSPACE:
			try:
				del self.reply[-1:]
			except IndexError:
				pass
		elif char in [terminal.TK_DOWN, terminal.TK_UP]:
			if self.large_window:
				if char == terminal.TK_DOWN:
					if self.max_row+1 < self.body_row_length:
						self.max_row += 1
						self.min_row += 1
				else:
					if self.min_row-1 >= 0:
						self.min_row -= 1
						self.max_row -= 1

		char = terminal.state(terminal.TK_CHAR)
		if (48 <= char <= 57) or (97 <= char <= 122) or (65 <= char <= 90) or char == 32:
			char = str(unichr(char))
			self.reply.append(char)
		else:
			if not self.only_ascii:
				if (33 <= char <= 126):
					char = str(unichr(char))
					self.reply.append(char)
		
		self.refresh_window()

	def refresh_window(self):
		super(text_input_popup, self).refresh_window()
		self.print_response()

	def print_response(self):
		print_reply = self.reply[-(self.row_width-1):]
		for i in range(len(print_reply)):
			# left to right indices
			char = print_reply[i]
			self.window.put(self.body_row_display_length+1+self.title_row_length, i+1, char)

		self.window.put(self.body_row_display_length+1+self.title_row_length, len(print_reply)+1, '_')

		terminal.refresh()

	def init(self):
		self.reply = []
		self.window_init()
		self.refresh_window()
		self.window.put(self.body_row_display_length+1+self.title_row_length, 1, '_')
		terminal.refresh()

		self.proceed = True
		self.return_reply = True

		while self.proceed:
			while terminal.has_input() and self.proceed:
				self.get_next_char()

		# finished response
		self.close()
		terminal.refresh()
		if self.return_reply:
			return ''.join(self.reply)
		else:
			return False