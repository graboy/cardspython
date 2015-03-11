#!/bin/env python2.7

from random import randint
import threading
import sys, socket

HOST = ''
PORT = 8000
PLAYER_DICT = {}
PLAYER_DICT_LOCK = threading.Lock()

# FIXME Close files and do error handling
wcards = open('wcards.txt', 'r').read().split('<>')
bcards = open('bcards.txt', 'r').read().split('<>')

def choosehand(wcards):
	hand = {}
	for i in range(1,8):
		hand[i] = wcards[randint(1, len(wcards))]
	return hand

def choosebcard(bcards):
	return bcards[randint(0, len(bcards))]

def playround():
	# Choose judge, run threads
	bcard = choosebcard(bcards)
	index = randint(0, len(PLAYER_DICT.values()) - 1)
	jplayer = PLAYER_DICT.values()[index]
	players = [player for player in PLAYER_DICT.values() if player != jplayer]
	for player in players:
		player.judge = False
		player.bcard = bcard
		# Let player run
		player.runlock.release()

	jplayer.send('Waiting for other players to move...')
	for player in players:
		player.runlock.acquire()

	jplayer.judge = True
	jplayer.bcard = bcard

	# Let judge run
	judge.runlock.release()
	judge.runlock.acquire()

class ClientThread(threading.Thread):
	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr
		self.player = getname()
		self.runlock = threading.Lock()
		self.alive = True
		print 'New player %s at %s:%s.' % (self.name, self.addr[0], self.addr[1])

	def run(self):
		while self.alive:
			self.runlock.acquire()
			if self.judge:
				self.judge(self.bcard)
			else:
				self.player(self.bcard)
			self.runlock.release()

	def getname(self):
		self.conn.send('Connected to server. What is your name?')
		player = self.conn.recv(1024).strip()

		PLAYER_DICT_LOCK.acquire()
		while player in PLAYER_DICT:
			PLAYER_DICT_LOCK.release()
			self.conn.send('Name taken, try another.')
			player = self.conn.recv(1024).strip()
			PLAYER_DICT_LOCK.acquire()

		PLAYER_DICT[player] = self
		PLAYER_DICT_LOCK.release()
		return player

	def player(bcard):
		hand = choosehand(wcards)
		self.chosen = []
		
		self.conn.send('\nBlack Card:\n%s' % bcard)
		self.conn.send('\nYour hand:\n')
		for i in hand:
			self.conn.send('%s: %s\n' % (i, hand[i]))
		self.conn.send('Select your card number(s): ')
		input = self.conn.recv(1024).split()
		for i in input:
			try:
				chosen.append(hand[int(i)])
			except IndexError, ValueError:
				self.conn.send('\nInvalid card number %s' % i)
				# FIXME Could this stop them from taking their turn?
				continue
		print 'Player %s has played.' % self.player

	def judge(bcard):
		sets = []
		players = PLAYER_DICT.values()
		for player in players:
			if player == self:
				continue
			sets.append(player.chosen)

		conn.send('\nBlack Card:\n%s' % bcard)
		conn.send('\nChoose the best card or set of cards:\n')
		secret = {}
		for i, j in zip(sets, range(1, len(sets) + 1)):
			secret[j] = i
			conn.send('%s: %s\n' % (j, sets[i]))
		conn.send('Selection:\n')
		input = conn.recv(1024)
		winner = secret[int(input)]
		conn.sendall('%s wins!\nSelected card(s): %s\n' % (winner, sets[winner]))
	
	def destroy(self):
		pass

class ConnectionWatcherThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.alive = True

	def run():
		while self.alive:
			conn, addr = s.accept()
			start_new_thread(clientthread, (conn, addr))

def startsocket():
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((HOST, PORT))
	s.listen(10)
	print 'Started server on port %i.' % PORT

if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		startsocket()
		cw = ConnectionWatcherThread()
		while 1:
			# FIXME block until enough players have connected.
			playround()

	except KeyboardInterrupt:
		print ' Stopping...'
	except socket.error:
		print 'Port %i in use, wait a minute and try again.' % PORT
	finally:
		s.close()
