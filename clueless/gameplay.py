#!/usr/bin/python

from PyQt4 import QtGui, QtCore
import uuid

class game():
    id = ''
    players = []
    deck = {}
    caseFile = {}

    def __init__(self):
        self.id = str(uuid.uuid4())

class player():
    pass

class notebook():
    pass

class board(QtGui.QWidget):
    
    def __init__(self, width, height):
        super(board, self).__init__()
        self.setFixedSize(width, height)
        self.setLayout(QtGui.QFormLayout())

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()

    def drawRectangles(self, qp):
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
        qp.drawText(x1Pos+18,y1Pos+14,'Library')

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
