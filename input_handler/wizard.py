# -*- coding: utf-8 -*- 
import weather
from tiles_data import tiles
import time
import math
import wizard

from bearlibterminal import terminal

from mobs import mobs
import action
from window import windows

def process_request(request, game):
	request = request.split()

	if request[0] == 'help':
		pass

	if request[0] == 'wait':
		try:
			time_advance = int(request[1])
			game.update(time_advance)
			game.update_screen()
			game.message_panel.add_phrase('Time advanced by ' + str(time_advance))
			game.message_panel.print_messages()	
		except IndexError:
			windows.pure_text_popup(("Please enter a time increment.", (255,0,0)), game.preferences.w_ylen, game.preferences.w_xlen, activepopups=game.activepopups)	
