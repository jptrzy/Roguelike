# -*- coding: utf-8 -*- 
import UserString

# Converts a string into a list of word-color pairs
# - if no color is specified, will auto pick white
def convert_phrase_to_list(phrase, color=[255,255,255]):
	if len(phrase.split()) == 1:
		return [[phrase, color]]

	phrase_list = [e+' ' for e in phrase.split() if e]
	phrase_list[-1] = UserString.MutableString(phrase_list[-1])

	del phrase_list[-1][-1]

	phrase_list[-1] = str(phrase_list[-1])
	texts_input = []

	for word in phrase_list:
		texts_input.append([word, color])

	return texts_input

# Converts a combination of different colored phrases into a list of word-color pairs
# - input_ will be in form [('phrase1', color1), ('phrase2', color2), ... ]
# - a space is automatically added at end of each phrase except when the
#   last character is '^'
def custom_convert_phrase_to_list(input_):
	texts_input = []
	for item in input_:
		phrase_list = convert_phrase_to_list(item[0], item[1])
		if item[0][-1] != '^':
			phrase_list[-1][0] += ' '
		else:
			phrase_list[-1][0] = phrase_list[-1][0].replace('^', '')
		texts_input += phrase_list
	return texts_input

# Converts a word into a list of character-color pairs.
# - if word is too long to fit on row, will return empty list
# as a precaution.
def convert_word_to_list(word, color, row_length):
	if len(word) > row_length:
		return []
	word_list = []
	for letter in word:
		word_list.append((letter, color))
	return word_list

# Recursively creates and adds lists of character-color pairs that fit within the
# row length until the whole message is added.
def s_add_message(input_, row_length, func_add_new_row):
	# input must be in form [['word', color], ... ] 
	# (must be converted to this form by the convert phrase to list function)
	space_count = 0
	new_row = []
	for i in range(len(input_)):
		word_info = input_[i] # word_info is in the form ['word', color]
		if len(word_info[0]) > row_length:
		# word won't fit on line, need to break it up into two or more words
			
			# first add existing row
			if new_row != []:
				func_add_new_row(new_row)
			
			num_word_pieces = int(len(word_info[0])) / int(row_length) + 1
			for n in range(num_word_pieces-1):
				word_piece = word_info[0][n*row_length:(n+1)*row_length]
				piece_letter_info = convert_word_to_list(word_piece, word_info[1], row_length)
				func_add_new_row(piece_letter_info)

			# replace original word with remaining word piece and add rest of message
			input_[i] = [word_info[0][(num_word_pieces-1)*row_length:], word_info[1]]
			s_add_message(input_[i:], row_length, func_add_new_row)
			return
		else:
			letter_info = convert_word_to_list(word_info[0], word_info[1], row_length)

		# checks for escape characters
		try:
			if letter_info[0][0] + letter_info[1][0] == '\\n':
				func_add_new_row(new_row)
				s_add_message(input_[(i+1):], row_length, func_add_new_row)
				return
			elif letter_info[0][0] + letter_info[1][0] == '\\v':
				func_add_new_row(new_row)
				func_add_new_row([[' ', [0,0,0]]])
				s_add_message(input_[(i+1):], row_length, func_add_new_row)
				return
		except IndexError:
			pass

		space_count += len(letter_info)
		if space_count <= row_length:
			new_row += letter_info
		else:
			func_add_new_row(new_row)
			s_add_message(input_[i:], row_length, func_add_new_row)
			return
	func_add_new_row(new_row)