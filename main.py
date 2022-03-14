import sys, pygame
from settings import *
from piece import *

class Game:
	'''	This class holds all the data for my chess game '''
	def __init__(self):
		pygame.init()
		pygame.display.list_modes()
		pygame.display.set_caption(NAME)
		self.clock = pygame.time.Clock()
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
		self.menu_screen = self.screen.subsurface((WIDTH / 2) - (MENU_WIDTH / 2) + OFFSET, (HEIGHT/ 2) - (MENU_HEIGHT / 2) + (OFFSET * 4), MENU_WIDTH, MENU_HEIGHT)
		self.piece_path = import_pieces()
		self.paused = False
		self.pause_buttons = []
		self.settingd = False
		self.settings_buttons = []
		self.settings = {'Settings' : SETTINGS, 'WhiteFirst' : WHITEFIRST, 'Captures' : CAPTURES, 'Score' : SCORE, 'DevMode' : DEVMODE}
		self.checker = []	# array of checkerboard squares
		self.piece_sprites = pygame.sprite.Group()
		self.piece_value = {'Pawn' : 1, 'Knight' : 3, 'Bishop' : 3, 'Rook' : 5, 'Queen' : 9, 'King' : 0 }	# dictionary for piece values
		self.tile = { 'piece' : [Piece(None) for _ in range(64)], 'rect' : [], 'color' : [], 'cell' : [] }	# dictionary for tile information
		self.click_time = 0
		self.click_cooldown = COOLDOWN
		self.turn = { 'white' : True, 'black' : False, 'empty' : False }
		self.blacks_captured = 0
		self.black_score = 0
		self.whites_captured = 0
		self.white_score = 0
		self.captured_section = [[],[]]
		self.captured_pieces = []			
		self.move_list = []

	def draw_board(self):
		for y in range (8):
			for x in range (0, 8, 2):
				tile_even = pygame.Rect(48 + ((WIDTH / 10) * x), 183 + ((WIDTH / 10) * y), TILESIZE, TILESIZE)
				self.checker.append(tile_even)
				tile_odd = pygame.Rect((48*2 - OFFSET) + ((WIDTH / 10) * x), 183 + ((WIDTH / 10) * y), TILESIZE, TILESIZE)
				self.checker.append(tile_odd)
				if (y % 2 == 0):
					color_one = WHITE_TILE
					color_two = BLACK_TILE
				else:
					color_one = BLACK_TILE
					color_two = WHITE_TILE
				self.tile['rect'].append(tile_even)
				self.tile['color'].append(color_one)
				self.tile['rect'].append(tile_odd)
				self.tile['color'].append(color_two)
				pygame.draw.rect(self.screen, color_one, tile_even)
				pygame.draw.rect(self.screen, color_two, tile_odd)
		# draw cell names
		self.font = pygame.font.SysFont(FONT, FONT_SIZE)
		for x in range(8):
			self.screen.blit(self.font.render(f'{chr(x + 65)}', True, FONT_COLOR, 'Black'), (self.checker[x].x + 18, self.checker[x].y - 15))
		for x in range(56, 64):
			self.screen.blit(self.font.render(f'{chr(x + 9)}', True, FONT_COLOR, 'Black'), (self.checker[x].x + 18, self.checker[x].y + 45))
		for x in range(0, 64, 8):
			self.screen.blit(self.font.render(f'{(64 - x) // 8}', True, FONT_COLOR, 'Black'), (self.checker[x].x - 12, self.checker[x].y + 12))
		for x in range(7, 64, 8):
			self.screen.blit(self.font.render(f'{((64 - x) // 8) + 1}', True, FONT_COLOR, 'Black'), (self.checker[x].x + 50, self.checker[x].y + 12))

	def add_piece(self, piece, x, y_off):
		'''helper function for draw_piece'''
		p = Piece(piece)
		p.rect.center = self.checker[x + y_off].center
		self.tile['piece'][x + y_off] = p
		self.piece_sprites.add(p)

	def draw_pieces(self):
		for piece in self.piece_path:
			if 'Pawn' in piece:
				y_off = 8
				if 'white' in piece:
					y_off = 48
				for x in range(8):
					self.add_piece(piece, x, y_off)
			elif 'Knight' in piece:
				y_off = 1
				if 'white' in piece:
					y_off = 57
				for x in range(0, 6, 5):
					self.add_piece(piece, x, y_off)
			elif 'King' in piece:
				y_off = 4
				if 'white' in piece:
					y_off = 60
				self.add_piece(piece, 0, y_off)
			elif 'Rook' in piece:
				y_off = 0
				if 'white' in piece:
					y_off = 56
				for x in range(0, 8, 7):
					self.add_piece(piece, x, y_off)
			elif 'Bishop' in piece:
				y_off = 2
				if 'white' in piece:
					y_off = 58
				for x in range(0, 4, 3):
					self.add_piece(piece, x, y_off)
			elif 'Queen' in piece:
				y_off = 3
				if 'white' in piece:
					y_off = 59
				self.add_piece(piece, 0, y_off)
		self.piece_sprites.draw(self.screen)

	def	draw_captured_section(self):
		white_capture_surf = pygame.Surface((TILESIZE, TILESIZE))
		black_capture_surf = pygame.Surface((TILESIZE, TILESIZE))
		white_capture_surf.fill(CAPTURED_W)
		black_capture_surf.fill(CAPTURED_B)
		for y in range(1, 3):
			for x in range(8):
				w_location = (48 + ((WIDTH / 10) * x), 183 - ((WIDTH / 10) * (3 - y)) - (OFFSET * 5))
				b_location = (48 + ((WIDTH / 10) * x), 183 + ((WIDTH / 10) * (7 + y)) + (OFFSET * 5))
				
				if self.settings['Captures'] is ENABLED:
					self.screen.blit(white_capture_surf, w_location)
					self.screen.blit(black_capture_surf, b_location)

				w_cap = pygame.Rect(w_location[0], w_location[1], TILESIZE, TILESIZE)
				b_cap = pygame.Rect(b_location[0], b_location[1], TILESIZE, TILESIZE)
				
				self.captured_section[0].append(w_cap)
				self.captured_section[1].append(b_cap)

	def draw_score_helper(self, score, score_pos):
		s = self.font.render(f'{score}', True, FONT_COLOR, 'Black')
		s_pos = s.get_rect()
		s_pos.topleft = score_pos.topright
		s_pos.x = 93
		self.screen.blit(s, s_pos)

	def draw_score(self, update, color):
		if self.settings['Score'] is ENABLED:
			self.font = pygame.font.SysFont(FONT, FONT_SIZE)
			s = self.font.render('SCORE :        ', True, FONT_COLOR, 'Black')
			score_pos = s.get_rect()
			score_pos.bottomleft = (self.captured_section[0][0].topleft)
			score_pos.y -= OFFSET
			if color != 'black':
				if update is True:
					score_pos.x = 48
					self.draw_score_helper(self.black_score, score_pos)
				else:
					self.screen.blit(s, score_pos)
			score_pos.topleft = (self.captured_section[1][8].bottomleft)
			score_pos.y += OFFSET
			if color != 'white':
				if update is True:
					self.draw_score_helper(self.white_score, score_pos)
				else:
					self.screen.blit(s, score_pos)

	def init_menu(self, menu):
		'''initialize variables for the menus'''
		self.font = pygame.font.SysFont(FONT, FONT_SIZE * 3)
		if menu == 'Pause':
			texts = ['undo', 'restart', 'quit']
		elif menu == 'Settings':
			texts = ['white', 'captures', 'scores', 'dev mode']
		button = []
		n = len(texts)
		for i in range(n):
			b = pygame.Rect(MENU_WIDTH * .1, (i * (MENU_HEIGHT / (n + 1))) + (TILESIZE / 2), MENU_WIDTH * .8, TILESIZE)
			button.append(b)
		for i, text in enumerate(texts):
			text = self.font.render(text, True, 'Black')
			pos = text.get_rect()
			pos.center = button[i].center
			if menu == 'Pause':
				self.pause_buttons.append((button[i], text, pos))
			if menu == 'Settings':
				self.settings_buttons.append((button[i], text, pos))

	def draw_pause(self):
		self.menu_screen.fill(MENU_COLOR)
		for box, text, pos in self.pause_buttons:
			pygame.draw.rect(self.menu_screen, MENU_BUTTON, box)
			self.menu_screen.blit(text, pos)
		pygame.display.update()
	
	def unpause(self):
		self.menu_screen.fill((0,0,0,0))
		for i, t in enumerate(self.tile['rect']):
			pygame.draw.rect(self.screen, self.tile['color'][i], t)
		self.piece_sprites.draw(self.screen)
		pygame.display.update()
		self.paused = False
		self.settingd = False

	def pause_menu(self):
		click = pygame.mouse.get_pressed()
		if click[0] == True:
			self.click_time = pygame.time.get_ticks()
		button = self.click_event(click, self.menu_screen, [x[0] for x in self.pause_buttons])
		if button is not False:
			if button == 0:
				self.undo_last_move()
			if button == 1:
				self.restart()
			if button == 2:
				pygame.quit()
				sys.exit()
			self.unpause()
		return button

	def draw_settings(self):
		if self.settings['Settings'] is ENABLED:
			self.font = pygame.font.SysFont(FONT, FONT_SIZE * 3)
			self.menu_screen.fill(MENU_COLOR)
			for i, button in enumerate(self.settings_buttons):
				box, text, pos = button
				if i == 0:
					if self.settings['WhiteFirst']:
						color = 'White'
						text = self.font.render('White', True, 'Black')
					else:
						color = 'Black'
						text = self.font.render('Black', True, 'White')
					pygame.draw.rect(self.menu_screen, color, box)
					self.menu_screen.blit(text, pos)
				else:
					pygame.draw.rect(self.menu_screen, MENU_BUTTON, box)
					self.menu_screen.blit(text, pos)
			pygame.display.update()
	
	def settings_menu(self):
		click = pygame.mouse.get_pressed()
		if click[0] == True:
			self.click_time = pygame.time.get_ticks()
		button = self.click_event(click, self.menu_screen, [x[0] for x in self.settings_buttons])
		if button is not False:
			if button == 0:
				self.settings['WhiteFirst'] = not self.settings['WhiteFirst']
			if button == 1:
				self.settings['Captures'] = not self.settings['Captures']
			if button == 2:
				self.settings['Score'] = not self.settings['Score']
			if button == 3:
				self.settings['DevMode'] = not self.settings['DevMode']
			self.unpause()
		return button

	def straight_moves(self, idx):
		moves = []
		same_x_r = False
		same_x_l = False
		swap_x_r = False
		swap_x_l = False
		same_y_u = False
		same_y_d = False
		swap_y_u = False
		swap_y_d = False
		cap = 0
		for i in range(1, 8):
			x = idx + i
			if idx % 8 > x % 8:
				x = x - (i + 1) - (x % 8)
			if x < 64 and x >= 0:
				if x > idx:
					if self.tile['piece'][x].color == self.tile['piece'][idx].color:
						same_x_r = True
					if not same_x_r and not swap_x_r:
						moves.append(x)
					if self.tile['piece'][x].color != 'empty' and self.tile['piece'][x].color != self.tile['piece'][idx].color:
						swap_x_r = True
				else:
					if self.tile['piece'][x].color == self.tile['piece'][idx].color:
						same_x_l = True
					if not same_x_l and not swap_x_l:
						moves.append(x)
					if self.tile['piece'][x].color != 'empty' and self.tile['piece'][x].color != self.tile['piece'][idx].color:
						swap_x_l = True
			y = idx + (i * 8)
			if y >= 64:
				cap += 1
				y = idx - (8 * cap)
			if y < 64 and y >= 0:
				if y > idx:
					if self.tile['piece'][y].color == self.tile['piece'][idx].color:
						same_y_d = True
					if not same_y_d and not swap_y_d:
						moves.append(y)
					if self.tile['piece'][y].color != 'empty' and self.tile['piece'][y].color != self.tile['piece'][idx].color:
						swap_y_d = True
				else:
					if self.tile['piece'][y].color == self.tile['piece'][idx].color:
						same_y_u = True
					if not same_y_u and not swap_y_u:
						moves.append(y)
					if self.tile['piece'][y].color != 'empty' and self.tile['piece'][y].color != self.tile['piece'][idx].color:
						swap_y_u = True
		return moves
					
	def diagonal_moves(self, idx):
		same_dl_d = False
		same_dl_u = False
		swap_dl_d = False
		swap_dl_u = False
		same_dr_u = False
		same_dr_d = False
		swap_dr_u = False
		swap_dr_d = False
		moves = []
		cap_dl = 0
		cap_dr = 0
		for i in range (1, 8):
			dl = idx + (i * 8) + i
			if dl >= 64:
				cap_dl += 1
				dl = idx - (cap_dl * 8) - cap_dl
			if dl < 64 and dl >= 0:
				if dl > idx:
					if dl % 8 < idx % 8:
						same_dl_d = True
					if self.tile['piece'][dl].color == self.tile['piece'][idx].color:
							same_dl_d = True
					if not same_dl_d and not swap_dl_d:
						moves.append(dl)
					if self.tile['piece'][dl].color != 'empty' and self.tile['piece'][dl].color != self.tile['piece'][idx].color:
						swap_dl_d = True
				else:
					if dl % 8 > idx % 8:
						same_dl_u = True
					if self.tile['piece'][dl].color == self.tile['piece'][idx].color:
							same_dl_u = True
					if not same_dl_u and not swap_dl_u:
						moves.append(dl)
					if self.tile['piece'][dl].color != 'empty' and self.tile['piece'][dl].color != self.tile['piece'][idx].color:
						swap_dl_u = True
			dr = idx + (i * 8) - i
			if dr >= 64 or same_dr_d: # hot fix condition using 'or' where dr didnt recognize all valid moves
				cap_dr += 1
				dr = idx - ((cap_dr) * 8) + cap_dr
			if dr < 64 and dr >= 0:
				if dr > idx:
					if dr % 8 > idx % 8:
						same_dr_d = True
					if self.tile['piece'][dr].color == self.tile['piece'][idx].color:
							same_dr_d = True
					if not same_dr_d and not swap_dr_d:
						moves.append(dr)
					if self.tile['piece'][dr].color != 'empty' and self.tile['piece'][dr].color != self.tile['piece'][idx].color:
						swap_dr_d = True
				else:
					if dr % 8 < idx % 8:
						same_dr_u = True
					if self.tile['piece'][dr].color == self.tile['piece'][idx].color:
							same_dr_u = True
					if not same_dr_u and not swap_dr_u:
						moves.append(dr)
					if self.tile['piece'][dr].color != 'empty' and self.tile['piece'][dr].color != self.tile['piece'][idx].color:
						swap_dr_u = True
		return moves

	def knight_moves(self, idx):
		all_moves = []
		moves = []
		i = [0, 16, 8]
		for n, val in enumerate(i):
			if n == 0:
				continue
			k = idx - val + n
			all_moves.append(k)
			k = idx - val - n
			all_moves.append(k)
			k = idx + val + n
			all_moves.append(k)
			k = idx + val - n
			all_moves.append(k)
		for m in all_moves:
			if abs(idx % 8 - m % 8) <= 2:
				if m < 64 and m >= 0:
					moves.append(m)
		return moves
	
	def king_moves(self, idx):
		moves = []
		m = [-9, -1, 7, -8, 8, -7, 1, 9]
		for i, val in enumerate(m):
			if (idx % 8 == 7 and i > 4) or (idx % 8 == 0 and i < 3):
				continue
			k = idx + val
			if k < 64 and k >= 0:
				if self.tile['piece'][idx].color != self.tile['piece'][k].color:
					moves.append(k)
		return moves

	def pawn_moves_helper(self, piece, p, idx, moves):
		if piece[p].color != 'empty' and piece[p].color != piece[idx].color:
			moves.append(p)
		return moves 

	def pawn_moves(self, idx):
		moves = []
		if self.tile['piece'][idx].color == 'white':
			p = idx - 8
			if self.tile['piece'][p].piece == None:
				moves.append(p)
				if idx >= 48 and idx <= 55:
					if self.tile['piece'][p - 8].piece == None:
						moves.append(p - 8)
			if p % 8 < 7:
				moves = self.pawn_moves_helper(self.tile['piece'], p + 1, idx, moves)
			if p % 8 > 0:
				moves = self.pawn_moves_helper(self.tile['piece'], p - 1, idx, moves)
		else:
			p = idx + 8
			if self.tile['piece'][p].piece == None:
				moves.append(p)
				if idx >= 8 and idx <= 15:
					if self.tile['piece'][p + 8].piece == None:
						moves.append(p + 8)
			if p % 8 < 7:
				moves = self.pawn_moves_helper(self.tile['piece'], p + 1, idx, moves)
			if p % 8 > 0:
				moves = self.pawn_moves_helper(self.tile['piece'], p - 1, idx, moves)
		return moves

	def move_valid(self, idx, moves):
		if self.settings['DevMode'] is ENABLED:
			return moves
		valid_moves = []
		for m in moves:
			old = self.tile['piece'][idx]
			new = self.tile['piece'][m]
			self.tile['piece'][idx] = Piece(None)
			self.tile['piece'][m] = old
			if not self.in_check(old.color):
				valid_moves.append(m)
			self.tile['piece'][idx] = old
			self.tile['piece'][m] = new
		return valid_moves

	def possible_moves(self, idx):
		moves = []
		if self.tile['piece'][idx].piece == 'Pawn':
			moves = self.pawn_moves(idx)
		elif self.tile['piece'][idx].piece == 'Knight':
			all_moves = self.knight_moves(idx)
			for m in all_moves:
				if self.tile['piece'][m].color != self.tile['piece'][idx].color:
					moves.append(m)
		elif self.tile['piece'][idx].piece == 'King':
			moves = self.king_moves(idx)
		elif self.tile['piece'][idx].piece == 'Rook':
			moves = self.straight_moves(idx)
		elif self.tile['piece'][idx].piece == 'Bishop':
			moves = self.diagonal_moves(idx)
		elif self.tile['piece'][idx].piece == 'Queen':
			moves = self.straight_moves(idx) + self.diagonal_moves(idx)
		return self.move_valid(idx, moves)
		
	def pawn_conversion(self, color):
		for piece in self.piece_path:
			if color in piece and not 'King' in piece and not 'Pawn' in piece:
				# TODO make options for pawn conversions
				path = './Piece/' + color + 'Queen' + '.png'
		return Piece(path)

	def move_piece(self, selection, tile_selected):
		update_tile = None
		capture = self.tile['piece'][selection]
		piece = self.tile['piece'][tile_selected]
		# pawn conversion check
		if piece.piece == 'Pawn':
			if piece.color == 'white' and selection >= 0 and selection < 8:
				update_tile = self.pawn_conversion('white')
			elif piece.color == 'black' and selection >= 56 and selection < 64:
				update_tile = self.pawn_conversion('black')
		# convert pawn
		if update_tile is not None:
			update_tile.rect.center = self.checker[selection].center
			self.piece_sprites.add(update_tile)
			self.piece_sprites.remove(self.tile['piece'][tile_selected])
		# move piece
		else:
			update_tile = piece
			self.tile['piece'][tile_selected].rect.center = self.checker[selection].center
		self.tile['piece'][tile_selected] = Piece(None)
		if capture.piece is not None:
			score = self.piece_value[capture.piece] * 10
			if capture.color != 'white':
				self.white_score += score
				if self.settings['Captures'] is ENABLED:
					capture.rect.center = self.captured_section[1][self.blacks_captured].center
				self.blacks_captured += 1
			if capture.color != 'black':
				self.black_score += score
				if self.settings['Captures'] is ENABLED:
					capture.rect.center = self.captured_section[0][self.whites_captured].center
				self.whites_captured += 1
			self.draw_score(True, capture.color)
			self.captured_pieces.append(capture)
			if self.settings['Captures'] is not ENABLED:
				self.piece_sprites.remove(capture)
		self.tile['piece'][selection] = update_tile

	def in_check(self, color):
		checks = []
		for idx, tile in enumerate(self.tile['piece']):
			if tile.piece == 'King' and tile.color == color:
				moves = self.straight_moves(idx)
				for m in moves:
					p = self.tile['piece'][m]
					if p.color != 'empty' and p.color != tile.color and (p.piece == 'Rook' or p.piece == 'Queen'):
						checks.append((p.piece, m))
				moves = self.diagonal_moves(idx)
				for m in moves:
					p = self.tile['piece'][m]
					if p.color != 'empty' and p.color != tile.color:
						if p.piece == 'Pawn':
							if tile.color == 'black':
								if m == idx + 9 or m == idx + 7:
									checks.append((p.piece, m))
							else:
								if m == idx - 9 or m == idx - 7:
									checks.append((p.piece, m))
						if p.piece == 'Bishop' or p.piece == 'Queen':
							checks.append((p.piece, m))
				moves = self.knight_moves(idx)
				for m in moves:
					p = self.tile['piece'][m]
					if p.color != 'empty' and p.color != tile.color and p.piece == 'Knight':
						checks.append((p.piece, m))
				moves = self.king_moves(idx)
				for m in moves:
					p = self.tile['piece'][m]
					if p.color != 'empty' and p.color != tile.color and p.piece == 'King':
						checks.append((p.piece, m))
		return checks

	def checkmate(self, color):
		options = []
		for i in range(64):
			p = self.tile['piece'][i]
			if p.color == color:
				options.extend(self.possible_moves(i))
		return not options

	def cycle_color(self, idx, color):
		if self.tile['color'][idx] == color:
			if ((idx % 8) + (idx // 8)) % 2 == 0:
				self.tile['color'][idx] = WHITE_TILE
			else:
				self.tile['color'][idx] = BLACK_TILE
		else:
			self.tile['color'][idx] = color
		pygame.draw.rect(self.screen, self.tile['color'][idx], self.tile['rect'][idx])
		self.piece_sprites.draw(self.screen)

	def unhighlight(self, idx):
		self.cycle_color(idx, SELECTED)
		for idx, p in enumerate(self.tile['color']):
			if p == HINT:
				self.cycle_color(idx, HINT)
		return False

	def cooldown(self):
		current_time = pygame.time.get_ticks()
		return not current_time - self.click_time >= self.click_cooldown 

	def check_turn(self):
		for color, val in self.turn.items():
			if val is True:
				return color

	def display_turn(self):
		self.font = pygame.font.SysFont(FONT, FONT_SIZE*4)
		color = self.check_turn()
		if color == 'white':
			c = self.font.render('WHITE TURN', True, FONT_COLOR, 'Black')
		else:
			c = self.font.render('BLACK TURN', True, FONT_COLOR, 'Black')
		if self.checkmate(color):
			c = self.font.render('GAME  OVER', True, FONT_COLOR, 'Black')
		c_r = c.get_rect()
		c_r.center = (self.checker[3].right, self.captured_section[0][3].top)
		c_r.bottom = self.captured_section[0][3].top - (OFFSET * 5)
		self.screen.blit(c, c_r)

	def undo_capture(self, color, piece, to_idx):
		score = self.piece_value[piece] * 10
		if color != 'white':
			self.white_score -= score
			self.draw_score(self.white_score != 0, color)
			self.blacks_captured -= 1
			i = 1
			j = self.blacks_captured
		elif color != 'black':
			self.black_score -= score
			self.draw_score(self.black_score != 0, color)
			self.whites_captured -= 1
			i = 0
			j = self.whites_captured
		box_colors = [CAPTURED_W, CAPTURED_B]
		p = self.captured_section[i][j]
		for x in self.piece_sprites:
			if x.rect.center == p.center:
				pygame.draw.rect(self.screen, box_colors[i], p)
		captured = self.captured_pieces.pop()
		captured.rect.center = self.checker[to_idx].center
		self.piece_sprites.add(captured)
		self.tile['piece'][to_idx] = captured

	def un_convert_pawn(self, color, to_idx, from_idx):
		path = './Piece/' + color + 'Pawn' + '.png'
		self.piece_sprites.remove(self.tile['piece'][to_idx])
		update = Piece(path)
		update.rect.center = self.checker[from_idx].center
		self.piece_sprites.add(update)
		self.tile['piece'][to_idx] = update

	def undo_last_move(self):
		if not self.move_list:
			return
		_, __, from_idx, color, piece, to_idx = self.move_list.pop()
		if __ == 'Pawn':
			if _ == 'white' and to_idx < 8:
				self.un_convert_pawn(_, to_idx, from_idx)
			elif _ == 'black' and to_idx >= 56:
				self.un_convert_pawn(_, to_idx, from_idx)		
		update = self.tile['piece'][to_idx]
		self.tile['piece'][to_idx].rect.center = self.checker[from_idx].center
		if piece is not None:
			self.undo_capture(color, piece, to_idx)
		else:
			self.tile['piece'][to_idx] = Piece(None)
		print(f'{_} {__} {from_idx} {color} {piece} {to_idx}')
		self.tile['piece'][from_idx] = update
		self.piece_sprites.draw(self.screen)
		if self.settings['DevMode'] is not ENABLED:
			self.turn['white'] = not self.turn['white']
			self.turn['black'] = not self.turn['black']
			self.display_turn()

	def restart(self):
		self.piece_sprites.empty()
		self.tile['piece'] = [Piece(None) for _ in range(64)]
		for i, t in enumerate(self.tile['rect']):
			pygame.draw.rect(self.screen, self.tile['color'][i], t)
		self.draw_pieces()
		self.turn['white'] = True
		self.turn['black'] = True
		if self.settings['DevMode'] is not ENABLED:
			self.turn['white'] = self.settings['WhiteFirst']
			self.turn['black'] = not self.settings['WhiteFirst']
			self.display_turn()
		self.blacks_captured = 0
		self.whites_captured = 0
		self.black_score = 0
		self.white_score = 0
		self.captured_section = [[],[]]
		self.captured_pieces = []			
		self.move_list = []
		self.draw_captured_section()
		self.draw_score(False, None)
		pygame.display.flip()

	def click_event(self, click, screen, area):
		if click[0]:
			mouse_pos = pygame.mouse.get_pos()
			if screen.get_parent() is not None:
				mouse_pos = tuple(map(lambda i, j: i - j, mouse_pos, screen.get_offset()))
			for idx, tile in enumerate(area):
				if tile.collidepoint(mouse_pos):
					return idx
		return False

	def run(self):
		tile_selected = False
		selection = False
		if self.settings['DevMode'] is ENABLED:
			self.turn['black'] = True
		else:
			self.display_turn()
		pygame.display.update()
		while True:
			self.clock.tick(FPS)
			while self.cooldown():
				pass
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_p:
						if self.settingd:
							continue
						self.paused = not self.paused
						if self.paused:
							self.draw_pause()
						else:
							self.unpause()
						continue
					if event.key == pygame.K_ESCAPE:
						if self.paused:
							continue
						self.settingd = not self.settingd
						if self.settingd:
							self.draw_settings()
						else:
							self.unpause()
						continue
			if self.paused is True:
				if self.pause_menu()is not False:
					if tile_selected is not False:
						tile_selected = self.unhighlight(tile_selected)
						pygame.display.update()
				continue
			if self.settingd is True:
				if self.settings_menu() is not False:
					self.restart()
				continue
			click = pygame.mouse.get_pressed()
			if click[0] == True:
				self.click_time = pygame.time.get_ticks()
			selection = self.click_event(click, self.screen, self.checker)
			if selection is not False:
				if tile_selected is False and self.tile['piece'][selection].piece != None:
					if self.settings['DevMode'] is not ENABLED:
						color = self.check_turn()
						if color != self.tile['piece'][selection].color:
							continue
					self.cycle_color(selection, SELECTED)
					hints = self.possible_moves(selection)
					for m in hints:
						self.cycle_color(m, HINT)
					tile_selected = selection
				elif selection == tile_selected:
					tile_selected = self.unhighlight(selection)
				elif self.tile['color'][selection] == HINT: # Valid move
					self.move_list.append((self.tile['piece'][tile_selected].color, self.tile['piece'][tile_selected].piece, tile_selected, self.tile['piece'][selection].color, self.tile['piece'][selection].piece, selection))
					self.move_piece(selection, tile_selected)
					tile_selected = self.unhighlight(tile_selected)
					self.piece_sprites.draw(self.screen)
					if self.settings['DevMode'] is not ENABLED:
						self.turn['white'] = not self.turn['white']
						self.turn['black'] = not self.turn['black']
						self.display_turn()
				pygame.display.update()
				
if __name__ == '__main__':
	game = Game()
	game.draw_board()
	game.draw_pieces()
	game.init_menu('Pause')
	game.init_menu('Settings')
	game.draw_captured_section()
	game.draw_score(False, None)
	game.run()
