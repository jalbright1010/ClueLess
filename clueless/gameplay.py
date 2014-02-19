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
HALLWAYS = ['Hall1', 'Hall2', 'Hall3', 'Hall4', 'Hall5', 
            'Hall6', 'Hall7', 'Hall8', 'Hall9', 'Hall10']

class game():
    id = ''
    players = []
    caseFile = {}

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.setup()
    
    def addPlayer(self, name, char):
        p = player(name, char)
        self.players.append(p)

    def setup(self):
        # Randomly choose the murder scenario
        who = random.randint(0,5)
        where = random.randint(0,8)
        weapon = random.randint(0,5)
        
        # Create the case file for this game
        self.caseFile['Who'] = PEOPLE[who]
        self.caseFile['Where'] = ROOMS[where]
        self.caseFile['Weapon'] = WEAPONS[weapon]
        
        # Set up a temporary list minus the chosen case file
        # cards to give out to the game players
        tmp = []
        p = PEOPLE
        p.pop(who)
        r = ROOMS
        r.pop(where)
        w = WEAPONS
        w.pop(weapon)
        tmp.extend(p)
        tmp.extend(r)
        tmp.extend(w)
        random.shuffle(tmp)
        
        # Dish out all remaining cards to the players in the game
        #while len(tmp) > 0:
        #    for player in self.players:
        #        if len(tmp) != 0:
        #            player.addCard(tmp.pop())

class room():
    id = ''
    connections = []

    def __init__(self, id, connections):
        self.id = id
        self.connections.extend(connections)

class hallway():
    id = ''
    connections = []
    
    def __init__(self, id, connections):
        self.id = id
        self.connections.extend(connections)

class player():
    name = ''
    character = ''
    cards = []

    def __init__(self, name, char):
        self.name = name
        self.character = char
 
    def addCard(self, card):
        self.cards.extend(card)

class notebook():
    pass

class board(QtGui.QWidget):
    
    def __init__(self, width, height):
        super(board, self).__init__()
        self.setFixedSize(width, height)
        #self.setLayout(QtGui.QFormLayout())
        self.update()
        self.player = ''
        self.drawingPlayer = False

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
        if self.drawingPlayer:
            if self.player == 'Colonel Mustard':
                center = QtCore.QPoint(x3Pos+rectSize+hallWidth+playerSize/2,hally4Pos+hallHeight/2)
                qp.setBrush(QtGui.QColor(204,204,0))
                qp.drawEllipse(center, playerSize, playerSize)
            elif self.player == 'Miss Scarlet':
                center = QtCore.QPoint(x2Pos+rectSize+hallLength/2,hally1Pos-hallWidth-playerSize/2)
                qp.setBrush(QtGui.QColor(240,0,0))
                qp.drawEllipse(center, playerSize, playerSize)
            elif self.player == 'Professor Plum':
                center = QtCore.QPoint(x1Pos-playerSize/2,hally4Pos+hallHeight/2)
                qp.setBrush(QtGui.QColor(153,51,102))
                qp.drawEllipse(center, playerSize, playerSize)
            elif self.player == 'Mrs. Peacock':
                center = QtCore.QPoint(x1Pos-playerSize/2,hally5Pos+hallHeight/2)
                qp.setBrush(QtGui.QColor(0,0,245))
                qp.drawEllipse(center, playerSize, playerSize)
            elif self.player == 'Mr. Green':
                center = QtCore.QPoint(hallx1Pos+hallLength/2,y3Pos+rectSize+playerSize/2)
                qp.setBrush(QtGui.QColor(51,153,0))
                qp.drawEllipse(center, playerSize, playerSize)
            elif self.player == 'Mrs. White':
                center = QtCore.QPoint(hallx2Pos+hallLength/2,y3Pos+rectSize+playerSize/2)
                qp.setBrush(QtGui.QColor(255,255,255))
                qp.drawEllipse(center, playerSize, playerSize)

        qp.end()
