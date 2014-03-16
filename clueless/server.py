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
                time.sleep(.05)
                conn.send('username')
                try:
                    name = conn.recv(1024).strip()
                except socket.error:
                    print 'Socket connection error...'
                    break
                if name in self.users:
                    time.sleep(.05)
                    conn.send('Username already in use.\n')
                elif name:
                    conn.setblocking(False)
                    self.users[name] = conn
                    time.sleep(.05)
                    self.broadcastMessageToAll('+++ %s arrived +++' % name)
                    time.sleep(.05)
                    conn.send('usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                    break
        self.acceptThread = thread.start_new_thread(threaded, ())

    def broadcastMessageToAll(self, message):
        # Send a message to all users from the given name.
        print message
        for name, conn in self.users.items():
            try:
                time.sleep(.05)
                conn.send(message + '\n')
            except:
                pass

    def broadcastMessageToUser(self, name, message):
        print message
        try:
            time.sleep(.05)
            self.users[name].send(message + '\n')
        except:
            pass

    def createNewGame(self):
        self.game = gameplay.game()
        time.sleep(.05)
        self.broadcastMessageToAll('Game created with id %s' % self.game.id)
        
    def joinGame(self, name, char):
        if self.game:
            if len(self.game.players) < 6:
                if char in [x.character for x in self.game.players.values()]:
                    try:
                        time.sleep(.05)
                        self.users[name].send('usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                    except:
                        pass
                else:
                    self.game.addPlayer(name, char)
                    time.sleep(.05)
                    self.broadcastMessageToAll('%s has joined the game as %s.' % (name, char))
                    self.playerLocations[char] = self.game.players[name].currentSpace.identifier
                    for name, conn in self.users.items():
                        try:
                            time.sleep(.05)
                            conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
                        except:
                            pass
            else:
                time.sleep(.05)
                self.broadcastMessageToUser(name, 'Game already has 6 players, cannot join.')
                self.acceptingConnections = False

    def startGame(self, name):
        if self.game:
            if len(self.playersReady) == len(self.users):
                self.game.start()
                time.sleep(.05)
                self.broadcastMessageToAll('%s has started the game! Good Luck!' % name)
                self.acceptingConnections = False
                time.sleep(.05)
                for char in gameplay.PEOPLE:
                    if char not in self.playerLocations:
                        self.playerLocations[char] = char+'Home'
                for conn in self.users.values():
                    time.sleep(.05)
                    conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
                for name,conn in self.users.items():
                    time.sleep(.05)
                    conn.send('cards:'+pickle.dumps([x.identifier for x in self.game.players[name].cards.values()]))
                self.sendTurnMessage()
            else:
                time.sleep(.05)
                self.broadcastMessageToUser(name, 'Not all players are ready to start....')
                for n in self.users.keys():
                    if n not in self.playersReady:
                        time.sleep(.05)
                        self.broadcastMessageToUser(name, '%s is not ready to start' % n)
                        

    def movePlayer(self, name, space):
        player = self.game.players[name]
        oldSpace = player.currentSpace
        newSpace = self.game.board[space]
        if isinstance(newSpace, gameplay.hallway):
            newSpace.occupied = True
        if isinstance(newSpace, gameplay.room):
            time.sleep(.05)
            self.users[name].send('suggestion')
        player.currentSpace = newSpace
        self.playerLocations[player.character] = newSpace.identifier
        for n,conn in self.users.items():
            if n != name: 
                time.sleep(.05)
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
        time.sleep(.05)
        self.users[self.game.currentPlayer.name].send('yourTurn:'+pickle.dumps([x.identifier for x in conns]))
	for name,conn in self.users.items():
            if name != self.game.currentPlayer.name:
                time.sleep(.05)
                self.broadcastMessageToUser(name,'Awaiting %s to make his/her move...' % self.game.currentPlayer.name)

    def endTurn(self, name):
        time.sleep(.05)
        self.broadcastMessageToAll('%s has ended his/her turn...' % name)
        self.game.turnOrder.append(self.game.turnOrder.pop(0))
        self.game.currentPlayer = self.game.turnOrder[0]
        time.sleep(.05)
        self.sendTurnMessage()

    def makeSuggestion(self, name, pickled):
        suggestion = pickle.loads(str(pickled))
        suspect = str(suggestion[0])
        weapon = str(suggestion[1])
        room = self.game.players[name].currentSpace.identifier
        time.sleep(.05)
        self.broadcastMessageToAll('%s suggests that the crime was committed in the %s by %s with the %s.' % (name,room,suspect,weapon))
        # Check if alleged suspect is part of this game
        # If so, update that player's current space
        for player in self.game.players.values():
            if player.character == suspect:
                player.currentSpace = self.game.board[room]
        self.playerLocations[suspect] = room
        # Tell everyone to redraw their gameboards
        for conn in self.users.values():
            time.sleep(.05)
            conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
        # Iterate through the list of players
        # If they have none of the suggested cards, move to the next person
        # If they have one of the cards, show it to the suggester
        # If they have more than one, send them a signal asking them to pick one
        for i in range(1,len(self.game.turnOrder)):
            person = self.game.turnOrder[i].name
            cards = self.game.turnOrder[i].cards
            show = []
            if suspect in cards:
                show.append(cards[suspect])
            if room in cards:
                show.append(cards[room])
            if weapon in cards:
                show.append(cards[weapon])
            if len(show) == 0:
                continue
            else:
                time.sleep(.05)
                self.users[person].send('revealCard:'+pickle.dumps([x.identifier for x in show])+':'+name)
                break

    def handleAccusation(self, name, pickled):
        accusation = pickle.loads(str(pickled))
        suspect = str(accusation[0])
        weapon = str(accusation[1])
        room = str(accusation[2])
        time.sleep(.05)
        self.broadcastMessageToAll('%s accuses %s of committing the crime in the %s with the %s.' % (name,suspect,room,weapon))
        correct = True
        caseFile = [x.identifier for x in self.game.caseFile]
        for card in accusation:
            if card not in caseFile:
                correct = False
                break
        if correct:
            time.sleep(.05)
            self.users[name].send('winner')
            for n,conn in self.users.items():
                if n != name:
                    time.sleep(.05)
                    conn.send('gameOver:'+name)
        else:
            time.sleep(.05)
            self.broadcastMessageToUser(name, 'Your accusation was incorrect.')
            time.sleep(.05)
            for n,conn in self.users.items():
                if n != name:
                    time.sleep(.05)
                    conn.send('%s\'s accusation was incorrect' % name)
            self.game.turnOrder = [x for x in self.game.turnOrder if x.name != name]
            if isinstance(self.game.players[name].currentSpace, gameplay.hallway):
                self.game.players[name].currentSpace = self.game.players[name].currentSpace.connections[0]
                self.playerLocations[self.game.players[name].character] = self.game.players[name].currentSpace.identifier
                time.sleep(.05)
                for conn in self.users.values():
                    time.sleep(.05)
                    conn.send('updateGameboard:'+pickle.dumps(self.playerLocations))
            time.sleep(.05)
            self.users[name].send('falseAccusation')


    def revealCard(self, name, card, person):
        time.sleep(.05)
        self.users[name].send('You have shown %s the %s card.' % (person,card))
        time.sleep(.05)
        self.users[person].send('%s has shown you the %s card.' % (name,card))

def main():
    #s = server('192.168.100.14', 4004)
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
                        elif splt2[0] == 'revealCard':
                            s.revealCard(name,splt2[1],splt2[2])
                        elif splt2[0] == 'makingAccusation':
                            s.handleAccusation(name,splt2[1])
                    elif splt[0] == 'message':
                        s.broadcastMessageToAll('%s> %s' % (name, splt[1]))
                else:
                    if not message:
                        # Empty string is given on disconnect
                        del s.users[name]
                        if s.game:
                            if name in s.game.players:
                                del s.game.players[name]
                        s.broadcastMessageToAll('--- %s leaves ---' % name)
            time.sleep(.05)
        except (SystemExit, KeyboardInterrupt):
            break

if __name__ == '__main__':
    main()
