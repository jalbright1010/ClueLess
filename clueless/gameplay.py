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
    players = {}
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
        space = self.board[char+'Home']
        p = player(name, char, space)
        self.players[name] = p
        
    def createGameBoard(self):
        board = {}
        rooms = {}
        hallways = {}
        homespaces = {}
        # Create all the rooms
        for r in ROOMS:
            rooms[r] = room(r)
        # Create all the hallways
        for h in HALLWAYS:
            hallways[h] = hallway(h)
        # Create all the homespaces
        for p in PEOPLE:
            homespaces[p+'Home'] = homespace(p+'Home')
        
        board.update(rooms)
        board.update(hallways)
        board.update(homespaces)
        
        # Make all the connections
        for item in board:
            if item == 'Ballroom':
                board[item].connections = [board['ConservatoryBallroom'], 
                                           board['BilliardRoomBallroom'],
                                           board['BallroomKitchen']]
            elif item == 'Billiard Room':
                board[item].connections = [board['HallBilliardRoom'],
                                           board['BilliardRoomDiningRoom'],
                                           board['BilliardRoomBallroom'],
                                           board['LibraryBilliardRoom']]
            elif item == 'Conservatory':
                board[item].connections = [board['LibraryConservatory'],
                                           board['Lounge'],
                                           board['ConservatoryBallroom']]
            elif item == 'Dining Room':
                board[item].connections = [board['LoungeDiningRoom'],
                                           board['BilliardRoomDiningRoom'],
                                           board['DiningRoomKitchen']]
            elif item == 'Hall':
                board[item].connections = [board['StudyHall'],
                                           board['HallBilliardRoom'],
                                           board['HallLounge']]
            elif item == 'Kitchen':
                board[item].connections = [board['BallroomKitchen'],
                                           board['Study'],
                                           board['DiningRoomKitchen']]
            elif item == 'Library':
                board[item].connections = [board['StudyLibrary'],
                                           board['LibraryBilliardRoom'],
                                           board['LibraryConservatory']]
            elif item == 'Lounge':
                board[item].connections = [board['HallLounge'],
                                           board['Conservatory'],
                                           board['LoungeDiningRoom']]
            elif item == 'Study':
                board[item].connections = [board['StudyHall'],
                                           board['Kitchen'],
                                           board['StudyLibrary']]
            elif item == 'StudyHall':
                board[item].connections = [board['Study'], 
                                           board['Hall']]
            elif item == 'HallBilliardRoom':
                board[item].connections = [board['Hall'],
                                           board['Billiard Room']]
            elif item == 'HallLounge':
                board[item].connections = [board['Hall'],
                                           board['Lounge']]
            elif item == 'StudyLibrary':
                board[item].connections = [board['Study'],
                                           board['Library']]
            elif item == 'LoungeDiningRoom':
                board[item].connections = [board['Lounge'],
                                           board['Dining Room']]
            elif item  == 'LibraryBilliardRoom':
                board[item].connections = [board['Library'],
                                           board['Billiard Room']]
            elif item == 'BilliardRoomDiningRoom':
                board[item].connections = [board['Billiard Room'],
                                           board['Dining Room']]
            elif item == 'LibraryConservatory':
                board[item].connections = [board['Library'],
                                           board['Conservatory']]
            elif item == 'BilliardRoomBallroom':
                board[item].connections = [board['Billiard Room'],
                                           board['Ballroom']]
            elif item == 'DiningRoomKitchen':
                board[item].connections = [board['Dining Room'],
                                           board['Kitchen']]
            elif item == 'ConservatoryBallroom':
                board[item].connections = [board['Conservatory'],
                                           board['Ballroom']]
            elif item == 'BallroomKitchen':
                board[item].connections = [board['Ballroom'],
                                           board['Kitchen']]
            elif item == 'Miss ScarletHome':
                board[item].connections = [board['HallLounge']]
            elif item == 'Colonel MustardHome':
                board[item].connections = [board['LoungeDiningRoom']]
            elif item == 'Mrs. WhiteHome':
                board[item].connections = [board['BallroomKitchen']]
            elif item == 'Mr. GreenHome':
                board[item].connections = [board['ConservatoryBallroom']]
            elif item == 'Mrs. PeacockHome':
                board[item].connections = [board['LibraryConservatory']]
            elif item == 'Professor PlumHome':
                board[item].connections = [board['StudyLibrary']]

        return board
        
    def start(self):
        # Determine the winning scenario for the game
        self.caseFile = self.deck.chooseCaseFile()

        self.deck.shuffleCards()

        # Deal the rest of the cards
        while len(self.deck.cards) > 0:
            for player in self.players:
                if len(self.deck.cards) != 0:
                    self.players[player].addCard(self.deck.cards.pop())
        
        # Determine the order based on which suspects
        # have been used by players in the game
        for char in self.defaultOrder:
            for player in self.players:
                if self.players[player].character == char:
                    self.turnOrder.append(self.players[player])

        self.currentPlayer = self.turnOrder[0]

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
    numOccupants = 0

    def __init__(self, roomId):
        self.identifier = roomId

