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
HALLWAYS = ['Study-Hall', 'Hall-Lounge', 'Study-Library', 
            'Hall-Billiard Room', 'Lounge-Dining Room', 
            'Library-Billiard Room', 'Billiard Room-Dining Room', 
            'Library-Conservatory', 'Billiard Room-Ballroom', 
            'Dining Room-Kitchen', 'Conservatory-Ballroom',
            'Ballroom-Kitchen']

class game():
    id = ''
    players = {}
    deck = None
    caseFile = []
    turnOrder = []
    disproveOrder = []
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
                board[item].connections = [board['Conservatory-Ballroom'], 
                                           board['Billiard Room-Ballroom'],
                                           board['Ballroom-Kitchen']]
            elif item == 'Billiard Room':
                board[item].connections = [board['Hall-Billiard Room'],
                                           board['Billiard Room-Dining Room'],
                                           board['Billiard Room-Ballroom'],
                                           board['Library-Billiard Room']]
            elif item == 'Conservatory':
                board[item].connections = [board['Library-Conservatory'],
                                           board['Lounge'],
                                           board['Conservatory-Ballroom']]
            elif item == 'Dining Room':
                board[item].connections = [board['Lounge-Dining Room'],
                                           board['Billiard Room-Dining Room'],
                                           board['Dining Room-Kitchen']]
            elif item == 'Hall':
                board[item].connections = [board['Study-Hall'],
                                           board['Hall-Billiard Room'],
                                           board['Hall-Lounge']]
            elif item == 'Kitchen':
                board[item].connections = [board['Ballroom-Kitchen'],
                                           board['Study'],
                                           board['Dining Room-Kitchen']]
            elif item == 'Library':
                board[item].connections = [board['Study-Library'],
                                           board['Library-Billiard Room'],
                                           board['Library-Conservatory']]
            elif item == 'Lounge':
                board[item].connections = [board['Hall-Lounge'],
                                           board['Conservatory'],
                                           board['Lounge-Dining Room']]
            elif item == 'Study':
                board[item].connections = [board['Study-Hall'],
                                           board['Kitchen'],
                                           board['Study-Library']]
            elif item == 'Study-Hall':
                board[item].connections = [board['Study'], 
                                           board['Hall']]
            elif item == 'Hall-Billiard Room':
                board[item].connections = [board['Hall'],
                                           board['Billiard Room']]
            elif item == 'Hall-Lounge':
                board[item].connections = [board['Hall'],
                                           board['Lounge']]
            elif item == 'Study-Library':
                board[item].connections = [board['Study'],
                                           board['Library']]
            elif item == 'Lounge-Dining Room':
                board[item].connections = [board['Lounge'],
                                           board['Dining Room']]
            elif item  == 'Library-Billiard Room':
                board[item].connections = [board['Library'],
                                           board['Billiard Room']]
            elif item == 'Billiard Room-Dining Room':
                board[item].connections = [board['Billiard Room'],
                                           board['Dining Room']]
            elif item == 'Library-Conservatory':
                board[item].connections = [board['Library'],
                                           board['Conservatory']]
            elif item == 'Billiard Room-Ballroom':
                board[item].connections = [board['Billiard Room'],
                                           board['Ballroom']]
            elif item == 'Dining Room-Kitchen':
                board[item].connections = [board['Dining Room'],
                                           board['Kitchen']]
            elif item == 'Conservatory-Ballroom':
                board[item].connections = [board['Conservatory'],
                                           board['Ballroom']]
            elif item == 'Ballroom-Kitchen':
                board[item].connections = [board['Ballroom'],
                                           board['Kitchen']]
            elif item == 'Miss ScarletHome':
                board[item].connections = [board['Hall-Lounge']]
            elif item == 'Colonel MustardHome':
                board[item].connections = [board['Lounge-Dining Room']]
            elif item == 'Mrs. WhiteHome':
                board[item].connections = [board['Ballroom-Kitchen']]
            elif item == 'Mr. GreenHome':
                board[item].connections = [board['Conservatory-Ballroom']]
            elif item == 'Mrs. PeacockHome':
                board[item].connections = [board['Library-Conservatory']]
            elif item == 'Professor PlumHome':
                board[item].connections = [board['Study-Library']]

        return board
        
    def start(self):
        # Determine the winning scenario for the game
        self.caseFile = self.deck.chooseCaseFile()

        self.deck.shuffleCards()

        # Deal the rest of the cards
        deal = self.deck.dealCards(len(self.players))
        for i in range(len(self.players.values())):
            self.players.values()[i].cards = deal.pop(i)
        
        # Determine the order based on which suspects
        # have been used by players in the game
        for char in self.defaultOrder:
            for player in self.players:
                if self.players[player].character == char:
                    self.turnOrder.append(self.players[player])

        self.currentPlayer = self.turnOrder[0]
        
        self.disproveOrder = self.turnOrder

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

    def dealCards(self, numPlayers):
        deal = {}
        for i in range(numPlayers):
            deal[i] = {}
        j = 0
        for card in self.cards:
            deal[j][card.identifier] = card
            if j == len(deal)-1:
                j = 0
            else:
                j = j+1

        return deal

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
    cards = {}
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

