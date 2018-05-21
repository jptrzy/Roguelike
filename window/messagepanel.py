# -*- coding: utf-8 -*- 
from bearlibterminal import terminal
from windows import *
from message import *

import math
import string

class message_panel(object):
	def __init__(self):
		self.messages = [] # list of [ row 0: [(letter, color), ... ], ... ]
		self.new = set() # set of new rows added
		self.raw_messages = [] # list of [message1, message2, ... ]

	def curs_init(self, game_y_len, game_x_len):
		self.window = window(13, game_x_len - 32, game_y_len - 14, 16)

	def recalc_win(self, game_y_len, game_x_len):
		self.window.resize(13, game_x_len - 32)
		self.window.move(game_y_len - 14, 16)

	def custom_add_phrase(self, input_):
		#input will be in form[('phrase', color), ... ]
		self.add_message(custom_convert_phrase_to_list(input_))

	def add_phrase(self, phrase, color=[255,255,255]):
		self.add_message(convert_phrase_to_list(phrase, color))

	def add_message(self, input_):
		self.new_message_top_index = len(self.messages)
		self.message_row_length = 0
		self.s_add_message(input_)
		self.raw_messages.append(input_)

	def s_add_message(self, input_):
		s_add_message(input_, self.window.xlen, self.add_new_row)

	def add_new_row(self, row):
		self.messages.append(row)
		self.new.add(len(self.messages)-1)
		self.message_row_length += 1

	def print_messages(self):
		#check if new messages exceed screen limit
		if len(self.new) > self.window.ylen:
			pages = len(self.new) // (self.window.ylen - 1)
			top_line_n = self.new_message_top_index
			for a in range(pages):
				self.window.clear()
				window_line_n = 0
				for n in range(self.window.ylen-1):
					row = self.messages[a*(self.window.ylen - 1)+n+top_line_n]
					self.new.remove(a*(self.window.ylen - 1)+n+top_line_n)
					for i in range(self.window.xlen):
						try:
							self.window.put(window_line_n, i, '[font=message]'+row[i][0]+'[/font]', row[i][1]) # +1 for boundary
						except IndexError:
							pass
					window_line_n += 1
				# prompt continue
				self.window.wprint(self.window.ylen-1, 0, '---more---')
				terminal.refresh()
				dir = terminal.read()

		self.window.clear()


		#print the latest 54 lines
		top_line_n = max(0, len(self.messages) - (self.window.ylen))
		window_line_n = 0
		for row in self.messages[-(self.window.ylen):]:
			if top_line_n + window_line_n in self.new:
				for i in range(self.window.xlen):
					try:
						self.window.put(window_line_n, i, '[font=message]'+row[i][0]+'[/font]', row[i][1]) # +1 for boundary
					except IndexError:
						pass
			else:
				for i in range(self.window.xlen):
					try:
						self.window.put(window_line_n, i, '[font=message]'+row[i][0]+'[/font]', [91, 91, 91]) # +1 for boundary
					except IndexError:
						pass
			window_line_n += 1

		terminal.refresh()
		self.new = set()



