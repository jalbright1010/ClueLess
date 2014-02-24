#!/usr/bin/python

import socket
import thread
import time
import sys
import cPickle as pickle
import uuid
import itertools
import gameplay 

class server():
    users = {}
    sock = None
    activeGames = []
    availableGames = []
    game = None
    playersReady = None
    playerLocations = {}
    
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind((str(host), int(port)))
        self.sock.listen(1)
        print 'Listening on %s' % ('%s:%s' % self.sock.getsockname())
        self.game = gameplay.game()
        print 'Game created with id %s' % self.game.id
        self.playersReady = []
        self.acceptingConnections = True

    def accept(self):
        return self.sock.accept()

    def acceptConnection(self, conn):
        def threaded():
            while True:
                conn.send('username')
                try:
                    name = conn.recv(1024).strip()
                except socket.error:
                    print 'Socket connection error...'
                    break
                if name in self.users:
                    conn.send('Username already in use.\n')
                elif name:
                    conn.setblocking(False)
                    self.users[name] = conn
                    self.broadcastMessageToAll('+++ %s arrived +++' % name)
                    time.sleep(.1)
                    conn.send('usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                    break
        self.acceptThread = thread.start_new_thread(threaded, ())

    def broadcastMessageToAll(self, message):
        # Send a message to all users from the given name.
        print message
        for name, conn in self.users.items():
            try:
                conn.send(message + '\n')
            except:
                pass

    def broadcastMessageToUser(self, name, message):
        print message
        try:
            self.users[name].send(message + '\n')
        except:
            pass

    def createNewGame(self):
        self.game = gameplay.game()
        self.broadcastMessageToAll('Game created with id %s' % self.game.id)
        
    def joinGame(self, name, char):
        if self.game:
            if len(self.game.players) < 6:
                if char in [x.character for x in self.game.players.values()]:
                    try:
                        self.users[name].send('usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                    except:
                        pass
                else:
                    self.game.addPlayer(name, char)
                    self.broadcastMessageToAll('%s has joined the game as %s.' % (name, char))
                    self.playerLocations[char] = self.game.players[name].currentSpace.identifier
                    time.sleep(.1)
                    for name, conn in self.users.items():
                        try:
                            conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
                        except:
                            pass
            else:
                self.broadcastMessageToUser(name, 'Game already has 6 players, cannot join.')
                self.acceptingConnections = False

    def startGame(self, name):
        if self.game:
            if len(self.playersReady) == len(self.users):
                self.game.start()
                self.broadcastMessageToAll('%s has started the game! Good Luck!' % name)
                self.acceptingConnections = False
                time.sleep(.1)
                for char in gameplay.PEOPLE:
                    if char not in self.playerLocations:
                        self.playerLocations[char] = char+'Home'
                for conn in self.users.values():
                    conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
                time.sleep(.1)
                for name,conn in self.users.items():
                    conn.send('cards:'+pickle.dumps([x.identifier for x in self.game.players[name].cards]))
                self.sendTurnMessage()
            else:
                self.broadcastMessageToUser(name, 'Not all players are ready to start....')
                for name in self.users.keys():
                    if name not in self.playersReady:
                        self.broadcastMessageToUser(name, '%s is not ready to start' % name)
                        

    def movePlayer(self, name, space):
        player = self.game.players[name]
        oldSpace = player.currentSpace
	newSpace = self.game.board[space]
        if isinstance(newSpace, gameplay.hallway):
            newSpace.occupied = True
        if isinstance(newSpace, gameplay.room):
            self.users[name].send('suggestion')
        player.currentSpace = newSpace
        self.playerLocations[player.character] = newSpace.identifier
        for n,conn in self.users.items():
            if n != name: 
                conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
        if isinstance(oldSpace, gameplay.hallway):
	    oldSpace.occupied = False
        

    def sendTurnMessage(self):
        conns = []
        for conn in self.game.currentPlayer.currentSpace.connections:
            if isinstance(conn, gameplay.hallway):
                if not conn.occupied:
                    conns.append(conn)
            else:
                conns.append(conn)
        self.users[self.game.currentPlayer.name].send('yourTurn:'+pickle.dumps([x.identifier for x in conns]))
	time.sleep(.1)	
	self.broadcastMessageToAll('Awaiting %s to make his/her move...' % self.game.currentPlayer.name)

    def endTurn(self, name):
        self.broadcastMessageToAll('%s has ended his/her turn...' % name)
        self.game.turnOrder.append(self.game.turnOrder.pop(0))
        self.game.currentPlayer = self.game.turnOrder[0]
        self.sendTurnMessage()

    def makeSuggestion(self, name, pickled):
        suggestion = pickle.loads(str(pickled))
        suspect = str(suggestion[0])
        weapon = str(suggestion[1])
        room = self.game.players[name].currentSpace.identifier
        self.broadcastMessageToAll('%s suggests that the crime was committed in the %s by %s with the %s.' % (name,room,suspect,weapon)) 
        if suspect in [x.character for x in self.game.players.values()]:
            self.game.players[name].currentSpace = self.game.board[room]
        self.playerLocations[suspect] = room
        time.sleep(.1)
        for conn in self.users.values():
            conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
        for i in range(1,len(self.game.turnOrder)):
            person = self.game.turnOrder[i].name
            cards = self.game.turnOrder[i].cards
            cardIds = [x.identifier for x in cards]
            show = []
            if suspect in cardIds:
                show.append(cards[cards.index(suspect)])
            elif room in cards:
                show.append(cards[cards.index(room)])
            elif weapon in cards:
                show.append(cards[card.index(weapon)])
            if len(show) == 0:
                continue
            elif len(show) == 1:
                self.users[name].send('%s has shown you the %s card.' % (person,show[0].identifier))
                time.sleep(.1)
                self.users[person].send('You have shown %s the %s card.' % (name,show[0].identifier))
            elif len(show) > 1:
                self.users[person].send('chooseCardToShow')
            

def main():
    #s = server('192.168.41.27', 4004)
    s = server('10.0.1.10', 4004)
    
    while True:
        try:
            # Accept new connections
            if s.acceptingConnections:
                while True:
                    try:
                        conn, addr = s.accept()
                    except:
                        break
                    s.acceptConnection(conn)

            # Read from connections
            for name, conn in s.users.items():
                try:
                    message = conn.recv(1024).strip()
                except socket.error:
                    continue
                if '::' in message:
                    splt = message.split('::')
                    if splt[0] == 'function':
                        splt2 = splt[1].split(':')
                        if splt2[0] == 'createNewGame':
                            s.createNewGame()
                        elif splt2[0] == 'joinGame':
                            s.joinGame(name, splt2[1])
                        elif splt2[0] == 'ready':
                            s.broadcastMessageToAll('%s is ready to start!' % name)
                            s.playersReady.append(name)
                        elif splt2[0] == 'start':
                            s.startGame(name)
                        elif splt2[0] == 'movePlayer':
                            s.movePlayer(name,splt2[1])
                        elif splt2[0] == 'endTurn':
                            s.endTurn(name)
                        elif splt2[0] == 'makingSuggestion':
                            s.makeSuggestion(name,splt2[1])
                    elif splt[0] == 'message':
                        s.broadcastMessageToAll('%s> %s' % (name, splt[1]))
                else:
                    if not message:
                        # Empty string is given on disconnect
                        del s.users[name]
                        if s.game:
                            del s.game.players[name]
                        s.broadcastMessageToAll('--- %s leaves ---' % name)
            time.sleep(.1)
        except (SystemExit, KeyboardInterrupt):
            break

if __name__ == '__main__':
    main()