class hallway():
    identifier = ''
    connections = []
    
    def __init__(self, hallId):
        self.identifier = hallId
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
        self.identifier = char

class board(QtGui.QWidget):
    
    def __init__(self, width, height):
        super(board, self).__init__()
        self.setFixedSize(width, height)
        self.update()
        self.players = {}
        
        width = self.width()
        height = self.height()
        
        self.rectSize = width/8
        self.playerSize = self.rectSize/6
        
        x1Pos = (width/8) - (self.rectSize/2)
        x2Pos = (width/2) - (self.rectSize/2)
        x3Pos = (7*width/8) - (self.rectSize/2)
        y1Pos = (height/8) - (self.rectSize/2)
        y2Pos = (height/2) - (self.rectSize/2)
        y3Pos = (7*height/8) - (self.rectSize/2)
        
        self.hallWidth = self.rectSize/3
        self.hallLength = (width/4)
        self.hallHeight = y2Pos - y1Pos - self.rectSize
        hallx1Pos = x1Pos + self.rectSize
        hallx2Pos = x2Pos + self.rectSize
        hallx3Pos = x1Pos + (self.rectSize/2) - (self.hallWidth/2)
        hallx4Pos = x2Pos + (self.rectSize/2) - (self.hallWidth/2)
        hallx5Pos = x3Pos + (self.rectSize/2) - (self.hallWidth/2)
        hally1Pos = y1Pos + self.hallWidth
        hally2Pos = y1Pos + self.rectSize
        hally3Pos = y2Pos + self.hallWidth
        hally4Pos = y2Pos + self.rectSize
        hally5Pos = y3Pos + self.hallWidth
        
        # Study coordinates
        self.studyXPos = x1Pos
        self.studyYPos = y1Pos
        self.studyTextXPos = self.studyXPos + self.playerSize/2
        self.studyTextYPos = self.studyXPos + self.playerSize/2
        self.studyPlayer1xPos = self.studyXPos + self.playerSize/2
        self.studyPlayer1yPos = self.studyYPos + self.rectSize/2
        self.studyPlayer2xPos = self.studyXPos + self.rectSize/2
        self.studyPlayer2yPos = self.studyYPos + self.rectSize/2
        self.studyPlayer3xPos = self.studyXPos + self.rectSize/2 + self.playerSize
        self.studyPlayer3yPos = self.studyYPos + self.rectSize/2
        self.studyPlayer4xPos = self.studyXPos + self.playerSize/2
        self.studyPlayer4yPos = self.studyYPos + self.rectSize/2 + self.playerSize
        self.studyPlayer5xPos = self.studyXPos + self.rectSize/2
        self.studyPlayer5yPos = self.studyYPos + self.rectSize/2 + self.playerSize
        self.studyPlayer6xPos = self.studyXPos + self.rectSize/2 + self.playerSize
        self.studyPlayer6yPos = self.studyYPos + self.rectSize/2 + self.playerSize
        # Hall Coordinates
        self.hallXPos = x2Pos
        self.hallYPos = y1Pos
        self.hallTextXPos = self.hallXPos + self.playerSize/2
        self.hallTextYPos = self.hallXPos + self.playerSize/2
        self.hallPlayer1xPos = self.hallXPos + self.playerSize/2
        self.hallPlayer1yPos = self.hallYPos + self.rectSize/2
        self.hallPlayer2xPos = self.hallXPos + self.rectSize/2
        self.hallPlayer2yPos = self.hallYPos + self.rectSize/2
        self.hallPlayer3xPos = self.hallXPos + self.rectSize/2 + self.playerSize
        self.hallPlayer3yPos = self.hallYPos + self.rectSize/2
        self.hallPlayer4xPos = self.hallXPos + self.playerSize/2
        self.hallPlayer4yPos = self.hallYPos + self.rectSize/2 + self.playerSize
        self.hallPlayer5xPos = self.hallXPos + self.rectSize/2
        self.hallPlayer5yPos = self.hallYPos + self.rectSize/2 + self.playerSize
        self.hallPlayer6xPos = self.hallXPos + self.rectSize/2 + self.playerSize
        self.hallPlayer6yPos = self.hallYPos + self.rectSize/2 + self.playerSize
        # Lounge Coordinates
        self.loungeXPos = x3Pos
        self.loungeYPos = y1Pos
        self.loungeTextXPos = self.loungeXPos + self.playerSize/2
        self.loungeTextYPos = self.loungeXPos + self.playerSize/2
        self.loungePlayer1xPos = self.loungeXPos + self.playerSize/2
        self.loungePlayer1yPos = self.loungeYPos + self.rectSize/2
        self.loungePlayer2xPos = self.loungeXPos + self.rectSize/2
        self.loungePlayer2yPos = self.loungeYPos + self.rectSize/2
        self.loungePlayer3xPos = self.loungeXPos + self.rectSize/2 + self.playerSize
        self.loungePlayer3yPos = self.loungeYPos + self.rectSize/2
        self.loungePlayer4xPos = self.loungeXPos + self.playerSize/2
        self.loungePlayer4yPos = self.loungeYPos + self.rectSize/2 + self.playerSize
        self.loungePlayer5xPos = self.loungeXPos + self.rectSize/2
        self.loungePlayer5yPos = self.loungeYPos + self.rectSize/2 + self.playerSize
        self.loungePlayer6xPos = self.loungeXPos + self.rectSize/2 + self.playerSize
        self.loungePlayer6yPos = self.loungeYPos + self.rectSize/2 + self.playerSize
        # Library Coordinates
        self.libraryXPos = x1Pos
        self.libraryYPos = y2Pos
        self.libraryTextXPos = self.libraryXPos + self.playerSize/2
        self.libraryTextYPos = self.libraryXPos + self.playerSize/2
        self.libraryPlayer1xPos = self.libraryXPos + self.playerSize/2
        self.libraryPlayer1yPos = self.libraryYPos + self.rectSize/2
        self.libraryPlayer2xPos = self.libraryXPos + self.rectSize/2
        self.libraryPlayer2yPos = self.libraryYPos + self.rectSize/2
        self.libraryPlayer3xPos = self.libraryXPos + self.rectSize/2 + self.playerSize
        self.libraryPlayer3yPos = self.libraryYPos + self.rectSize/2
        self.libraryPlayer4xPos = self.libraryXPos + self.playerSize/2
        self.libraryPlayer4yPos = self.libraryYPos + self.rectSize/2 + self.playerSize
        self.libraryPlayer5xPos = self.libraryXPos + self.rectSize/2
        self.libraryPlayer5yPos = self.libraryYPos + self.rectSize/2 + self.playerSize
        self.libraryPlayer6xPos = self.libraryXPos + self.rectSize/2 + self.playerSize
        self.libraryPlayer6yPos = self.libraryYPos + self.rectSize/2 + self.playerSize
        # Billiard Room Coordinates
        self.billiardXPos = x2Pos
        self.billiardYPos = y2Pos
        self.billiardTextXPos = self.billiardXPos + self.playerSize/2
        self.billiardTextYPos = self.billiardXPos + self.playerSize/2
        self.billiardPlayer1xPos = self.billiardXPos + self.playerSize/2
        self.billiardPlayer1yPos = self.billiardYPos + self.rectSize/2
        self.billiardPlayer2xPos = self.billiardXPos + self.rectSize/2
        self.billiardPlayer2yPos = self.billiardYPos + self.rectSize/2
        self.billiardPlayer3xPos = self.billiardXPos + self.rectSize/2 + self.playerSize
        self.billiardPlayer3yPos = self.billiardYPos + self.rectSize/2
        self.billiardPlayer4xPos = self.billiardXPos + self.playerSize/2
        self.billiardPlayer4yPos = self.billiardYPos + self.rectSize/2 + self.playerSize
        self.billiardPlayer5xPos = self.billiardXPos + self.rectSize/2
        self.billiardPlayer5yPos = self.billiardYPos + self.rectSize/2 + self.playerSize
        self.billiardPlayer6xPos = self.billiardXPos + self.rectSize/2 + self.playerSize
        self.billiardPlayer6yPos = self.billiardYPos + self.rectSize/2 + self.playerSize
        # Dining Room Coordinates
        self.diningXPos = x3Pos
        self.diningYPos = y2Pos
        self.diningTextXPos = self.diningXPos + self.playerSize/2
        self.diningTextYPos = self.diningXPos + self.playerSize/2
        self.diningPlayer1xPos = self.diningXPos + self.playerSize/2
        self.diningPlayer1yPos = self.diningYPos + self.rectSize/2
        self.diningPlayer2xPos = self.diningXPos + self.rectSize/2
        self.diningPlayer2yPos = self.diningYPos + self.rectSize/2
        self.diningPlayer3xPos = self.diningXPos + self.rectSize/2 + self.playerSize
        self.diningPlayer3yPos = self.diningYPos + self.rectSize/2
        self.diningPlayer4xPos = self.diningXPos + self.playerSize/2
        self.diningPlayer4yPos = self.diningYPos + self.rectSize/2 + self.playerSize
        self.diningPlayer5xPos = self.diningXPos + self.rectSize/2
        self.diningPlayer5yPos = self.diningYPos + self.rectSize/2 + self.playerSize
        self.diningPlayer6xPos = self.diningXPos + self.rectSize/2 + self.playerSize
        self.diningPlayer6yPos = self.diningYPos + self.rectSize/2 + self.playerSize
        # Conservatory Coordinates
        self.conservatoryXPos = x1Pos
        self.conservatoryYPos = y3Pos
        self.conservatoryTextXPos = self.conservatoryXPos + self.playerSize/2
        self.conservatoryTextYPos = self.conservatoryXPos + self.playerSize/2
        self.conservatoryPlayer1xPos = self.conservatoryXPos + self.playerSize/2
        self.conservatoryPlayer1yPos = self.conservatoryYPos + self.rectSize/2
        self.conservatoryPlayer2xPos = self.conservatoryXPos + self.rectSize/2
        self.conservatoryPlayer2yPos = self.conservatoryYPos + self.rectSize/2
        self.conservatoryPlayer3xPos = self.conservatoryXPos + self.rectSize/2 + self.playerSize
        self.conservatoryPlayer3yPos = self.conservatoryYPos + self.rectSize/2
        self.conservatoryPlayer4xPos = self.conservatoryXPos + self.playerSize/2
        self.conservatoryPlayer4yPos = self.conservatoryYPos + self.rectSize/2 + self.playerSize
        self.conservatoryPlayer5xPos = self.conservatoryXPos + self.rectSize/2
        self.conservatoryPlayer5yPos = self.conservatoryYPos + self.rectSize/2 + self.playerSize
        self.conservatoryPlayer6xPos = self.conservatoryXPos + self.rectSize/2 + self.playerSize
        self.conservatoryPlayer6yPos = self.conservatoryYPos + self.rectSize/2 + self.playerSize
        # Ballroom Coordinates
        self.ballroomXPos = x2Pos
        self.ballroomYPos = y3Pos
        self.ballroomTextXPos = self.ballroomXPos + self.playerSize/2
        self.ballroomTextYPos = self.ballroomXPos + self.playerSize/2
        self.ballroomPlayer1xPos = self.ballroomXPos + self.playerSize/2
        self.ballroomPlayer1yPos = self.ballroomYPos + self.rectSize/2
        self.ballroomPlayer2xPos = self.ballroomXPos + self.rectSize/2
        self.ballroomPlayer2yPos = self.ballroomYPos + self.rectSize/2
        self.ballroomPlayer3xPos = self.ballroomXPos + self.rectSize/2 + self.playerSize
        self.ballroomPlayer3yPos = self.ballroomYPos + self.rectSize/2
        self.ballroomPlayer4xPos = self.ballroomXPos + self.playerSize/2
        self.ballroomPlayer4yPos = self.ballroomYPos + self.rectSize/2 + self.playerSize
        self.ballroomPlayer5xPos = self.ballroomXPos + self.rectSize/2
        self.ballroomPlayer5yPos = self.ballroomYPos + self.rectSize/2 + self.playerSize
        self.ballroomPlayer6xPos = self.ballroomXPos + self.rectSize/2 + self.playerSize
        self.ballroomPlayer6yPos = self.ballroomYPos + self.rectSize/2 + self.playerSize
        # Kitchen Coordinates
        self.kitchenXPos = x3Pos
        self.kitchenYPos = y3Pos
        self.kitchenTextXPos = self.kitchenXPos + self.playerSize/2
        self.kitchenTextYPos = self.kitchenXPos + self.playerSize/2
        self.kitchenPlayer1xPos = self.libraryXPos + self.playerSize/2
        self.kitchenPlayer1yPos = self.libraryYPos + self.rectSize/2
        self.kitchenPlayer2xPos = self.libraryXPos + self.rectSize/2
        self.kitchenPlayer2yPos = self.libraryYPos + self.rectSize/2
        self.kitchenPlayer3xPos = self.libraryXPos + self.rectSize/2 + self.playerSize
        self.kitchenPlayer3yPos = self.libraryYPos + self.rectSize/2
        self.kitchenPlayer4xPos = self.libraryXPos + self.playerSize/2
        self.kitchenPlayer4yPos = self.libraryYPos + self.rectSize/2 + self.playerSize
        self.kitchenPlayer5xPos = self.libraryXPos + self.rectSize/2
        self.kitchenPlayer5yPos = self.libraryYPos + self.rectSize/2 + self.playerSize
        self.kitchenPlayer6xPos = self.libraryXPos + self.rectSize/2 + self.playerSize
        self.kitchenPlayer6yPos = self.libraryYPos + self.rectSize/2 + self.playerSize
        # StudyHall Coordinates
        self.shXPos = hallx1Pos
        self.shYPos = hally1Pos
        self.shPlayerxPos = self.shXPos + self.hallLength/2
        self.shPlayeryPos = self.shYPos + self.playerSize/2
        # HallLounge Coordinates
        self.hlXPos = hallx2Pos
        self.hlYPos = hally1Pos
        self.hlPlayerXPos = self.hlXPos + self.hallLength/2
        self.hlPlayerYPos = self.hlYPos + self.playerSize/2
        # StudyLibrary Coordinates
        self.slXPos = hallx3Pos
        self.slYPos = hally2Pos
        self.slPlayerXPos = self.slXPos + self.playerSize/2
        self.slPlayerYPos = self.slYPos + self.hallHeight/2
        # HallBilliardRoom Coordinates
        self.hbXPos = hallx4Pos
        self.hbYPos = hally2Pos
        self.hbPlayerXPos = self.hbXPos + self.playerSize/2
        self.hbPlayerYPos = self.hbYPos + self.hallHeight/2
        # LoungeDiningRoom Coordinates
        self.ldXPos = hallx5Pos
        self.ldYPos = hally2Pos
        self.ldPlayerXPos = self.ldXPos + self.playerSize/2
        self.ldPlayerYPos = self.ldYPos + self.hallHeight/2
        # LibraryBilliardRoom Coordinates
        self.lbXPos = hallx1Pos
        self.lbYPos = hally3Pos
        self.lbPlayerXPos = self.lbXPos + self.hallLength/2
        self.lbPlayerYPos = self.lbYPos + self.playerSize/2
        # BilliardRoomDiningRoom Coordinates
        self.bdXPos = hallx2Pos
        self.bdYPos = hally3Pos
        self.bdPlayerXPos = self.bdXPos + self.hallLength/2
        self.bdPlayerYPos = self.bdYPos + self.playerSize/2
        # LibraryConservatory Coordinates
        self.lcXPos = hallx3Pos
        self.lcYPos = hally4Pos
        self.lcPlayerXPos = self.lcXPos + self.playerSize/2
        self.lcPlayerYPos = self.lcYPos + self.hallHeight/2
        # BilliardRoomBallroom Coordinates
        self.bbXPos = hallx4Pos
        self.bbYPos = hally4Pos
        self.bbPlayerXPos = self.bbXPos + self.playerSize/2
        self.bbPlayerYPos = self.bbYPos + self.hallHeight/2
        # DiningRoomKitchen Coordinates
        self.dkXPos = hallx5Pos
        self.dkYPos = hally4Pos
        self.dkPlayerXPos = self.dkXPos + self.playerSize/2
        self.dkPlayerYPos = self.dkYPos + self.hallHeight/2
        # ConservatoryBallroom Coordinates
        self.cbXPos = hallx1Pos
        self.cbYPos = hally5Pos
        self.cbPlayerXPos = self.cbXPos + self.hallLength/2
        self.cbPlayerYPos = self.cbYPos + self.playerSize/2
        # BallroomKitchen Coordinates
        self.bkXPos = hallx2Pos
        self.bkYPos = hally5Pos
        self.bkPlayerXPos = self.bkXPos + self.hallLength/2
        self.bkPlayerYPos = self.bkYPos + self.playerSize/2
        # Colonel Mustard settings
        self.cmHomeXPos = x3Pos+self.rectSize+self.hallWidth+self.playerSize/2
        self.cmHomeYPos = hally4Pos+self.hallHeight/2
        self.cmColor = QtGui.QColor(204,204,0)
        # Miss Scarlet settings
        self.msHomeXPos = x2Pos+self.rectSize+self.hallLength/2
        self.msHomeYPos = hally1Pos-self.hallWidth-self.playerSize/2
        self.msColor = QtGui.QColor(240,0,0)
        # Professor Plum settings
        self.ppHomeXPos = x1Pos-self.playerSize/2
        self.ppHomeYPos = hally4Pos+self.hallHeight/2
        self.ppColor = QtGui.QColor(153,51,102)
        # Mrs.Peacock Settings
        self.mpHomeXPos = x1Pos-self.playerSize/2
        self.mpHomeYPos = hally5Pos+self.hallHeight/2
        self.mpColor = QtGui.QColor(0,0,245)
        # Mr. Green Settings
        self.mgHomeXPos = hallx1Pos+self.hallLength/2
        self.mgHomeYPos = y3Pos+self.rectSize+self.playerSize/2
        self.mgColor = QtGui.QColor(51,153,0)
        # Mrs. White settings
        self.mwHomeXPos = hallx2Pos+self.hallLength/2
        self.mwHomeYPos = y3Pos+self.rectSize+self.playerSize/2
        self.mwColor = QtGui.QColor(255,255,255)
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        self.draw(qp)

    def draw(self, qp):
        qp.begin(self)
        
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')
        qp.setPen(color)
        
        # Draw Hallways
        # StudyHall
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.shXPos, self.shYPos, self.hallLength, self.hallWidth)
        
        # HallLounge
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.hlXPos, self.hlYPos, self.hallLength, self.hallWidth)
        
        # StudyLibrary
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.slXPos, self.slYPos, self.hallWidth, self.hallHeight)
        
        # HallBilliardRoom
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.hbXPos, self.hbYPos, self.hallWidth, self.hallHeight)
        
        # LoungeDiningRoom
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.ldXPos, self.ldYPos, self.hallWidth, self.hallHeight)
        
        # LibraryBilliardRoom
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.lbXPos, self.lbYPos, self.hallLength, self.hallWidth)
        
        # BilliardRoomDiningRoom
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.bdXPos, self.bdYPos, self.hallLength, self.hallWidth)
        
        # LibraryConservatory
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.lcXPos, self.lcYPos, self.hallWidth, self.hallHeight)
        
        # BilliardRoomBallroom
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.bbXPos, self.bbYPos, self.hallWidth, self.hallHeight)
        
        # DiningRoomKitchen
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.dkXPos, self.dkYPos, self.hallWidth, self.hallHeight)
        
        # ConservatoryBallroom
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.cbXPos, self.cbYPos, self.hallLength, self.hallWidth)
        
        # BallroomKitchen
        qp.setBrush(QtGui.QColor(100, 100, 100))
        qp.drawRect(self.bkXPos, self.bkYPos, self.hallLength, self.hallWidth)
               
        # Draw Rooms
        # Study
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.studyXPos, self.studyYPos, self.rectSize, self.rectSize)
            
        # Hall
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.hallXPos, self.hallYPos, self.rectSize, self.rectSize)
        
        #Lounge
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.loungeXPos, self.loungeYPos, self.rectSize, self.rectSize)
        
        # Library
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.libraryXPos, self.libraryYPos, self.rectSize, self.rectSize)
        
        # Billiard Room
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.billiardXPos, self.billiardYPos, self.rectSize, self.rectSize)
        
        # Dining Room
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.diningXPos, self.diningYPos, self.rectSize, self.rectSize)
        
        # Conservatory
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.conservatoryXPos, self.conservatoryYPos, self.rectSize, self.rectSize)
        
        # Ballroom
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.ballroomXPos, self.ballroomYPos, self.rectSize, self.rectSize)
        
        # Kitchen
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.kitchenXPos, self.kitchenYPos, self.rectSize, self.rectSize)
        
           
        # Draw a player token
        for player,location in self.players.items():
            if player == 'Colonel Mustard':
                qp.setBrush(self.cmColor)
                if location == 'Colonel MustardHome':
                    center = QtCore.QPoint(self.cmHomeXPos,self.cmHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyHall':
                    center = QtCore.QPoint(self.shXPos,self.shYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallLounge':
                    center = QtCore.QPoint(self.hlXPos,self.hlYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyLibrary':
                    center = QtCore.QPoint(self.slXPos,self.slYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallBilliardRoom':
                    center = QtCore.QPoint(self.hbXPos,self.hbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LoungeDiningRoom':
                    center = QtCore.QPoint(self.ldXPos,self.ldYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryBilliardRoom':
                    center = QtCore.QPoint(self.lbXPos,self.lbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomDiningRoom':
                    center = QtCore.QPoint(self.bdXPos,self.bdYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryConservatory':
                    center = QtCore.QPoint(self.lcXPos,self.lcYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomBallroom':
                    center = QtCore.QPoint(self.bbXPos,self.bbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoomKitchen':
                    center = QtCore.QPoint(self.dkXPos,self.dkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'ConservatoryBallroom':
                    center = QtCore.QPoint(self.cbXPos,self.cbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BallroomKitchen':
                    center = QtCore.QPoint(self.bkXPos,self.bkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPlayer1xPos,self.studyPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPlayer1xPos,self.hallPlayer1yPos)
                    qp.drawEllipse(center, playerSize, playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePlayer1xPos,self.loungePlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPlayer1xPos,self.libraryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoom':
                    center = QtCore.QPoint(self.billiardPlayer1xPos,self.billiardPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoom':
                    center = QtCore.QPoint(self.diningPlayer1xPos,self.diningPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPlayer1xPos,self.conservatoryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPlayer1xPos,self.ballroomPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPlayer1xPos,self.kitchenPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Miss Scarlet':
                qp.setBrush(self.msColor)
                if location == 'Miss ScarletHome':
                    center = QtCore.QPoint(self.msHomeXPos,self.msHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyHall':
                    center = QtCore.QPoint(self.shXPos,self.shYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallLounge':
                    center = QtCore.QPoint(self.hlXPos,self.hlYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyLibrary':
                    center = QtCore.QPoint(self.slXPos,self.slYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallBilliardRoom':
                    center = QtCore.QPoint(self.hbXPos,self.hbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LoungeDiningRoom':
                    center = QtCore.QPoint(self.ldXPos,self.ldYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryBilliardRoom':
                    center = QtCore.QPoint(self.lbXPos,self.lbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomDiningRoom':
                    center = QtCore.QPoint(self.bdXPos,self.bdYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryConservatory':
                    center = QtCore.QPoint(self.lcXPos,self.lcYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomBallroom':
                    center = QtCore.QPoint(self.bbXPos,self.bbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoomKitchen':
                    center = QtCore.QPoint(self.dkXPos,self.dkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'ConservatoryBallroom':
                    center = QtCore.QPoint(self.cbXPos,self.cbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BallroomKitchen':
                    center = QtCore.QPoint(self.bkXPos,self.bkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPlayer1xPos,self.studyPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPlayer1xPos,self.hallPlayer1yPos)
                    qp.drawEllipse(center, playerSize, playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePlayer1xPos,self.loungePlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPlayer1xPos,self.libraryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoom':
                    center = QtCore.QPoint(self.billiardPlayer1xPos,self.billiardPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoom':
                    center = QtCore.QPoint(self.diningPlayer1xPos,self.diningPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPlayer1xPos,self.conservatoryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPlayer1xPos,self.ballroomPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPlayer1xPos,self.kitchenPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Professor Plum':
                qp.setBrush(self.ppColor)
                if location == 'Professor PlumHome':
                    center = QtCore.QPoint(self.ppHomeXPos,self.msHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyHall':
                    center = QtCore.QPoint(self.shXPos,self.shYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallLounge':
                    center = QtCore.QPoint(self.hlXPos,self.hlYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyLibrary':
                    center = QtCore.QPoint(self.slXPos,self.slYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallBilliardRoom':
                    center = QtCore.QPoint(self.hbXPos,self.hbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LoungeDiningRoom':
                    center = QtCore.QPoint(self.ldXPos,self.ldYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryBilliardRoom':
                    center = QtCore.QPoint(self.lbXPos,self.lbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomDiningRoom':
                    center = QtCore.QPoint(self.bdXPos,self.bdYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryConservatory':
                    center = QtCore.QPoint(self.lcXPos,self.lcYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomBallroom':
                    center = QtCore.QPoint(self.bbXPos,self.bbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoomKitchen':
                    center = QtCore.QPoint(self.dkXPos,self.dkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'ConservatoryBallroom':
                    center = QtCore.QPoint(self.cbXPos,self.cbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BallroomKitchen':
                    center = QtCore.QPoint(self.bkXPos,self.bkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPlayer1xPos,self.studyPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPlayer1xPos,self.hallPlayer1yPos)
                    qp.drawEllipse(center, playerSize, playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePlayer1xPos,self.loungePlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPlayer1xPos,self.libraryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoom':
                    center = QtCore.QPoint(self.billiardPlayer1xPos,self.billiardPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoom':
                    center = QtCore.QPoint(self.diningPlayer1xPos,self.diningPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPlayer1xPos,self.conservatoryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPlayer1xPos,self.ballroomPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPlayer1xPos,self.kitchenPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Mrs. Peacock':
                qp.setBrush(self.mpColor)
                if location == 'Mrs. PeacockHome':
                    center = QtCore.QPoint(self.mpHomeXPos,self.mpHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyHall':
                    center = QtCore.QPoint(self.shXPos,self.shYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallLounge':
                    center = QtCore.QPoint(self.hlXPos,self.hlYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyLibrary':
                    center = QtCore.QPoint(self.slXPos,self.slYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallBilliardRoom':
                    center = QtCore.QPoint(self.hbXPos,self.hbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LoungeDiningRoom':
                    center = QtCore.QPoint(self.ldXPos,self.ldYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryBilliardRoom':
                    center = QtCore.QPoint(self.lbXPos,self.lbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomDiningRoom':
                    center = QtCore.QPoint(self.bdXPos,self.bdYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryConservatory':
                    center = QtCore.QPoint(self.lcXPos,self.lcYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomBallroom':
                    center = QtCore.QPoint(self.bbXPos,self.bbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoomKitchen':
                    center = QtCore.QPoint(self.dkXPos,self.dkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'ConservatoryBallroom':
                    center = QtCore.QPoint(self.cbXPos,self.cbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BallroomKitchen':
                    center = QtCore.QPoint(self.bkXPos,self.bkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPlayer1xPos,self.studyPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPlayer1xPos,self.hallPlayer1yPos)
                    qp.drawEllipse(center, playerSize, playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePlayer1xPos,self.loungePlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPlayer1xPos,self.libraryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoom':
                    center = QtCore.QPoint(self.billiardPlayer1xPos,self.billiardPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoom':
                    center = QtCore.QPoint(self.diningPlayer1xPos,self.diningPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPlayer1xPos,self.conservatoryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPlayer1xPos,self.ballroomPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPlayer1xPos,self.kitchenPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Mr. Green':
                qp.setBrush(self.mgColor)
                if location == 'Mr. GreenHome':
                    center = QtCore.QPoint(self.mgHomeXPos,self.mgHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyHall':
                    center = QtCore.QPoint(self.shXPos,self.shYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallLounge':
                    center = QtCore.QPoint(self.hlXPos,self.hlYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyLibrary':
                    center = QtCore.QPoint(self.slXPos,self.slYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallBilliardRoom':
                    center = QtCore.QPoint(self.hbXPos,self.hbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LoungeDiningRoom':
                    center = QtCore.QPoint(self.ldXPos,self.ldYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryBilliardRoom':
                    center = QtCore.QPoint(self.lbXPos,self.lbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomDiningRoom':
                    center = QtCore.QPoint(self.bdXPos,self.bdYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryConservatory':
                    center = QtCore.QPoint(self.lcXPos,self.lcYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomBallroom':
                    center = QtCore.QPoint(self.bbXPos,self.bbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoomKitchen':
                    center = QtCore.QPoint(self.dkXPos,self.dkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'ConservatoryBallroom':
                    center = QtCore.QPoint(self.cbXPos,self.cbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BallroomKitchen':
                    center = QtCore.QPoint(self.bkXPos,self.bkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPlayer1xPos,self.studyPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPlayer1xPos,self.hallPlayer1yPos)
                    qp.drawEllipse(center, playerSize, playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePlayer1xPos,self.loungePlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPlayer1xPos,self.libraryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoom':
                    center = QtCore.QPoint(self.billiardPlayer1xPos,self.billiardPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoom':
                    center = QtCore.QPoint(self.diningPlayer1xPos,self.diningPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPlayer1xPos,self.conservatoryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPlayer1xPos,self.ballroomPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPlayer1xPos,self.kitchenPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Mrs. White':
                qp.setBrush(self.mwColor)
                if location == 'Mrs. WhiteHome':
                    center = QtCore.QPoint(self.mwHomeXPos,self.mwHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyHall':
                    center = QtCore.QPoint(self.shXPos,self.shYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallLounge':
                    center = QtCore.QPoint(self.hlXPos,self.hlYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'StudyLibrary':
                    center = QtCore.QPoint(self.slXPos,self.slYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'HallBilliardRoom':
                    center = QtCore.QPoint(self.hbXPos,self.hbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LoungeDiningRoom':
                    center = QtCore.QPoint(self.ldXPos,self.ldYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryBilliardRoom':
                    center = QtCore.QPoint(self.lbXPos,self.lbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomDiningRoom':
                    center = QtCore.QPoint(self.bdXPos,self.bdYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'LibraryConservatory':
                    center = QtCore.QPoint(self.lcXPos,self.lcYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoomBallroom':
                    center = QtCore.QPoint(self.bbXPos,self.bbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoomKitchen':
                    center = QtCore.QPoint(self.dkXPos,self.dkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'ConservatoryBallroom':
                    center = QtCore.QPoint(self.cbXPos,self.cbYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BallroomKitchen':
                    center = QtCore.QPoint(self.bkXPos,self.bkYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPlayer1xPos,self.studyPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPlayer1xPos,self.hallPlayer1yPos)
                    qp.drawEllipse(center, playerSize, playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePlayer1xPos,self.loungePlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPlayer1xPos,self.libraryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'BilliardRoom':
                    center = QtCore.QPoint(self.billiardPlayer1xPos,self.billiardPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'DiningRoom':
                    center = QtCore.QPoint(self.diningPlayer1xPos,self.diningPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPlayer1xPos,self.conservatoryPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPlayer1xPos,self.ballroomPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPlayer1xPos,self.kitchenPlayer1yPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                        
        qp.end()
