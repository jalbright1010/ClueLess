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
    game = None
    playersReady = []
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
        self.acceptingConnections = True

    def accept(self):
        return self.sock.accept()

    def acceptConnection(self, conn):
        def threaded():
            while True:
                time.sleep(.05)
                conn.send('function::username')
                try:
                    name = conn.recv(1024).strip()
                except socket.error:
                    print 'Socket connection error'
                    break
                if name in self.users:
                    time.sleep(.05)
                    conn.send('Username already in use.\n')
                elif name:
                    conn.setblocking(False)
                    self.users[name] = conn
                    self.broadcastMessageToAllExcept(0, name,'+++ %s arrived +++' % name)
                    self.broadcastMessageToUser(1, name, 'usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                    break
        self.acceptThread = thread.start_new_thread(threaded, ())

    def broadcastMessageToAll(self, type, message):
        # Send a message to all users
        #print message
        for conn in self.users.values():
            try:
                time.sleep(.05)
                if not type:
                    conn.send('message::'+message)
                elif type:
                    conn.send('function::'+message)
            except:
                pass

    def broadcastMessageToAllExcept(self, type, user, message):
        # Send a message to all users except @arg user
        #print message
        for name, conn in self.users.items():
            if name != user:
                try:
                    time.sleep(.05)
                    if not type:
                        conn.send('message::'+message)
                    elif type:
                        conn.send('function::'+message)
                except:
                    pass

    def broadcastMessageToUser(self, type, name, message):
        # Send a message to specific user @arg name
        #print message
        try:
            time.sleep(.05)
            if not type:
                self.users[name].send('message::'+message)
            elif type:
                self.users[name].send('function::'+message)
        except:
            pass

    def createNewGame(self):
        self.game = gameplay.game()
        #time.sleep(.05)
        #self.broadcastMessageToAll('Game created with id %s' % self.game.id)
        print 'Game created with id %s' % self.game.id
        
    def joinGame(self, name, char):
        if self.game:
            if len(self.game.players) < 6:
                if char in [x.character for x in self.game.players.values()]:
                    self.broadcastMessageToUser(1, name, 'usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                else:
                    self.game.addPlayer(name, char)
                    self.broadcastMessageToAllExcept(0, name, '%s has joined the game as %s.' % (name, char))
                    self.playerLocations[char] = self.game.players[name].currentSpace.identifier
                    self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
            else:
                self.broadcastMessageToUser(0, name, 'Game already has 6 players, cannot join.')
                self.acceptingConnections = False

    def startGame(self, name):
        if self.game:
            if len(self.playersReady) == len(self.users):
                self.game.start()
                self.broadcastMessageToAll(0, '%s has started the game! Good Luck!' % name)
                self.acceptingConnections = False
                for char in gameplay.PEOPLE:
                    if char not in self.playerLocations:
                        self.playerLocations[char] = char+'Home'
                self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
                for name in self.users.keys():
                    self.broadcastMessageToUser(1, name, 'cards:'+pickle.dumps([x.identifier for x in self.game.players[name].cards.values()]))
                self.sendTurnMessage()
            else:
                self.broadcastMessageToUser(0, name, 'Not all players are ready to start....')
                for n in self.users.keys():
                    if n not in self.playersReady:
                        self.broadcastMessageToUser(0, name, '%s is not ready to start' % n)
                        

    def movePlayer(self, name, space):
        player = self.game.players[name]
        oldSpace = player.currentSpace
        newSpace = self.game.board[space]
        if isinstance(newSpace, gameplay.hallway):
            newSpace.occupied = True
        if isinstance(newSpace, gameplay.room):
            self.broadcastMessageToUser(1, name, 'suggestion')
        player.currentSpace = newSpace
        self.playerLocations[player.character] = newSpace.identifier
        self.broadcastMessageToAllExcept(1, name, 'updateGameboard:'+pickle.dumps(self.playerLocations))
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
        self.broadcastMessageToUser(1, self.game.currentPlayer.name, 'yourTurn:'+pickle.dumps([x.identifier for x in conns]))
        self.broadcastMessageToAllExcept(0, self.game.currentPlayer.name, 'Awaiting %s to make his/her move...' % self.game.currentPlayer.name)
        

    def endTurn(self, name):
        self.broadcastMessageToAll(0, '%s has ended his/her turn...' % name)
        self.game.turnOrder.append(self.game.turnOrder.pop(0))
        self.game.currentPlayer = self.game.turnOrder[0]
        self.sendTurnMessage()

    def makeSuggestion(self, name, pickled):
        suggestion = pickle.loads(str(pickled))
        suspect = str(suggestion[0])
        weapon = str(suggestion[1])
        room = self.game.players[name].currentSpace.identifier
        time.sleep(.05)
        self.broadcastMessageToAll(0, '%s suggests that the crime was committed in the %s by %s with the %s.' % (name,room,suspect,weapon))
        # Check if alleged suspect is part of this game
        # If so, update that player's current space
        for player in self.game.players.values():
            if player.character == suspect:
                player.currentSpace = self.game.board[room]
        self.playerLocations[suspect] = room
        # Tell everyone to redraw their gameboards
        self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
        # Iterate through the disprove order
        # If they have none of the suggested cards, move to the next person
        # If they have one of the cards, send a signal to have them choose which card to reveal
        disproved = False
        for i in range(1,len(self.game.disproveOrder)):
            person = self.game.disproveOrder[i].name
            cards = self.game.disproveOrder[i].cards
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
                self.broadcastMessageToUser(1, person, 'revealCard:'+pickle.dumps([x.identifier for x in show])+':'+name)
                disproved = True
                break
        if not disproved:
            self.broadcastMessageToUser(1, name, 'shown:No one could disprove your suggestion!')

    def handleAccusation(self, name, pickled):
        accusation = pickle.loads(str(pickled))
        suspect = str(accusation[0])
        weapon = str(accusation[1])
        room = str(accusation[2])
        self.broadcastMessageToAll(0, '%s accuses %s of committing the crime in the %s with the %s.' % (name,suspect,room,weapon))
        caseFile = [x.identifier for x in self.game.caseFile]
        correct = True
        for card in accusation:
            if card not in caseFile:
                correct = False
                break
        if correct:
            self.broadcastMessageToUser(1, name, 'winner')
            self.broadcastMessageToAllExcept(1, name, 'gameOver:'+name)
        else:
            self.broadcastMessageToUser(0, name, 'Your accusation was incorrect.')
            self.broadcastMessageToAllExcept(0, name, '%s\'s accusation was incorrect' % name)
            self.game.turnOrder = [x for x in self.game.turnOrder if x.name != name]
            if isinstance(self.game.players[name].currentSpace, gameplay.hallway):
                self.game.players[name].currentSpace = self.game.players[name].currentSpace.connections[0]
                self.playerLocations[self.game.players[name].character] = self.game.players[name].currentSpace.identifier
                self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
            self.broadcastMessageToUser(1, name, 'falseAccusation')


    def revealCard(self, name, card, person):
        self.broadcastMessageToUser(0, name, 'You have shown %s the %s card.' % (person,card))
        self.broadcastMessageToUser(1, person, 'shown:%s has shown you the %s card.' % (name,card))
