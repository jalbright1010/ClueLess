#!/usr/bin/python

from PyQt4 import QtGui, QtCore
import uuid
import random

PEOPLE = ['Miss Scarlet', 'Colonel Mustard', 'Professor Plum',
           'Mr. Green', 'Mrs. White', 'Mrs. Peacock']
ROOMS = ['Ballroom', 'Billiard Room', 'Conservatory', 'Dining Room',
         'Hall', 'Kitchen', 'Library', 'Lounge', 'Study']
WEAPONS = ['Candlestick', 'Knife', 'Lead Pipe', 'Revolver',
           'Rope', 'Wrench']
HALLWAYS = ['StudyHall', 'HallLounge', 'StudyLibrary', 
            'HallBilliardRoom', 'LoungeDiningRoom', 
            'LibraryBilliardRoom', 'BilliardRoomDiningRoom', 
            'LibraryConservatory', 'BilliardRoomBallroom', 
            'DiningRoomKitchen', 'ConservatoryBallroom',
            'BallroomKitchen']

class game():
    id = ''
    players = []
    deck = None
    caseFile = []
    turnOrder = []
    board = None

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.deck = carddeck()
        self.defaultOrder = ['Miss Scarlet', 'Colonel Mustard',
                             'Mrs. White', 'Mr. Green',
                             'Mrs. Peacock', 'Professor Plum']
    
        self.board = self.createGameBoard()

    def addPlayer(self, name, char):
        space = [x for x in self.board if x.identifier == (char+'Home')][0]
        p = player(name, char, space)
        self.players.append(p)
        
    def createGameBoard(self):
        board = []
        rooms = []
        hallways = []
        homespaces = []
        # Create all the rooms
        for r in ROOMS:
            rooms.append(room(r))
        # Create all the hallways
        for h in HALLWAYS:
            hallways.append(hallway(h))
        # Create all the homespaces
        for p in PEOPLE:
            homespaces.append(homespace(p))
        
        board = rooms + hallways + homespaces
        
        # Make all the connections
        for item in board:
            if item.identifier == 'Ballroom':
                item.connections = [x for x in board if 
                                    'ConservatoryBallroom' == x.identifier or 
                                    'BilliardRoomBallroom' == x.identifier or
                                    'BallroomKitchen' == x.identifier]
            elif item.identifier == 'Billiard Room':
                item.connections = [x for x in board if
                                    'HallBilliardRoom' == x.identifier or
                                    'BilliardRoomDiningRoom' == x.identifier or
                                    'BilliardRoomBallroom' == x.identifier or
                                    'LibraryBilliardRoom' == x.identifier]
            elif item.identifier == 'Conservatory':
                item.connections = [x for x in board if
                                    'LibraryConservatory' == x.identifier or
                                    'Lounge' == x.identifier or
                                    'ConservatoryBallroom' == x.identifier]
            elif item.identifier == 'Dining Room':
                item.connections = [x for x in board if
                                    'LoungeDiningRoom' == x.identifier or
                                    'BilliardRoomDiningRoom' == x.identifier or
                                    'DiningRoomKitchen' == x.identifier]
            elif item.identifier == 'Hall':
                item.connections = [x for x in board if
                                    'StudyHall' == x.identifier or
                                    'HallBilliardRoom' == x.identifier or
                                    'HallLounge' == x.identifier]
            elif item.identifier == 'Kitchen':
                item.connections = [x for x in board if
                                    'BallroomKitchen' == x.identifier or
                                    'Study' == x.identifier or
                                    'DiningRoomKitchen' == x.identifier]
            elif item.identifier == 'Library':
                item.connections = [x for x in board if
                                    'StudyLibrary' == x.identifier or
                                    'LibraryBilliardRoom' == x.identifier or
                                    'LibraryConservatory' == x.identifier]
            elif item.identifier == 'Lounge':
                item.connections = [x for x in board if
                                    'HallLounge' == x.identifier or
                                    'Conservatory' == x.identifier or
                                    'LoungeDiningRoom' == x.identifier]
            elif item.identifier == 'Study':
                item.connections = [x for x in board if
                                    'StudyHall' == x.identifier or
                                    'Kitchen' == x.identifier or
                                    'StudyLibrary' == x.identifier]
            elif item.identifier == 'StudyHall':
                item.connections = [x for x in board if
                                    'Study' == x.identifier or 
                                    'Hall' == x.identifier]
            elif item.identifier == 'HallBilliardRoom':
                item.connections = [x for x in board if
                                    'Hall' == x.identifier or 
                                    'Billiard Room' == x.identifier]
            elif item.identifier == 'HallLounge':
                item.connections = [x for x in board if
                                    'Hall' == x.identifier or
                                    'Lounge' == x.identifier]
            elif item.identifier == 'StudyLibrary':
                item.connections = [x for x in board if
                                    'Study' == x.identifier or
                                    'Library' == x.identifier]
            elif item.identifier == 'LoungeDiningRoom':
                item.connections = [x for x in board if
                                    'Lounge' == x.identifier or
                                    'Dining Room' == x.identifier]
            elif item.identifier  == 'LibraryBilliardRoom':
                item.connections = [x for x in board if
                                    'Library' == x.identifier or
                                    'Billiard Room' == x.identifier]
            elif item.identifier == 'BilliardRoomDiningRoom':
                item.connections = [x for x in board if
                                    'Billiard Room' == x.identifier or
                                    'Dining Room' == x.identifier]
            elif item.identifier == 'LibraryConservatory':
                item.connections = [x for x in board if
                                    'Library' == x.identifier or
                                    'Conservatory' == x.identifier]
            elif item.identifier == 'BilliardRoomBallroom':
                item.connections = [x for x in board if
                                    'Billiard Room' == x.identifier or
                                    'Ballroom' == x.identifier]
            elif item.identifier == 'DiningRoomKitchen':
                item.connections = [x for x in board if
                                    'Dining Room' == x.identifier or
                                    'Kitchen' == x.identifier]
            elif item.identifier == 'ConservatoryBallroom':
                item.connections = [x for x in board if
                                    'Conservatory' == x.identifier or
                                    'Ballroom' == x.identifier]
            elif item.identifier == 'BallroomKitchen':
                item.connections = [x for x in board if
                                    'Ballroom' == x.identifier or
                                    'Kitchen' == x.identifier]
            elif item.identifier == 'Miss ScarletHome':
                item.connections = [x for x in board if
                                    'HallLounge' == x.identifier]
            elif item.identifier == 'Colonel MustardHome':
                item.connections = [x for x in board if
                                    'LoungeDiningRoom' == x.identifier]
            elif item.identifier == 'Mrs. WhiteHome':
                item.connections = [x for x in board if
                                    'BallroomKitchen' == x.identifier]
            elif item.identifier == 'Mr. GreenHome':
                item.connections = [x for x in board if
                                    'ConservatoryBallroom' == x.identifier]
            elif item.identifier == 'Mrs. PeacockHome':
                item.connections = [x for x in board if
                                    'LibraryConservatory' == x.identifier]
            elif item.identifier == 'Professor PlumHome':
                item.connections = [x for x in board if
                                    'StudyLibrary' == x.identifier]

        return board
        
    def start(self):
        # Determine the winning scenario for the game
        self.caseFile = self.deck.chooseCaseFile()

        self.deck.shuffleCards()

        # Deal the rest of the cards
        while len(self.deck.cards) > 0:
            for player in self.players:
                if len(self.deck.cards) != 0:
                    player.addCard(self.deck.cards.pop())
        
        # Determine the order based on which suspects
        # have been used by players in the game
        for char in self.defaultOrder:
            for player in self.players:
                if player.character == char:
                    self.turnOrder.append(player)

        self.currentPlayer = self.turnOrder[0]

    def playerMove(self, name, char, space):
        # Check that is that player's turn
        if name == self.currentPlayer.name:
            pass
        else:
            self.throwException('It is not %s\'s turn' % name)
        
        # Check that moving to that space is a valid move
        if isinstance(space, hallway):
            if not space.occupied:
                if space.identifier in self.currentPlayer.currentSpace.connections:
            #Move the player to that space
                    pass
                else:
                    self.throwException('Those space are not connected')
            else:
                print 'Space is occupied'
            
    def throwException(self, e):
        raise Exception(e)

