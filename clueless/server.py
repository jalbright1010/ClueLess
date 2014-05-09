#!/usr/bin/python

import socket
import thread
import time
import sys
import cPickle as pickle
import uuid
import itertools
import gameplay 
import consts

class server():
    """
    Clue-Less server class that handles communication between all players
    and Clue-Less game.
    """
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
        """
        Accept a socket connection via server socket accept() function.
        """
        return self.sock.accept()

    def acceptConnection(self, conn):
        """
        Launch thread to handle getting username from user client and add
        this user client to class user dictionary.
        """
        def threaded():
            while True:
                time.sleep(.05)
                conn.send(self.encrypt('function::username'))
                try:
                    r = conn.recv(1024).strip()
                    name = self.decrypt(r)
                except socket.error:
                    print 'Socket connection error'
                    break
                if name in self.users:
                    time.sleep(.05)
                    conn.send(self.encrypt('Username already in use.\n'))
                elif name:
                    conn.setblocking(False)
                    self.users[name] = conn
                    self.broadcastMessageToAllExcept(0, name, '+++ %s arrived +++' % name)
                    self.broadcastMessageToUser(0, name, 'Welcome, %s!' % name)
                    self.broadcastMessageToUser(1, name, 'usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                    break
        self.acceptThread = thread.start_new_thread(threaded, ())

    def addReadyPlayer(self, name):
        """
        Add player to list of player's that are ready to start.
        Keyword Arguments:
        name -- string name of player who is ready.
        """
        self.playersReady.append(name)
        self.broadcastMessageToAll(0, '%s is ready to start!' % name)

    def broadcastMessageToAll(self, type, message):
        """
        Send a message to all users.
        Keyword Arguments:
        type -- defines type of message to be sent as integer.
                0 = game log messsage
                1 = game function message
        message -- message to send to user as string.
        """
        #print message
        for conn in self.users.values():
            try:
                time.sleep(.05)
                if not type:
                    conn.send(self.encrypt('message::'+ message))
                elif type:
                    conn.send(self.encrypt('function::'+ message))
            except:
                pass

    def broadcastMessageToAllExcept(self, type, user, message):
        """
        Send a message to all users except specified user.
        Keyword Arguments:
        type -- defines type of message to be sent as integer.
                0 = game log messsage
                1 = game function message
        user -- name of user who will not receive message as string.
        message -- message to send to user as string.
        """
        #print message
        for name, conn in self.users.items():
            if name != user:
                try:
                    time.sleep(.05)
                    if not type:
                        conn.send(self.encrypt('message::'+ message))
                    elif type:
                        conn.send(self.encrypt('function::'+ message))
                except:
                    pass

    def broadcastMessageToUser(self, type, name, message):
        """
        Send a message to specified user.
        Keyword Arguments:
        type -- defines type of message to be sent as integer.
                0 = game log messsage
                1 = game function message
        name -- name of user to send message to as string.
        message -- message to send to user as string.
        """
        #print message
        try:
            time.sleep(.05)
            if not type:
                self.users[name].send(self.encrypt('message::'+ message))
            elif type:
                self.users[name].send(self.encrypt('function::'+ message))
        except:
            pass

    def createNewGame(self):
        """
        Create a new instance of the Clue-Less game class.
        """
        self.game = gameplay.game()
        print 'Game created with id %s' % self.game.id

    def decrypt(self, message):
        """
        Decrypt message.
        Keyword Arguments:
        message -- string message to be decrypted.
        """
        return ''.join([chr(ord(x) - 11) for x in message])

    def encrypt(self, message):
        """
        Encrypt message.
        Keyword Arguments:
        message -- string message to be encrypted.
        """
        return ''.join([chr(ord(x) + 11) for x in message])
    
    def endTurn(self, name):
        """
        End player's turn.
        Keyword Arguments:
        name -- string name of player who ended their turn.
        """
        self.broadcastMessageToAll(0, '%s has ended his/her turn...' % name)
        self.game.endTurn(name)
        self.sendTurnMessage()
        
    def handleAccusation(self, name, pickled):
        """
        Handle player's accusation and compare it against the game case file.
        Keyword Arguments:
        name -- string name of player who made accusation.
        pickled -- pickled list of card identifiers.
        """
        # Get list of cards in accusation
        accusation = pickle.loads(str(pickled))
        suspect = str(accusation[0])
        weapon = str(accusation[1])
        room = str(accusation[2])
        # Notify all players of accusation that was made
        self.broadcastMessageToAll(0, '%s accuses %s of committing the crime in the %s with the %s.' 
                                   % (name,suspect,room,weapon))
        caseFile = [x.identifier for x in self.game.caseFile]
        # Compare accusation cards against case file
        correct = True
        for card in accusation:
            if card not in caseFile:
                correct = False
                break
        # Notify winner and remaining players that game is over
        if correct:
            self.broadcastMessageToUser(1, name, 'winner')
            self.broadcastMessageToAllExcept(1, name, 'gameOver:'+name)
        # Notify all players that accusation was incorrect
        else:
            self.broadcastMessageToUser(0, name, 'Your accusation was incorrect.')
            self.broadcastMessageToAllExcept(0, name, '%s\'s accusation was incorrect' % name)
            # Remove player from turn order because they can no longer move
            self.game.turnOrder = [x for x in self.game.turnOrder if x.name != name]
            if isinstance(self.game.players[name].currentSpace, gameplay.hallway):
                oldSpace = self.game.players[name].currentSpace
                # Move player to adjacent room
                self.game.players[name].currentSpace = self.game.players[name].currentSpace.connections[0]
                self.playerLocations[self.game.players[name].character] = \
                    self.game.players[name].currentSpace.identifier
                # Mark hallway unoccupied
                oldSpace.occupied = False
                self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
            self.broadcastMessageToUser(1, name, 'falseAccusation')
            self.game.currentPlayer = self.game.turnOrder[0]
            self.sendTurnMessage()
     
    def handleMove(self, name, space):
        """
        Move player to specified space.
        Keyword Arguments:
        name -- string name of user to be moved.
        space -- string identifier of game board space.
        """
        newSpace = self.game.movePlayer(name, space)
        if isinstance(newSpace, gameplay.hallway):
            self.broadcastMessageToAllExcept(0, name, '%s has moved to the %s hallway.' 
                                             % (name, newSpace.identifier))
        elif isinstance(newSpace, gameplay.room):
            # Ask user to make suggestion
            self.broadcastMessageToUser(1, name, 'suggestion')
            self.broadcastMessageToAllExcept(0, name, '%s has moved to the %s.'
                                             % (name, newSpace.identifier))
        # Update local player locations dictionary
        self.playerLocations[self.game.players[name].character] = newSpace.identifier
        self.broadcastMessageToAllExcept(1, name, 'updateGameboard:'+pickle.dumps(self.playerLocations))
           
    def handleSuggestion(self, name, pickled):
        """
        Handle player's suggestion and try to disprove suggestion. If another
        player can disprove they are sent a notification to reveal a card.
        Keyword Arguments:
        name -- string name of player who made suggestion.
        pickled -- pickled list of card identifiers.
        """
        # Get list of cards in suggestion
        suggestion = pickle.loads(str(pickled))
        suspect = str(suggestion[0])
        weapon = str(suggestion[1])
        room = self.game.players[name].currentSpace.identifier
        # Notify all players of the suggestion that was made
        self.broadcastMessageToAll(0, '%s suggests that the crime was committed in the %s by %s with the %s.' 
                                   % (name,room,suspect,weapon))
        for player in self.game.players.values():
            # Check if alleged suspect is part of this game
            if player.character == suspect:
                # Move player to suggested room
                self.game.movePlayer(player.name, room)
        # Update local player locations dictionary
        self.playerLocations[suspect] = room
        self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
        # Get name of player who can disprove suggestion
        disprover = self.game.disproveSuggestion(suspect, weapon, room)
        # Check if anyone could disprove the suggestion
        if disprover:
            disproveCards = self.game.getDisproveList()
            self.broadcastMessageToUser(1, disprover, 
                                        'revealCard:'+pickle.dumps([x.identifier for x in disproveCards])+':'+name)
        else:
            self.broadcastMessageToUser(1, name, 'shown:No one could disprove your suggestion!')
            self.broadcastMessageToAllExcept(0, name, 'No one could disprove %s\'s suggestion' % name)
        
    def joinGame(self, name, char):
        """
        Add user to the game.
        Keyword Arguments:
        name -- string name of user to add to game.
        char -- string character identifier user has chosen.
        """
        if self.game:
            # Check if game has reached limit of players
            if len(self.game.players) < 6:
                # Check if character is already taken
                if char in [x.character for x in self.game.players.values()]:
                    # Ask user to select another character
                    self.broadcastMessageToUser(1, name, 'usedChars:'+pickle.dumps([x.character for x in self.game.players.values()]))
                else:
                    self.game.addPlayer(name, char)
                    self.broadcastMessageToAllExcept(0, name, '%s has joined the game as %s.' % (name, char))
                    self.playerLocations[char] = self.game.players[name].currentSpace.identifier
                    self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
            else:
                self.broadcastMessageToUser(0, name, 'Game already has 6 players, cannot join.')
                self.acceptingConnections = False
     
    def removePlayer(self, name):
        """
        Remove player from the Clue-Less game.
        Keyword Arguments:
        name -- string name of player who is being removed.
        """
        del self.users[name]
        if self.game:
            if name in self.game.players:
                if not self.game.started:
                    del self.playerLocations[self.game.players[name].character]
                self.game.removePlayer(name)
        self.broadcastMessageToAll(0, '--- %s leaves ---' % name) 
        self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
            
    def revealCard(self, name, card, person):
        """
        Reveal card to player who made a suggestion.
        Keyword Arguments:
        name -- name of player who is revealing card as string.
        card -- identifier of card being revealed as string.
        person -- name of player who is being shown card as string.
        """
        self.broadcastMessageToUser(0, name, 'You have shown %s the %s card.' % (person,card))
        self.broadcastMessageToUser(0, person, '%s has shown you the %s card.' % (name, card))
        self.broadcastMessageToUser(1, person, 'shown:%s has shown you the %s card.' % (name,card))
     
    def sendTurnMessage(self):
        """
        Notify player that it is their turn based on turn order.
        """
        moves = self.game.getMoves()
        # Send possible moves to player
        self.broadcastMessageToUser(1, self.game.currentPlayer.name, 'yourTurn:'+pickle.dumps([x.identifier for x in moves]))
        self.broadcastMessageToAllExcept(0, self.game.currentPlayer.name, 'Awaiting %s to make his/her move...' % self.game.currentPlayer.name)
           
    def startGame(self, name):
        """
        Start the game.
        Keyword Arguments:
        name -- name of user who started the game as string.
        """
        if self.game:
            if not self.game.started:
                # Verify that all players are ready
                if len(self.playersReady) == len(self.users):
                    self.game.start()
                    self.broadcastMessageToAll(0, '%s has started the game! Good Luck!' % name)
                    # No longer accept new connections to server
                    self.acceptingConnections = False
                    # Set initial locations for characters not in use by a client
                    for char in consts.SUSPECTS:
                        if char not in self.playerLocations:
                            self.playerLocations[char] = char+'Home'
                    self.broadcastMessageToAll(1, 'updateGameboard:'+pickle.dumps(self.playerLocations))
                    # Send cards to each client
                    for name in self.users.keys():
                        self.broadcastMessageToUser(1, name, 'cards:'+pickle.dumps([x.identifier for x in self.game.players[name].cards.values()]))
                    # Notify the first user of their turn
                    self.sendTurnMessage()
                else:
                    # Tell user who is not ready to play
                    self.broadcastMessageToUser(0, name, 'Not all players are ready to start....')
                    for n in self.users.keys():
                        if n not in self.playersReady:
                            self.broadcastMessageToUser(0, name, '%s is not ready to start' % n)