class board(QtGui.QFrame):
    
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
        self.studyTextXPos = self.studyXPos + self.rectSize/3
        self.studyTextYPos = self.studyYPos + self.rectSize/2
        self.studyMustardXPos = self.studyXPos + self.playerSize
        self.studyMustardYPos = self.studyYPos + self.playerSize
        self.studyScarletXPos = self.studyXPos + self.rectSize/2
        self.studyScarletYPos = self.studyYPos + self.playerSize
        self.studyPlumXPos = self.studyXPos + self.rectSize - self.playerSize
        self.studyPlumYPos = self.studyYPos + self.playerSize
        self.studyPeacockXPos = self.studyXPos + self.playerSize
        self.studyPeacockYPos = self.studyYPos + self.rectSize - self.playerSize
        self.studyGreenXPos = self.studyXPos + self.rectSize/2
        self.studyGreenYPos = self.studyYPos + self.rectSize - self.playerSize
        self.studyWhiteXPos = self.studyXPos + self.rectSize - self.playerSize
        self.studyWhiteYPos = self.studyYPos + self.rectSize - self.playerSize
        # Hall Coordinates
        self.hallXPos = x2Pos
        self.hallYPos = y1Pos
        self.hallTextXPos = self.hallXPos + self.rectSize/3
        self.hallTextYPos = self.hallYPos + self.rectSize/2
        self.hallMustardXPos = self.hallXPos + self.playerSize
        self.hallMustardYPos = self.hallYPos + self.playerSize
        self.hallScarletXPos = self.hallXPos + self.rectSize/2
        self.hallScarletYPos = self.hallYPos + self.playerSize
        self.hallPlumXPos = self.hallXPos + self.rectSize - self.playerSize
        self.hallPlumYPos = self.hallYPos + self.playerSize
        self.hallPeacockXPos = self.hallXPos + self.playerSize
        self.hallPeacockYPos = self.hallYPos + self.rectSize - self.playerSize
        self.hallGreenXPos = self.hallXPos + self.rectSize/2
        self.hallGreenYPos = self.hallYPos + self.rectSize - self.playerSize
        self.hallWhiteXPos = self.hallXPos + self.rectSize - self.playerSize
        self.hallWhiteYPos = self.hallYPos + self.rectSize - self.playerSize
        # Lounge Coordinates
        self.loungeXPos = x3Pos
        self.loungeYPos = y1Pos
        self.loungeTextXPos = self.loungeXPos + self.rectSize/3
        self.loungeTextYPos = self.loungeYPos + self.rectSize/2
        self.loungeMustardXPos = self.loungeXPos + self.playerSize
        self.loungeMustardYPos = self.loungeYPos + self.playerSize
        self.loungeScarletXPos = self.loungeXPos + self.rectSize/2
        self.loungeScarletYPos = self.loungeYPos + self.playerSize
        self.loungePlumXPos = self.loungeXPos + self.rectSize - self.playerSize
        self.loungePlumYPos = self.loungeYPos + self.playerSize
        self.loungePeacockXPos = self.loungeXPos + self.playerSize
        self.loungePeacockYPos = self.loungeYPos + self.rectSize - self.playerSize
        self.loungeGreenXPos = self.loungeXPos + self.rectSize/2
        self.loungeGreenYPos = self.loungeYPos + self.rectSize - self.playerSize
        self.loungeWhiteXPos = self.loungeXPos + self.rectSize - self.playerSize
        self.loungeWhiteYPos = self.loungeYPos + self.rectSize - self.playerSize
        # Library Coordinates
        self.libraryXPos = x1Pos
        self.libraryYPos = y2Pos
        self.libraryTextXPos = self.libraryXPos + self.rectSize/4
        self.libraryTextYPos = self.libraryYPos + self.rectSize/2
        self.libraryMustardXPos = self.libraryXPos + self.playerSize
        self.libraryMustardYPos = self.libraryYPos + self.playerSize
        self.libraryScarletXPos = self.libraryXPos + self.rectSize/2
        self.libraryScarletYPos = self.libraryYPos + self.playerSize
        self.libraryPlumXPos = self.libraryXPos + self.rectSize - self.playerSize
        self.libraryPlumYPos = self.libraryYPos + self.playerSize
        self.libraryPeacockXPos = self.libraryXPos + self.playerSize
        self.libraryPeacockYPos = self.libraryYPos + self.rectSize - self.playerSize
        self.libraryGreenXPos = self.libraryXPos + self.rectSize/2
        self.libraryGreenYPos = self.libraryYPos + self.rectSize - self.playerSize
        self.libraryWhiteXPos = self.libraryXPos + self.rectSize - self.playerSize
        self.libraryWhiteYPos = self.libraryYPos + self.rectSize - self.playerSize
        # Billiard Room Coordinates
        self.billiardXPos = x2Pos
        self.billiardYPos = y2Pos
        self.billiardTextXPos = self.billiardXPos + self.rectSize/6
        self.billiardTextYPos = self.billiardYPos + self.rectSize/2
        self.billiardMustardXPos = self.billiardXPos + self.playerSize
        self.billiardMustardYPos = self.billiardYPos + self.playerSize
        self.billiardScarletXPos = self.billiardXPos + self.rectSize/2
        self.billiardScarletYPos = self.billiardYPos + self.playerSize
        self.billiardPlumXPos = self.billiardXPos + self.rectSize - self.playerSize
        self.billiardPlumYPos = self.billiardYPos + self.playerSize
        self.billiardPeacockXPos = self.billiardXPos + self.playerSize
        self.billiardPeacockYPos = self.billiardYPos + self.rectSize - self.playerSize
        self.billiardGreenXPos = self.billiardXPos + self.rectSize/2
        self.billiardGreenYPos = self.billiardYPos + self.rectSize - self.playerSize
        self.billiardWhiteXPos = self.billiardXPos + self.rectSize - self.playerSize
        self.billiardWhiteYPos = self.billiardYPos + self.rectSize - self.playerSize
        # Dining Room Coordinates
        self.diningXPos = x3Pos
        self.diningYPos = y2Pos
        self.diningTextXPos = self.diningXPos + self.rectSize/6
        self.diningTextYPos = self.diningYPos + self.rectSize/2
        self.diningMustardXPos = self.diningXPos + self.playerSize
        self.diningMustardYPos = self.diningYPos + self.playerSize
        self.diningScarletXPos = self.diningXPos + self.rectSize/2
        self.diningScarletYPos = self.diningYPos + self.playerSize
        self.diningPlumXPos = self.diningXPos + self.rectSize - self.playerSize
        self.diningPlumYPos = self.diningYPos + self.playerSize
        self.diningPeacockXPos = self.diningXPos + self.playerSize
        self.diningPeacockYPos = self.diningYPos + self.rectSize - self.playerSize
        self.diningGreenXPos = self.diningXPos + self.rectSize/2
        self.diningGreenYPos = self.diningYPos + self.rectSize - self.playerSize
        self.diningWhiteXPos = self.diningXPos + self.rectSize - self.playerSize
        self.diningWhiteYPos = self.diningYPos + self.rectSize - self.playerSize
        # Conservatory Coordinates
        self.conservatoryXPos = x1Pos
        self.conservatoryYPos = y3Pos
        self.conservatoryTextXPos = self.conservatoryXPos + self.rectSize/6
        self.conservatoryTextYPos = self.conservatoryYPos + self.rectSize/2
        self.conservatoryMustardXPos = self.conservatoryXPos + self.playerSize
        self.conservatoryMustardYPos = self.conservatoryYPos + self.playerSize
        self.conservatoryScarletXPos = self.conservatoryXPos + self.rectSize/2
        self.conservatoryScarletYPos = self.conservatoryYPos + self.playerSize
        self.conservatoryPlumXPos = self.conservatoryXPos + self.rectSize - self.playerSize
        self.conservatoryPlumYPos = self.conservatoryYPos + self.playerSize
        self.conservatoryPeacockXPos = self.conservatoryXPos + self.playerSize
        self.conservatoryPeacockYPos = self.conservatoryYPos + self.rectSize - self.playerSize
        self.conservatoryGreenXPos = self.conservatoryXPos + self.rectSize/2
        self.conservatoryGreenYPos = self.conservatoryYPos + self.rectSize - self.playerSize
        self.conservatoryWhiteXPos = self.conservatoryXPos + self.rectSize - self.playerSize
        self.conservatoryWhiteYPos = self.conservatoryYPos + self.rectSize - self.playerSize
        # Ballroom Coordinates
        self.ballroomXPos = x2Pos
        self.ballroomYPos = y3Pos
        self.ballroomTextXPos = self.ballroomXPos + self.rectSize/4
        self.ballroomTextYPos = self.ballroomYPos + self.rectSize/2
        self.ballroomMustardXPos = self.ballroomXPos + self.playerSize
        self.ballroomMustardYPos = self.ballroomYPos + self.playerSize
        self.ballroomScarletXPos = self.ballroomXPos + self.rectSize/2
        self.ballroomScarletYPos = self.ballroomYPos + self.playerSize
        self.ballroomPlumXPos = self.ballroomXPos + self.rectSize - self.playerSize
        self.ballroomPlumYPos = self.ballroomYPos + self.playerSize
        self.ballroomPeacockXPos = self.ballroomXPos + self.playerSize
        self.ballroomPeacockYPos = self.ballroomYPos + self.rectSize - self.playerSize
        self.ballroomGreenXPos = self.ballroomXPos + self.rectSize/2
        self.ballroomGreenYPos = self.ballroomYPos + self.rectSize - self.playerSize
        self.ballroomWhiteXPos = self.ballroomXPos + self.rectSize - self.playerSize
        self.ballroomWhiteYPos = self.ballroomYPos + self.rectSize - self.playerSize
        # Kitchen Coordinates
        self.kitchenXPos = x3Pos
        self.kitchenYPos = y3Pos
        self.kitchenTextXPos = self.kitchenXPos + self.rectSize/3
        self.kitchenTextYPos = self.kitchenYPos + self.rectSize/2
        self.kitchenMustardXPos = self.kitchenXPos + self.playerSize
        self.kitchenMustardYPos = self.kitchenYPos + self.playerSize
        self.kitchenScarletXPos = self.kitchenXPos + self.rectSize/2
        self.kitchenScarletYPos = self.kitchenYPos + self.playerSize
        self.kitchenPlumXPos = self.kitchenXPos + self.rectSize - self.playerSize
        self.kitchenPlumYPos = self.kitchenYPos + self.playerSize
        self.kitchenPeacockXPos = self.kitchenXPos + self.playerSize
        self.kitchenPeacockYPos = self.kitchenYPos + self.rectSize - self.playerSize
        self.kitchenGreenXPos = self.kitchenXPos + self.rectSize/2
        self.kitchenGreenYPos = self.kitchenYPos + self.rectSize - self.playerSize
        self.kitchenWhiteXPos = self.kitchenXPos + self.rectSize - self.playerSize
        self.kitchenWhiteYPos = self.kitchenYPos + self.rectSize - self.playerSize
        # StudyHall Coordinates
        self.shXPos = hallx1Pos
        self.shYPos = hally1Pos
        self.shPlayerXPos = self.shXPos + self.hallLength/2
        self.shPlayerYPos = self.shYPos + self.playerSize
        # HallLounge Coordinates
        self.hlXPos = hallx2Pos
        self.hlYPos = hally1Pos
        self.hlPlayerXPos = self.hlXPos + self.hallLength/2
        self.hlPlayerYPos = self.hlYPos + self.playerSize
        # StudyLibrary Coordinates
        self.slXPos = hallx3Pos
        self.slYPos = hally2Pos
        self.slPlayerXPos = self.slXPos + self.playerSize
        self.slPlayerYPos = self.slYPos + self.hallHeight/2
        # HallBilliardRoom Coordinates
        self.hbXPos = hallx4Pos
        self.hbYPos = hally2Pos
        self.hbPlayerXPos = self.hbXPos + self.playerSize
        self.hbPlayerYPos = self.hbYPos + self.hallHeight/2
        # LoungeDiningRoom Coordinates
        self.ldXPos = hallx5Pos
        self.ldYPos = hally2Pos
        self.ldPlayerXPos = self.ldXPos + self.playerSize
        self.ldPlayerYPos = self.ldYPos + self.hallHeight/2
        # LibraryBilliardRoom Coordinates
        self.lbXPos = hallx1Pos
        self.lbYPos = hally3Pos
        self.lbPlayerXPos = self.lbXPos + self.hallLength/2
        self.lbPlayerYPos = self.lbYPos + self.playerSize
        # BilliardRoomDiningRoom Coordinates
        self.bdXPos = hallx2Pos
        self.bdYPos = hally3Pos
        self.bdPlayerXPos = self.bdXPos + self.hallLength/2
        self.bdPlayerYPos = self.bdYPos + self.playerSize
        # LibraryConservatory Coordinates
        self.lcXPos = hallx3Pos
        self.lcYPos = hally4Pos
        self.lcPlayerXPos = self.lcXPos + self.playerSize
        self.lcPlayerYPos = self.lcYPos + self.hallHeight/2
        # BilliardRoomBallroom Coordinates
        self.bbXPos = hallx4Pos
        self.bbYPos = hally4Pos
        self.bbPlayerXPos = self.bbXPos + self.playerSize
        self.bbPlayerYPos = self.bbYPos + self.hallHeight/2
        # DiningRoomKitchen Coordinates
        self.dkXPos = hallx5Pos
        self.dkYPos = hally4Pos
        self.dkPlayerXPos = self.dkXPos + self.playerSize
        self.dkPlayerYPos = self.dkYPos + self.hallHeight/2
        # ConservatoryBallroom Coordinates
        self.cbXPos = hallx1Pos
        self.cbYPos = hally5Pos
        self.cbPlayerXPos = self.cbXPos + self.hallLength/2
        self.cbPlayerYPos = self.cbYPos + self.playerSize
        # BallroomKitchen Coordinates
        self.bkXPos = hallx2Pos
        self.bkYPos = hally5Pos
        self.bkPlayerXPos = self.bkXPos + self.hallLength/2
        self.bkPlayerYPos = self.bkYPos + self.playerSize
        # Colonel Mustard settings
        self.cmHomeXPos = x3Pos+self.rectSize+self.hallWidth+self.playerSize/2
        self.cmHomeYPos = hally2Pos+self.hallHeight/2
        self.cmColor = QtGui.QColor(204,204,0)
        # Miss Scarlet settings
        self.msHomeXPos = x2Pos+self.rectSize+self.hallLength/2
        self.msHomeYPos = hally1Pos-self.hallWidth-self.playerSize/2
        self.msColor = QtGui.QColor(240,0,0)
        # Professor Plum settings
        self.ppHomeXPos = x1Pos-self.playerSize/2
        self.ppHomeYPos = hally2Pos+self.hallHeight/2
        self.ppColor = QtGui.QColor(153,51,102)
        # Mrs.Peacock Settings
        self.mpHomeXPos = x1Pos-self.playerSize/2
        self.mpHomeYPos = hally4Pos+self.hallHeight/2
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
        self.setStyleSheet('border-image: url(./images/tabletop.jpg)')
        self.setAutoFillBackground(True)

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
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawText(self.studyTextXPos, self.studyTextYPos, 'Study')
        qp.setPen(color)

        # Hall
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.hallXPos, self.hallYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(0,0,0))
        qp.drawText(self.hallTextXPos, self.hallTextYPos, 'Hall') 
        qp.setPen(color)

        #Lounge
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.loungeXPos, self.loungeYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawText(self.loungeTextXPos, self.loungeTextYPos, 'Lounge')
        qp.setPen(color)

        # Library
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.libraryXPos, self.libraryYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(0,0,0))
        qp.drawText(self.libraryTextXPos, self.libraryTextYPos, 'Library')
        qp.setPen(color)

        # Billiard Room
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.billiardXPos, self.billiardYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawText(self.billiardTextXPos, self.billiardTextYPos, 'Billiard Room')
        qp.setPen(color)

        # Dining Room
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.diningXPos, self.diningYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(0,0,0))
        qp.drawText(self.diningTextXPos, self.diningTextYPos, 'Dining Room')
        qp.setPen(color)

        # Conservatory
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.conservatoryXPos, self.conservatoryYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawText(self.conservatoryTextXPos, self.conservatoryTextYPos, 'Conservatory')
        qp.setPen(color)

        # Ballroom
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(self.ballroomXPos, self.ballroomYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(0,0,0))
        qp.drawText(self.ballroomTextXPos, self.ballroomTextYPos, 'Ballroom')
        qp.setPen(color)

        # Kitchen
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(self.kitchenXPos, self.kitchenYPos, self.rectSize, self.rectSize)
        qp.setPen(QtGui.QColor(255,255,255))
        qp.drawText(self.kitchenTextXPos, self.kitchenTextYPos, 'Kitchen')
        qp.setPen(color)

        # Draw a player token
        for player,location in self.players.items():
            if player == 'Colonel Mustard':
                qp.setBrush(self.cmColor)
                if location == 'Colonel MustardHome':
                    center = QtCore.QPoint(self.cmHomeXPos,self.cmHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Hall':
                    center = QtCore.QPoint(self.shPlayerXPos,self.shPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Lounge':
                    center = QtCore.QPoint(self.hlPlayerXPos,self.hlPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Library':
                    center = QtCore.QPoint(self.slPlayerXPos,self.slPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Billiard Room':
                    center = QtCore.QPoint(self.hbPlayerXPos,self.hbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Lounge-Dining Room':
                    center = QtCore.QPoint(self.ldPlayerXPos,self.ldPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Billiard Room':
                    center = QtCore.QPoint(self.lbPlayerXPos,self.lbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Dining Room':
                    center = QtCore.QPoint(self.bdPlayerXPos,self.bdPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Conservatory':
                    center = QtCore.QPoint(self.lcPlayerXPos,self.lcPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Ballroom':
                    center = QtCore.QPoint(self.bbPlayerXPos,self.bbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room-Kitchen':
                    center = QtCore.QPoint(self.dkPlayerXPos,self.dkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory-Ballroom':
                    center = QtCore.QPoint(self.cbPlayerXPos,self.cbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom-Kitchen':
                    center = QtCore.QPoint(self.bkPlayerXPos,self.bkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyMustardXPos,self.studyMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallMustardXPos,self.hallMustardYPos)
                    qp.drawEllipse(center, self.playerSize, self.playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungeMustardXPos,self.loungeMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryMustardXPos,self.libraryMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room':
                    center = QtCore.QPoint(self.billiardMustardXPos,self.billiardMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room':
                    center = QtCore.QPoint(self.diningMustardXPos,self.diningMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryMustardXPos,self.conservatoryMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomMustardXPos,self.ballroomMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenMustardXPos,self.kitchenMustardYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Miss Scarlet':
                qp.setBrush(self.msColor)
                if location == 'Miss ScarletHome':
                    center = QtCore.QPoint(self.msHomeXPos,self.msHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Hall':
                    center = QtCore.QPoint(self.shPlayerXPos,self.shPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Lounge':
                    center = QtCore.QPoint(self.hlPlayerXPos,self.hlPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Library':
                    center = QtCore.QPoint(self.slPlayerXPos,self.slPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Billiard Room':
                    center = QtCore.QPoint(self.hbPlayerXPos,self.hbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Lounge-Dining Room':
                    center = QtCore.QPoint(self.ldPlayerXPos,self.ldPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Billiard Room':
                    center = QtCore.QPoint(self.lbPlayerXPos,self.lbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Dining Room':
                    center = QtCore.QPoint(self.bdPlayerXPos,self.bdPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Conservatory':
                    center = QtCore.QPoint(self.lcPlayerXPos,self.lcPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Ballroom':
                    center = QtCore.QPoint(self.bbPlayerXPos,self.bbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room-Kitchen':
                    center = QtCore.QPoint(self.dkPlayerXPos,self.dkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory-Ballroom':
                    center = QtCore.QPoint(self.cbPlayerXPos,self.cbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom-Kitchen':
                    center = QtCore.QPoint(self.bkPlayerXPos,self.bkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyScarletXPos,self.studyScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallScarletXPos,self.hallScarletYPos)
                    qp.drawEllipse(center, self.playerSize, self.playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungeScarletXPos,self.loungeScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryScarletXPos,self.libraryScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room':
                    center = QtCore.QPoint(self.billiardScarletXPos,self.billiardScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room':
                    center = QtCore.QPoint(self.diningScarletXPos,self.diningScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryScarletXPos,self.conservatoryScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomScarletXPos,self.ballroomScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenScarletXPos,self.kitchenScarletYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Professor Plum':
                qp.setBrush(self.ppColor)
                if location == 'Professor PlumHome':
                    center = QtCore.QPoint(self.ppHomeXPos,self.ppHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Hall':
                    center = QtCore.QPoint(self.shPlayerXPos,self.shPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Lounge':
                    center = QtCore.QPoint(self.hlPlayerXPos,self.hlPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Library':
                    center = QtCore.QPoint(self.slPlayerXPos,self.slPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Billiard Room':
                    center = QtCore.QPoint(self.hbPlayerXPos,self.hbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Lounge-Dining Room':
                    center = QtCore.QPoint(self.ldPlayerXPos,self.ldPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Billiard Room':
                    center = QtCore.QPoint(self.lbPlayerXPos,self.lbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Dining Room':
                    center = QtCore.QPoint(self.bdPlayerXPos,self.bdPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Conservatory':
                    center = QtCore.QPoint(self.lcPlayerXPos,self.lcPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Ballroom':
                    center = QtCore.QPoint(self.bbPlayerXPos,self.bbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room-Kitchen':
                    center = QtCore.QPoint(self.dkPlayerXPos,self.dkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory-Ballroom':
                    center = QtCore.QPoint(self.cbPlayerXPos,self.cbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom-Kitchen':
                    center = QtCore.QPoint(self.bkPlayerXPos,self.bkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPlumXPos,self.studyPlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPlumXPos,self.hallPlumYPos)
                    qp.drawEllipse(center, self.playerSize, self.playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePlumXPos,self.loungePlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPlumXPos,self.libraryPlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room':
                    center = QtCore.QPoint(self.billiardPlumXPos,self.billiardPlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room':
                    center = QtCore.QPoint(self.diningPlumXPos,self.diningPlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPlumXPos,self.conservatoryPlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPlumXPos,self.ballroomPlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPlumXPos,self.kitchenPlumYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Mrs. Peacock':
                qp.setBrush(self.mpColor)
                if location == 'Mrs. PeacockHome':
                    center = QtCore.QPoint(self.mpHomeXPos,self.mpHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Hall':
                    center = QtCore.QPoint(self.shPlayerXPos,self.shPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Lounge':
                    center = QtCore.QPoint(self.hlPlayerXPos,self.hlPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Library':
                    center = QtCore.QPoint(self.slPlayerXPos,self.slPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Billiard Room':
                    center = QtCore.QPoint(self.hbPlayerXPos,self.hbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Lounge-Dining Room':
                    center = QtCore.QPoint(self.ldPlayerXPos,self.ldPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Billiard Room':
                    center = QtCore.QPoint(self.lbPlayerXPos,self.lbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Dining Room':
                    center = QtCore.QPoint(self.bdPlayerXPos,self.bdPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Conservatory':
                    center = QtCore.QPoint(self.lcPlayerXPos,self.lcPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Ballroom':
                    center = QtCore.QPoint(self.bbPlayerXPos,self.bbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room-Kitchen':
                    center = QtCore.QPoint(self.dkPlayerXPos,self.dkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory-Ballroom':
                    center = QtCore.QPoint(self.cbPlayerXPos,self.cbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom-Kitchen':
                    center = QtCore.QPoint(self.bkPlayerXPos,self.bkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyPeacockXPos,self.studyPeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallPeacockXPos,self.hallPeacockYPos)
                    qp.drawEllipse(center, self.playerSize, self.playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungePeacockXPos,self.loungePeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryPeacockXPos,self.libraryPeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room':
                    center = QtCore.QPoint(self.billiardPeacockXPos,self.billiardPeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room':
                    center = QtCore.QPoint(self.diningPeacockXPos,self.diningPeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryPeacockXPos,self.conservatoryPeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomPeacockXPos,self.ballroomPeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenPeacockXPos,self.kitchenPeacockYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Mr. Green':
                qp.setBrush(self.mgColor)
                if location == 'Mr. GreenHome':
                    center = QtCore.QPoint(self.mgHomeXPos,self.mgHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Hall':
                    center = QtCore.QPoint(self.shPlayerXPos,self.shPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Lounge':
                    center = QtCore.QPoint(self.hlPlayerXPos,self.hlPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Library':
                    center = QtCore.QPoint(self.slPlayerXPos,self.slPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Billiard Room':
                    center = QtCore.QPoint(self.hbPlayerXPos,self.hbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Lounge-Dining Room':
                    center = QtCore.QPoint(self.ldPlayerXPos,self.ldPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Billiard Room':
                    center = QtCore.QPoint(self.lbPlayerXPos,self.lbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Dining Room':
                    center = QtCore.QPoint(self.bdPlayerXPos,self.bdPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Conservatory':
                    center = QtCore.QPoint(self.lcPlayerXPos,self.lcPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Ballroom':
                    center = QtCore.QPoint(self.bbPlayerXPos,self.bbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room-Kitchen':
                    center = QtCore.QPoint(self.dkPlayerXPos,self.dkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory-Ballroom':
                    center = QtCore.QPoint(self.cbPlayerXPos,self.cbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom-Kitchen':
                    center = QtCore.QPoint(self.bkPlayerXPos,self.bkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyGreenXPos,self.studyGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallGreenXPos,self.hallGreenYPos)
                    qp.drawEllipse(center, self.playerSize, self.playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungeGreenXPos,self.loungeGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryGreenXPos,self.libraryGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room':
                    center = QtCore.QPoint(self.billiardGreenXPos,self.billiardGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room':
                    center = QtCore.QPoint(self.diningGreenXPos,self.diningGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryGreenXPos,self.conservatoryGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomGreenXPos,self.ballroomGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenGreenXPos,self.kitchenGreenYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
            elif player == 'Mrs. White':
                qp.setBrush(self.mwColor)
                if location == 'Mrs. WhiteHome':
                    center = QtCore.QPoint(self.mwHomeXPos,self.mwHomeYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Hall':
                    center = QtCore.QPoint(self.shPlayerXPos,self.shPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Lounge':
                    center = QtCore.QPoint(self.hlPlayerXPos,self.hlPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study-Library':
                    center = QtCore.QPoint(self.slPlayerXPos,self.slPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall-Billiard Room':
                    center = QtCore.QPoint(self.hbPlayerXPos,self.hbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Lounge-Dining Room':
                    center = QtCore.QPoint(self.ldPlayerXPos,self.ldPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Billiard Room':
                    center = QtCore.QPoint(self.lbPlayerXPos,self.lbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Dining Room':
                    center = QtCore.QPoint(self.bdPlayerXPos,self.bdPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library-Conservatory':
                    center = QtCore.QPoint(self.lcPlayerXPos,self.lcPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room-Ballroom':
                    center = QtCore.QPoint(self.bbPlayerXPos,self.bbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room-Kitchen':
                    center = QtCore.QPoint(self.dkPlayerXPos,self.dkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory-Ballroom':
                    center = QtCore.QPoint(self.cbPlayerXPos,self.cbPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom-Kitchen':
                    center = QtCore.QPoint(self.bkPlayerXPos,self.bkPlayerYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Study':
                    center = QtCore.QPoint(self.studyWhiteXPos,self.studyWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Hall':
                    center = QtCore.QPoint(self.hallWhiteXPos,self.hallWhiteYPos)
                    qp.drawEllipse(center, self.playerSize, self.playerSize)
                elif location == 'Lounge':
                    center = QtCore.QPoint(self.loungeWhiteXPos,self.loungeWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Library':
                    center = QtCore.QPoint(self.libraryWhiteXPos,self.libraryWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Billiard Room':
                    center = QtCore.QPoint(self.billiardWhiteXPos,self.billiardWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Dining Room':
                    center = QtCore.QPoint(self.diningWhiteXPos,self.diningWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Conservatory':
                    center = QtCore.QPoint(self.conservatoryWhiteXPos,self.conservatoryWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Ballroom':
                    center = QtCore.QPoint(self.ballroomWhiteXPos,self.ballroomWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                elif location == 'Kitchen':
                    center = QtCore.QPoint(self.kitchenWhiteXPos,self.kitchenWhiteYPos)
                    qp.drawEllipse(center,self.playerSize,self.playerSize)
                        
        qp.end()
