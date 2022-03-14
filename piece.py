import pygame, re
from os import walk

PIECE_SCALE	= 48

class Piece(pygame.sprite.Sprite):
	def __init__(self, path):
		if path is not None:
			pygame.sprite.Sprite.__init__(self)
			self.image = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (PIECE_SCALE, PIECE_SCALE))
			self.rect = self.image.get_rect()

			x = re.search('([^/]*)(.png)', path).group(1)
			self.color = re.split('(?=[A-Z])', x)[0]
			self.piece = re.split('(?=[A-Z])', x)[1]
		else:
			self.image = path
			self.rect = path
			self.color = 'empty'
			self.piece = path

def import_pieces():
	piece_list = []
	path = './Piece/'
	for _,__,img_data in walk(path):
		for img in img_data:
			full_path = path + img
			piece_list.append(full_path)
	return piece_list
