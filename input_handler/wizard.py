# -*- coding: utf-8 -*- 

from bearlibterminal import terminal

from mobs import mobs
import action
from window import windows

def process_request(request, game):
	request = request.split()

	if request[0] == 'help':
		pass
