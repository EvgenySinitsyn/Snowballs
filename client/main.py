import pygame as pg
from objects import Player, Aim
import socket
import pickle
import time



class App:
	def __init__(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			self.sock.connect(('localhost', 10000))
			print('Подключился')
		except Exception as ex:
			print(ex)

		self.RESOLUTION = self.WIDTH, self.HEIGHT = 1080, 720
		pg.init()
		self.screen = pg.display.set_mode(self.RESOLUTION)
		self.surface = pg.Surface(self.RESOLUTION)
		self.clock = pg.time.Clock()
		self.objects = []
		pg.font.init()
		self.text = pg.font.SysFont('Arial', 40, bold=True)
		pg.mouse.set_visible(False)
		self.mouse_pos = pg.mouse.get_pos()
		self.players = ((self, (pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN), 'right', 50, 250), (self, (pg.K_a, pg.K_d, pg.K_w, pg.K_s, pg.K_f), 'left', self.WIDTH - 150, 250))
		self.bg = pg.transform.scale(pg.image.load('images/bg.jpg'), self.RESOLUTION)
		self.players_count = 0


	def draw(self):

		self.surface.blit(self.bg, (0, 0))
		for obj in self.objects:
			if isinstance(obj, Player):
				obj.acts = self.data.pop(0)
			obj.draw()
		self.screen.blit(self.surface, (0, 0))

	def run(self):
		while True:
			#состояние мыши и клавиатуры
			self.mouse_buttons = pg.mouse.get_pressed()
			self.mouse_pos = pg.mouse.get_pos()
			self.pressed_keys = pg.key.get_pressed()

			#отправка данных на сервер
			try:
				self.message = pickle.dumps((self.mouse_buttons, self.mouse_pos, self.pressed_keys))
				self.sock.send(self.message)
			except Exception as ex:
				pass

			#прием данных с сервера
			try:
				self.data = self.sock.recv(4096)
				if not self.data: continue
				self.data = pickle.loads(self.data)

			#Создание игрока если произошло новое подключение к серверу
				if isinstance(self.data, str):
					for i in range(int(self.data.split()[1])):
						if not hasattr(self, f'player_{i}'):
							self.__setattr__(f'player_{i}', Player(*self.players[i]))
							self.players_count += 1
							print(f'Игрок player_{i} создан')
					if not hasattr(self, 'your_player'):
						self.your_player = self.__getattribute__(f'player_{i}')

					continue
			except Exception as ex:
				print(ex)
				# continue
			#Запись текущего состояния игроков
			if not isinstance(self.data, list) or len(self.data) < self.players_count:
				continue
			self.draw()
			[exit() for i in pg.event.get() if i.type == pg.QUIT]
			pg.display.update()
			self.clock.tick(30)


if __name__ == '__main__':
	App().run()