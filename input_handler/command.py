# -*- coding: utf-8 -*- 
### commands
import weather
from tiles_data import tiles
import time
import math
import wizard

from bearlibterminal import terminal

from mobs import mobs
import action
from window import windows

class commands_handler(object):
	def __init__(self):
		self.move = {
		### numpad on keyboard
		terminal.TK_KP_1 : [1, -1],
		terminal.TK_KP_2 : [1, 0],
		terminal.TK_KP_3 : [1, 1],
		terminal.TK_KP_4 : [0, -1],
		terminal.TK_KP_5 : [0, 0],
		terminal.TK_KP_6 : [0, 1],
		terminal.TK_KP_7 : [-1, -1],
		terminal.TK_KP_8 : [-1, 0],
		terminal.TK_KP_9 : [-1, 1],
		### conventional 4-dir
		terminal.TK_RIGHT : [0, 1],
		terminal.TK_DOWN : [1, 0],
		terminal.TK_LEFT : [0, -1],
		terminal.TK_UP : [-1, 0],
		### rest
		terminal.TK_R : [0, 0]
		}

		self.update_time = 0
		self.wizard_commands = wizard.wizard_commands()

	def command(self, uinput, game):
		if terminal.check(terminal.TK_SHIFT):
			self.shift_on = True
		else:
			self.shift_on = False

		if uinput == terminal.TK_ESCAPE:
			game.proceed = False

		elif uinput in self.move.keys():
			#p movement_time = time.clock()

			newy = game.me.y + self.move[uinput][0]
			newx = game.me.x + self.move[uinput][1]

			if game.world.check_passable(newy, newx) or uinput == terminal.TK_R:
				if self.shift_on:
					move_action = action.a_Sprint
				else:
					move_action = action.a_Walk

				game.me.do_action(move_action, (game.me, newy, newx), game)
			else:
				game.message_panel.add_phrase('Cannot move there.', [255,0,0])
				game.message_panel.print_messages()
			
			#p print("movement update: --- %s seconds ---" % (time.clock() - movement_time))

		elif uinput == terminal.TK_W:
			time_advance = 100
			game.update(game.timer.time+time_advance)
			game.update_screen()
			game.message_panel.add_phrase('Time advanced by ' + str(time_advance))
			game.message_panel.print_messages()

		elif uinput == terminal.TK_M:
			while not terminal.has_input():
				dir = terminal.read()
				break
			game.message_panel.add_phrase(dir, [255,0,0])
			game.message_panel.print_messages()

		elif uinput == terminal.TK_X:
			check_y = game.me.y
			check_x = game.me.x

			game.info_panel.open(game.bg_windows)
			game.info_panel.prompt(check_y, check_x)
			game.info_panel.exit(game.bg_windows)
			game.world.view()
			terminal.refresh()

		elif uinput == terminal.TK_H:
			for dynam_stat in game.me.dynam_stats:
				dynam_stat.alter(-1)
			game.me.printstats()

		elif uinput == terminal.TK_ENTER:
			message_test_popup = windows.text_input_popup('Enter test message to be displayed on the message panel:', game=game, title='test title', only_ascii=False)
			message_test = message_test_popup.init()
			if message_test is not None:
				if message_test == 'Lorem Ipsum':
					game.message_panel.add_phrase("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec lacus urna, rhoncus eget eros id, aliquet efficitur quam. Cras aliquam malesuada ex ut dapibus. Aliquam non nisl diam. Ut eget enim gravida, convallis nunc vel, consequat massa. Praesent ultricies lorem fringilla mauris lobortis, quis tincidunt velit vulputate. Aenean luctus dolor quis nisl vestibulum, tristique sagittis nisi bibendum. Cras molestie pulvinar tortor vitae elementum. Ut eu erat at neque dapibus commodo. Cras a ligula hendrerit est tincidunt accumsan. Ut sed interdum turpis, suscipit mollis eros. Suspendisse libero nunc, sodales eu diam nec, feugiat pharetra felis. Nullam vitae gravida justo. Proin volutpat vestibulum pulvinar. Aliquam gravida suscipit odio in placerat. \\v Cras est orci, dapibus vel semper nec, luctus vel nisl. Maecenas scelerisque imperdiet vestibulum. Cras sed ligula sit amet nisi dictum euismod sit amet nec lacus. Curabitur dapibus tellus nec orci luctus, nec hendrerit diam ornare. Curabitur sed ipsum a ligula vulputate iaculis. Morbi dignissim lectus vitae mattis ultricies. In sem magna, vestibulum rutrum elementum sed, maximus eu turpis. Morbi laoreet lorem diam, et porta nunc vestibulum a. Pellentesque varius hendrerit lectus, id dignissim arcu porta sit amet. Curabitur in facilisis turpis, vitae consectetur ex. Aliquam erat ipsum, porttitor a ullamcorper at, mattis ac eros. \\v Curabitur maximus efficitur interdum. Vivamus varius fermentum nibh, hendrerit laoreet elit sodales auctor. Suspendisse pellentesque turpis vel finibus varius. Phasellus vel lectus vitae odio auctor vehicula at vitae lacus. Nunc sagittis pharetra nulla, sed pharetra sem volutpat a. Aliquam finibus nulla quis metus ultrices vulputate. Pellentesque gravida fermentum quam, a fringilla sem tempor et. Suspendisse porttitor sapien ac lacinia dignissim. Mauris ante sapien, malesuada vitae eros sed, egestas aliquam ipsum. Nunc venenatis, risus sit amet gravida malesuada, erat libero egestas nisl, eu gravida velit diam sit amet nisi. In sit amet mollis ante, a dictum mi. Fusce gravida nulla id justo porta, at euismod nulla porta. In non quam ex.")
				else:
					game.message_panel.add_phrase(message_test)
				game.message_panel.print_messages()

		elif uinput == terminal.TK_A:
			proceed = True
			dir = terminal.read()
			if dir == terminal.TK_ESCAPE:
				proceed = False
			while dir not in self.move.keys() and proceed:
				dir = terminal.read()

			if proceed:
				attack_y = game.me.y + self.move[dir][0]
				attack_x = game.me.x + self.move[dir][1]

				attack_action = action.a_smite

				game.me.do_action(attack_action, (game.me, attack_y, attack_x, game.all_mobs.mob_lib), game)

		# other possibilities
		elif uinput == terminal.TK_RESIZED:
			# print '--------------------------!!!RESIZED!!!!!!!!!!--------------------'
			# game.w_ylen = terminal.state(terminal.TK_HEIGHT)
			# game.w_xlen = terminal.state(terminal.TK_WIDTH)

			# game.world.recalc_win(game.w_ylen, game.w_xlen)

			# game.message_panel.recalc_win(game.w_ylen, game.w_xlen)

			# game.info_panel.recalc_win(game.w_ylen, game.w_xlen)

			# game.me.recalc_win(game.w_ylen, game.w_xlen)

			# game.all_mobs.recalc_win(game.w_ylen, game.w_xlen)

			# game.bg_windows.recalc_win(game.w_ylen, game.w_xlen, 0, 0, 150)

			# game.bg_windows.recalc_borders()
			# game.bg_windows.print_borders()

			self.update_view(game)

		# wizard mode
		elif uinput == terminal.TK_BACKSLASH: # text_input_popup
			wizard_popup = windows.text_input_popup('Enter your command:', game=game, only_ascii=False)
			wizard_command = wizard_popup.init()
			if wizard_command:
				self.wizard_commands.process_request(wizard_command, game)