class carddeck():
    cards = []

    def __init__(self):
        self.suspects = [card(x,'Suspect') for x in PEOPLE]
        self.rooms = [card(x,'Room') for x in ROOMS]
        self.weapons = [card(x,'Weapon') for x in WEAPONS]
        self.cards = self.suspects + self.rooms + self.weapons

    def shuffleCards(self):
        random.shuffle(self.cards)

    def chooseCaseFile(self):
        caseFile = []
        
        # Randomly choose the winning cards
        caseFile.append(self.suspects[random.randint(0,len(PEOPLE)-1)])
        caseFile.append(self.rooms[random.randint(0, len(ROOMS)-1)])
        caseFile.append(self.weapons[random.randint(0, len(WEAPONS)-1)])

        # Remove the case file cards from the deck
        self.cards = [x for x in self.cards if x not in caseFile]

        return caseFile

class card():
    identifier = ''
    cardType = ''

    def __init__(self, cardId, cardType):
        self.identifier = cardId
        self.cardType = cardType

class room():
    identifier = ''
    connections = []

    def __init__(self, roomId):
        self.identifier = roomId
        #self.connections.extend(connections)

class hallway():
    identifier = ''
    connections = []
    
    def __init__(self, hallId):
        self.identifier = hallId
        #self.connections.extend(connections)
        self.occupied = False

class player():
    name = ''
    character = ''
    cards = []
    currentSpace = None

    def __init__(self, name, char, space):
        self.name = name
        self.character = char
        self.currentSpace = space

    def addCard(self, card):
        self.cards.append(card)

class homespace():
    identifier = ''
    connections = []

    def __init__(self, char):
        self.identifier = char+'Home'
        #self.connections = connections

