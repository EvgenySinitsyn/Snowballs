import pygame as pg
import math


class Player:
	def __init__(self, app, keys, direction, x=300, y=200):
		# объект главного приложения
		self.app = app
		self.app.objects.append(self)

		# хранение параметров объекта
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

		# начальные параметры
		self.frame = 0
		self.x, self.y = x, y
		self.speed = 7
		self.direction = direction
		self.health = 200
		self.set_image()
		self.aim = Aim(self)

	def set_image(self):
		"""
		Установка текущего изображения персонажа
		"""
		self.image = self.sheet.subsurface((64 * self.frame, 64 * self.movements[self.direction], 64, 64))
		self.image = pg.transform.scale(self.image, (128, 128))

	# pg.draw.rect(self.image, 'blue', self.image.get_rect())

	def update(self):
		"""
		Обновление параметров персонажа
		"""
		self.set_direction()
		keys = self.acts[2]
		mouse_buttons = self.acts[0]
		self.movement = []
		if keys[self.keys['left']]:
			self.movement.append('left')

		if keys[self.keys['right']]:
			self.movement.append('right')

		if keys[self.keys['up']]:
			self.movement.append('up')

		if keys[self.keys['down']]:
			self.movement.append('down')
		if self.movement:
			self.move()
		if not (keys[self.keys['down']] or keys[self.keys['up']] or keys[self.keys['right']] or keys[
			self.keys['left']]):
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
				self.snowball.lenv = ((self.aim.pos[0] - self.snowball.x) ** 2 + (
						self.aim.pos[1] - self.snowball.y) ** 2) ** 0.5
				v = (self.aim.pos[0] - self.snowball.x) / self.snowball.lenv, (
						self.aim.pos[1] - self.snowball.y) / self.snowball.lenv
				self.snowball.v = (v[0] * self.snowball.speed, v[1] * self.snowball.speed)
				self.snowball.flying = True
				self.__delattr__('snowball')

	def move(self):
		"""
		Изменение положения персонажа
		"""
		if not self.app.waiting:
			self.frame = self.frame + 1 if self.frame < 8 else 0
			div_dpos = len(self.movement)
			dx, dy = 0, 0
			coef = len(self.movement)
			for move in self.movement:
				dx += self.directions[move][0] / coef ** 0.5
				dy += self.directions[move][1] / coef ** 0.5
			self.set_image()
			if 0 < self.x + dx * self.speed + 64 < self.app.WIDTH:
				self.x += dx * self.speed
			if 0 < self.y + dy * self.speed + 64 < self.app.HEIGHT:
				self.y += dy * self.speed

	def get_damage(self, damage):
		"""
		Получение урона персонажем
		"""
		self.health -= damage
		print(self.health)
		if self.health <= 0:
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

	def get_speed_bar(self):
		speed_bar = pg.Surface((214, 52))
		speed_bar.fill('blue')
		if hasattr(self, 'snowball'):
			pg.draw.rect(speed_bar, 'green', (2, 2, self.snowball.speed * 3, 47))
		return speed_bar

	def get_health_bar(self):
		health_bar = pg.Surface((128, 20))
		health_bar.fill('black')

		pg.draw.rect(health_bar, 'white', (2, 2, 124, 16))
		r = 255 - int(255 / 200 * self.health)
		g = int(255 / 200 * self.health)
		pg.draw.rect(health_bar, (r, g, 0), (2, 2, 124 / 200 * self.health, 16))
		return health_bar

	def draw(self):
		"""
		Отрисовка персонажа
		"""
		self.update()
		speed_bar = self.get_speed_bar()
		health_bar = self.get_health_bar()
		if self is self.app.your_player:
			self.app.surface.blit(speed_bar, (10, 10))
		self.app.surface.blit(self.image, (self.x, self.y))
		self.app.surface.blit(health_bar, (self.x, self.y - 30))


class Snowball:
	def __init__(self, player):
		self.player = player  # игрок, выпустивший снежок

		# начальные параметры
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

	def grow(self):

		if self.frame < 8:
			self.frame += 1
		if self.speed < self.max_speed:
			self.speed += .5
		self.image = self.sheet.subsurface(100 * self.frame, 0, 100, 100)

	# pg.draw.rect(self.image, 'red', self.image.get_rect())

	# pg.draw.rect(self.image, 'red', (0, 0, 100, 100))

	def destroy(self):
		self.player.app.objects.remove(self)
		del self

	def update(self):
		if self.flying:
			if 0 <= self.x <= self.player.app.WIDTH and -200 <= self.y <= self.player.app.HEIGHT and self.passed_range <= self.lenv:
				for obj in self.player.app.objects:
					if not obj is self.player and not obj is self and not isinstance(obj, Aim):
						if self.image.get_rect(center=(self.x, self.y)).colliderect(
								obj.image.get_rect(center=(obj.x, obj.y))):
							if isinstance(obj, Player):
								self.destroy()
								obj.get_damage(self.speed)

				self.warper += 2
				self.x += self.v[0]
				self.y += self.v[1] + self.warper
				self.passed_range += (self.v[0] ** 2 + (self.v[1] + self.warper) ** 2) ** 0.5
				self.passed_frames += 1
				try:
					if self.passed_frames > self.limit_frames:
						self.destroy()
				except:
					pass

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
