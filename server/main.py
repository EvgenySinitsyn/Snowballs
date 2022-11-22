import socket
import pickle
import pygame as pg

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('192.168.99.70', 10000))
main_socket.setblocking(0)
main_socket.listen(5)
print('Сокет создан')
players_sockets = []
clock = pg.time.Clock()

while True:
	acts = []
	try:
		new_socket, addr = main_socket.accept()
		print('Подключился ', addr)
		new_socket.setblocking(0)
		players_sockets.append(new_socket)
		mess = f'Create {len(players_sockets)}'
		for sock in players_sockets:
			sock.send(pickle.dumps(mess))

	except:
		pass

	for sock in players_sockets:

		try:
			data = sock.recv(4096)

			data = pickle.loads(data)
			acts.append(data)
		except Exception as ex:
			print(ex)


	for sock in players_sockets:
		try:
			sock.send(pickle.dumps(acts))
		except Exception as ex:
			print(ex)
			players_sockets.remove(sock)
			sock.close()
			print('Отключился игрок')

	clock.tick(30)