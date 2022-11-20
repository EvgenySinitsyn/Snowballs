import pygame as pg
import math


class Player:
	def __init__(self, app, keys, direction, x=300, y=200):
		#объект главного приложения
		self.app = app
		self.app.objects.append(self)

		#хранение параметров объекта
		self.sheet = pg.image.load('images/human.png')
		self.movements = {
			'up': 8,
			'left': 9,
			'down': 10,
			'right': 11
		}
		self.directions = {
			'left': (-1, 0),
			'right': (1, 0),
			'up': (0, -1),
			'down': (0, 1)
		}
		self.keys = {
			'left': keys[0],
			'right': keys[1],
			'up': keys[2],
			'down': keys[3],
		}
		self.shot_timer = 0
		self.shot_delay = 30

		#начальные параметры
		self.frame = 0
		self.x, self.y = x, y
		self.speed = 5
		self.direction = direction
		self.health = 5
		self.set_image()
		self.aim = Aim(self)

	def set_image(self):
		"""
		Установка текущего изображения персонажа
		"""
		self.image = self.sheet.subsurface((64 * self.frame, 64 * self.movements[self.direction], 64, 64))
		self.image = pg.transform.scale(self.image, (128, 128))

	def update(self):
		"""
		Обновление параметров персонажа
		"""
		self.set_direction()
		keys = self.acts[2]
		mouse_buttons = self.acts[0]
		if keys[self.keys['left']]:
			self.movement = 'left'
			self.move()
		if keys[self.keys['right']]:
			self.movement = 'right'
			self.move()
		if keys[self.keys['up']]:
			self.movement = 'up'
			self.move()
		if keys[self.keys['down']]:
			self.movement = 'down'
			self.move()
		if not (keys[self.keys['down']] or keys[self.keys['up']] or keys[self.keys['right']] or keys[self.keys['left']]):
			self.frame = 0
			self.set_image()

		if mouse_buttons[0]:
			if not hasattr(self, 'snowball'):
				self.snowball = Snowball(self)
			else:
				self.snowball.grow()
		else:
			if hasattr(self, 'snowball'):
				self.snowball.passed_frames = 0
				# self.snowball.alpha = self.alpha
				# self.snowball.start_pos = (self.snowball.x, self.snowball.y)
				self.snowball.target = self.aim.pos
				self.snowball.lenv = ((self.aim.pos[0] - self.snowball.x) ** 2 + (self.aim.pos[1] - self.snowball.y) ** 2) ** 0.5
				v = (self.aim.pos[0] - self.snowball.x) / self.snowball.lenv, (self.aim.pos[1] - self.snowball.y) / self.snowball.lenv
				self.snowball.v = (v[0] * self.snowball.speed, v[1] * self.snowball.speed)
				self.snowball.flying = True
				self.__delattr__('snowball')




	def get_damage(self):
		"""
		Получение урона персонажем
		"""
		print(self.health)
		if self.health > 1:
			self.health -= 1
		else:
			self.health = 0
			self.app.objects.remove(self)

	def set_direction(self):
		"""
		Направление персонажа в соответствии с положением прицела
		"""
		self.alpha = math.atan2(self.acts[1][1] - self.y, self.acts[1][0] - self.x)
		if -math.pi / 4 <= self.alpha < math.pi / 4:
			self.direction = 'right'
		elif math.pi / 4 <= self.alpha < 3 * math.pi / 4:
			self.direction = 'down'
		elif -math.pi <= self.alpha < -3 * math.pi / 4 or 3 * math.pi / 4 <= self.alpha < math.pi:
			self.direction = 'left'
		else:
			self.direction = 'up'

	def move(self):
		"""
		Изменение положения персонажа
		"""
		self.frame = self.frame + 1 if self.frame < 8 else 0
		dpos = self.directions[self.movement]
		self.set_image()
		self.x += dpos[0] * self.speed
		self.y += dpos[1] * self.speed

	def draw(self):
		"""
		Отрисовка персонажа
		"""
		self.update()
		self.app.surface.blit(self.image, (self.x, self.y))


class Snowball:
	def __init__(self, player):
		self.player = player	#игрок, выпустивший снежок

		#начальные параметры
		self.x = self.player.x + 64 + self.player.directions[self.player.direction][0] * 50 - 50
		self.y = self.player.y + 64 + self.player.directions[self.player.direction][1] * 50 - 50
		self.speed = 12
		self.max_speed = 70



		self.player.app.objects.append(self)
		self.sheet = pg.image.load('images/snowball.png')
		self.flying = False
		self.frame = 0
		self.image = self.sheet.subsurface(100 * self.frame, 0, 100, 100)
		self.passed_range = 0
		self.warper = -15
		self.limit_frames = 15
		# pg.draw.rect(self.image, 'red', (0, 0, 100, 100))

	def grow(self):

		if self.frame < 8:
			self.frame += 1
		if self.speed < self.max_speed:
			self.speed += .5
		self.image = self.sheet.subsurface(100 * self.frame, 0, 100, 100)
		# pg.draw.rect(self.image, 'red', (0, 0, 100, 100))

	def destroy(self):
		self.player.app.objects.remove(self)
		del self

	def update(self):
		if self.flying:
			if 0 <= self.x <= self.player.app.WIDTH and -200 <= self.y <= self.player.app.HEIGHT and self.passed_range <= self.lenv:
				for obj in self.player.app.objects:
					if not obj is self.player and not obj is self and not isinstance(obj, Aim):
						if self.image.get_rect(center=(self.x, self.y)).colliderect(obj.image.get_rect(center=(obj.x, obj.y))):
							if isinstance(obj, Player):
								self.destroy()
								obj.get_damage()


				self.warper += 2
				self.x += self.v[0]
				self.y += self.v[1] + self.warper
				self.passed_range += (self.v[0] ** 2 + (self.v[1] + self.warper) ** 2) ** 0.5
				self.passed_frames += 1
				if self.passed_frames > self.limit_frames:
					self.destroy()

			else:
				self.destroy()
		else:
			self.x = self.player.x + 64 + self.player.directions[self.player.direction][0] * 50 - 50
			self.y = self.player.y + 64 + self.player.directions[self.player.direction][1] * 50 - 50
			self.direction = self.player.direction

	def draw(self):
		self.update()
		self.player.app.surface.blit(self.image, (self.x, self.y))


class Aim:
	def __init__(self, parent):
		self.parent = parent
		self.set_image()

		self.parent.app.objects.append(self)

	def set_image(self):
		self.image = pg.transform.scale(pg.image.load('images/aim.png'), (70, 70))

	def update(self):
		self.pos = self.parent.acts[1]

	def draw(self):
		self.update()
		if self.parent is self.parent.app.your_player:
			self.parent.app.surface.blit(self.image, self.pos)
