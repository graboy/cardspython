from random import randint
from thread import start_new_thread
import sys, socket, time

#threading for players needs to be implemented before this will work

HOST = ''
PORT = 8000
PLAYER_DICT = {}

wcards = open('wcards.txt', 'r').read().split('<>')
bcards = open('bcards.txt', 'r').read().split('<>')

def choosehand(wcards):
	hand = {}
	for i in range(1,8):
		hand[i] = wcards[randint(1, len(wcards))]
	return hand

def choosebcard(bcards):
	return bcards[randint(0, len(bcards))]

def player(bcard, conn):
	hand = choosehand(wcards)
	chosen = []
	
	conn.send('\nBlack Card:\n%s' % bcard)
	conn.send('\nYour hand:\n')
	for i in hand:
		conn.send('%s: %s\n' % (i, hand[i]))
	conn.send('Select your card number(s): ')
	input = conn.recv(1024).split()
	for i in input:
		try:
			chosen.append(hand[int(i)])
		except Exception:
			conn.send('\nInvalid card number %s' % i)
			continue
	print 'Player %s has played.' % [i for key,value in PLAYER_DICT.items()][0]
	return chosen
	
def judge(bcard, conn, sets):
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

def checkjudge(sets):
	return (len(sets.keys()) == len(PLAYER_DICT.keys()))

def playround():
	while 1:
		bcard = choosebcard(bcards)
		sets = {}
		index = randint(0, len(PLAYER_DICT.values()) - 1)
		jplayer = PLAYER_DICT.values()[index]
		for i in PLAYER_DICT.values():
			if i == jplayer:
				jplayer.send('Waiting for other players to move...')
			else:
				sets[i] = start_new_thread(player, (bcard, i, ))
		while checkjudge(sets) == False: time.sleep(1)
		start_new_thread(judge, (bcard, jplayer, sets))
				
def clientthread(conn, addr):	
	conn.send('Connected to server. What is your name?')
	name = str(conn.recv(1024).strip('\r\n'))
	PLAYER_DICT[name] = conn
	print 'New player %s at %s:%s.' % (name, addr[0], str(addr[1]))
	conn.send('Waiting for someone to start game...')
	start = conn.recv(1024).strip('\r\n')
	if start == 'start':
		playround()

def startsocket():
	try: s.bind((HOST, PORT))
	except socket.error:
		print 'Port %i in use, wait a minute and try again.' % PORT
		sys.exit()
	s.listen(10)
	print 'Started server on port %i.' % PORT
	while 1:
		conn, addr = s.accept()
		start_new_thread(clientthread,(conn, addr, ))
		
if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try: startsocket()
	except KeyboardInterrupt:
		s.close()
		print ' Stopping...'
		sys.exit()
