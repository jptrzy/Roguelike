# -*- coding: utf-8 -*- 

from bearlibterminal import terminal

import mobs
import action
from windowmod import *

def process_request(request, game):
	request = request.split()

	if request[0] == 'help':
		pass