class notebook():
    pass

class board(QtGui.QWidget):
    
    def __init__(self, width, height):
        super(board, self).__init__()
        self.setFixedSize(width, height)
        self.update()
        self.players = []

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        self.draw(qp)

    def draw(self, qp):
        qp.begin(self)
        
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')
        qp.setPen(color)
        
        width = self.width()
        height = self.height()
        rectSize = width/8
        x1Pos = (width/8) - (rectSize/2)
        x2Pos = (width/2) - (rectSize/2)
        x3Pos = (7*width/8) - (rectSize/2)
        y1Pos = (height/8) - (rectSize/2)
        y2Pos = (height/2) - (rectSize/2)
        y3Pos = (7*height/8) - (rectSize/2)
        
        hallWidth = rectSize/3
        hallLength = (width/4)
        hallHeight = y2Pos - y1Pos - rectSize
        hallx1Pos = x1Pos + rectSize
        hallx2Pos = x2Pos + rectSize
        hallx3Pos = x1Pos + (rectSize/2) - (hallWidth/2)
        hallx4Pos = x2Pos + (rectSize/2) - (hallWidth/2)
        hallx5Pos = x3Pos + (rectSize/2) - (hallWidth/2)
        hally1Pos = y1Pos + (rectSize/2) - (hallWidth/2)
        hally2Pos = y2Pos + (rectSize/2) - (hallWidth/2)
        hally3Pos = y3Pos + (rectSize/2) - (hallWidth/2)
        hally4Pos = y1Pos + rectSize
        hally5Pos = y2Pos + rectSize
        
        # Draw Rooms
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(x1Pos, y1Pos, rectSize, rectSize)
        
        qp.setBrush(QtGui.QColor(255,255,255))
        qp.drawText(x1Pos+18,y1Pos+14,'Study')
            
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(x2Pos, y1Pos, rectSize, rectSize)
        
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(x3Pos, y1Pos, rectSize ,rectSize)
        
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(x1Pos, y2Pos, rectSize ,rectSize)
        
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(x2Pos, y2Pos, rectSize ,rectSize)
        
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(x3Pos, y2Pos, rectSize ,rectSize)
        
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(x1Pos, y3Pos, rectSize ,rectSize)
        
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(x2Pos, y3Pos, rectSize ,rectSize)
        
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(x3Pos, y3Pos, rectSize ,rectSize)
        
        # Draw Hallways
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx1Pos, hally1Pos, hallLength, hallWidth)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx2Pos, hally1Pos, hallLength, hallWidth)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx1Pos, hally2Pos, hallLength, hallWidth)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx2Pos, hally2Pos, hallLength, hallWidth)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx1Pos, hally3Pos, hallLength, hallWidth)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx2Pos, hally3Pos, hallLength, hallWidth)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx3Pos, hally4Pos, hallWidth, hallHeight)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx4Pos, hally4Pos, hallWidth, hallHeight)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx5Pos, hally4Pos, hallWidth, hallHeight)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx3Pos, hally5Pos, hallWidth, hallHeight)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx4Pos, hally5Pos, hallWidth, hallHeight)
        
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(hallx5Pos, hally5Pos, hallWidth, hallHeight)
        
        playerSize = rectSize/6
            
        # Draw a player token
        for player in self.players:
            if player == 'Colonel Mustard':
                center = QtCore.QPoint(x3Pos+rectSize+hallWidth+playerSize/2,hally4Pos+hallHeight/2)
                qp.setBrush(QtGui.QColor(204,204,0))
                qp.drawEllipse(center, playerSize, playerSize)
            elif player == 'Miss Scarlet':
                center = QtCore.QPoint(x2Pos+rectSize+hallLength/2,hally1Pos-hallWidth-playerSize/2)
                qp.setBrush(QtGui.QColor(240,0,0))
                qp.drawEllipse(center, playerSize, playerSize)
            elif player == 'Professor Plum':
                center = QtCore.QPoint(x1Pos-playerSize/2,hally4Pos+hallHeight/2)
                qp.setBrush(QtGui.QColor(153,51,102))
                qp.drawEllipse(center, playerSize, playerSize)
            elif player == 'Mrs. Peacock':
                center = QtCore.QPoint(x1Pos-playerSize/2,hally5Pos+hallHeight/2)
                qp.setBrush(QtGui.QColor(0,0,245))
                qp.drawEllipse(center, playerSize, playerSize)
            elif player == 'Mr. Green':
                center = QtCore.QPoint(hallx1Pos+hallLength/2,y3Pos+rectSize+playerSize/2)
                qp.setBrush(QtGui.QColor(51,153,0))
                qp.drawEllipse(center, playerSize, playerSize)
            elif player == 'Mrs. White':
                center = QtCore.QPoint(hallx2Pos+hallLength/2,y3Pos+rectSize+playerSize/2)
                qp.setBrush(QtGui.QColor(255,255,255))
                qp.drawEllipse(center, playerSize, playerSize)
                    
        qp.end()
