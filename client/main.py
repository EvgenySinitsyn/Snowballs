import pygame as pg
from objects import Player
import socket
import pickle


class App:
	def __init__(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			self.sock.connect(('192.168.99.70', 10000))
			print('Подключился')
		except Exception as ex:
			print(ex)
		self.FPS = 60
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
		self.controls = pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN
		self.players_settings = (
		(self, self.controls, 'right', 50, 250), (self, self.controls, 'left', self.WIDTH - 150, 250))
		self.bg = pg.transform.scale(pg.image.load('images/bg.jpg'), self.RESOLUTION)
		self.players_count = 0
		self.objects = dict(broken_snowballs=[], players=[], snowballs=[], aims=[], )

		self.waiting = True

	def draw(self):
		self.surface.blit(self.bg, (0, 0))
		for player in self.objects['players']:
			player.acts = self.data.pop(0)
		for l in self.objects:
			for obj in self.objects[l]:
				obj.draw()
		if self.waiting:
			self.surface.blit(pg.font.SysFont('arial', size=20).render('Ожидание второго игрока', True, 'red'),
							  (self.WIDTH - 200, 10))
		self.screen.blit(self.surface, (0, 0))

	def run(self):
		while True:
			# состояние мыши и клавиатуры
			self.mouse_buttons = pg.mouse.get_pressed()
			self.mouse_pos = pg.mouse.get_pos()
			self.pressed_keys = pg.key.get_pressed()

			# отправка данных на сервер
			try:
				self.message = pickle.dumps((self.mouse_buttons, self.mouse_pos, self.pressed_keys))
				self.sock.send(self.message)
			except Exception as ex:
				pass

			# прием данных с сервера
			try:
				self.data = self.sock.recv(4096)
				if not self.data: continue
				self.data = pickle.loads(self.data)

				# Создание игрока если произошло новое подключение к серверу
				if isinstance(self.data, str):
					for i in range(int(self.data.split()[1])):
						if not hasattr(self, f'player_{i}'):
							self.__setattr__(f'player_{i}', Player(*self.players_settings[i]))
							self.players_count += 1
							print(f'Игрок player_{i} создан')
					if not hasattr(self, 'your_player'):
						self.your_player = self.__getattribute__(f'player_{i}')
					if self.players_count > 1: self.waiting = False
					continue
			except Exception as ex:
				print(ex)
			# continue
			# Запись текущего состояния игроков
			if not isinstance(self.data, list) or len(self.data) < self.players_count:
				continue
			self.draw()
			[exit() for i in pg.event.get() if i.type == pg.QUIT]
			pg.display.update()
			# self.clock.tick(self.FPS)


if __name__ == '__main__':
	App().run()
