#!/usr/bin/python

import socket
import time
import sys
import thread
import cPickle as pickle
import gameplay
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        host = '192.168.41.27'
        port = 4004
        self.connectToServer(host, port)
        self.initUI()

    def connectToServer(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except socket.error:
            print 'Could not connect to server'
            sys.exit()
    
    def initUI(self):
        self.initWidth = (QtGui.QDesktopWidget().availableGeometry().width() *.9)
        self.initHeight = (QtGui.QDesktopWidget().availableGeometry().height() * .9)
        self.resize(self.initWidth, self.initHeight)
        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.createMenuBar()

        self.centralWidget.form = QtGui.QFormLayout()
        self.centralWidget.form.addROw(self.createBoard())
        self.centralWidget.setLayout(self.centralWidget.form)

    def createMenuBar(self):
        menubar = self.menuBar()
        mainMenu = menubar.addMenu('File')
        create = QtGui.QAction('Create Game', self)
        create.setShortcut('Ctrl+G')
        #create.triggered.connect(self.createGameLauncher)
        mainMenu.addAction(create)
        join = QtGui.QAction('Join Game', self)
        join.setShortcut('Ctrl+J')
        #join.triggered.connect(self.sendGameRequest)
        mainMenu.addAction(join)
        quit = QtGui.QAction('Exit', self)
        quit.setShortcut('Ctrl+Q')
        quit.triggered.connect(self.close)
        mainMenu.addAction(quit)

    def createBoard(self):
        self.gameboard = gameplay.board(self.width()/2, self.height()/2)
        return self.gameboard
