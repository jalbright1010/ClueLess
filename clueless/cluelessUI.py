#!/usr/bin/python

import socket
import time
import sys
import thread
import cPickle as pickle
import gameplay
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    receiveSignal = QtCore.pyqtSignal(str)
    usernameSignal = QtCore.pyqtSignal()
    characterSignal = QtCore.pyqtSignal(str)
    characterAddSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()
        host = '127.0.0.1'
        port = 4004
        self.connectToServer(host, port)
        self.receiveSignal.connect(self.appendMessage)
        self.usernameSignal.connect(self.askForUsername)
        self.characterSignal.connect(self.createCharacterPicker)
        self.characterAddSignal.connect(self.drawCharacter)
        self.initUI()
        self.createReceiveThread()
        
    @QtCore.pyqtSlot(str)
    def appendMessage(self, message):
	   self.messageWindow.append(message)
	   self.messageWindow.moveCursor(QtGui.QTextCursor.End)

    @QtCore.pyqtSlot()
    def askForUsername(self):
    	self.getUsername = QtGui.QWidget()
    	self.getUsername.resize(250,100)
        self.getUsername.move(self.width()/2-62,self.height()/2-25)
    	form = QtGui.QFormLayout()
    	form.addRow(QtGui.QLabel('Please enter your username:'))
    	self.getUsername.edit = QtGui.QLineEdit()
    	self.getUsername.edit.returnPressed.connect(self.sendUsername)
    	form.addRow(self.getUsername.edit)
    	self.getUsername.setLayout(form)
    	self.getUsername.show()

    def sendUsername(self):
    	self.client.send(str(self.getUsername.edit.text()))
    	self.getUsername.close()
    	self.inputWindow.setReadOnly(False)
        self.sendCharRequest()

    def sendCharRequest(self):
        self.client.send('function::requestingChars')

    @QtCore.pyqtSlot(str)
    def createCharacterPicker(self, used):
        self.getCharacter = QtGui.QWidget()
        self.getCharacter.resize(250,250)
        self.getCharacter.move(self.width()/2-62, self.height()/2-62)
        form = QtGui.QFormLayout()
        form.addRow(QtGui.QLabel('Pick your character for the game:'))
        self.getCharacter.charList = QtGui.QListWidget()
        for character in gameplay.PEOPLE:
            if character not in [x.character for x in pickle.loads(str(used))]:
                self.getCharacter.charList.addItem(character)
        self.getCharacter.charList.setCurrentRow(0)
        form.addRow(self.getCharacter.charList)
        button = QtGui.QPushButton('Pick')
        button.setFixedSize(65,25)
        button.clicked.connect(self.chooseCharacter)
        form.addRow(button)
        self.getCharacter.setLayout(form)
        self.getCharacter.show()

    def chooseCharacter(self):
        character = str(self.getCharacter.charList.currentItem().text())
        self.client.send('function::joinGame:'+character)
        self.getCharacter.close()

    @QtCore.pyqtSlot(str)
    def drawCharacter(self, pickled):
        self.gameboard.players = pickle.loads(str(pickled))
        self.gameboard.update()

    @QtCore.pyqtSlot()
    def gameStart(self):
        pass

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
        self.centralWidget.form.addRow(self.createBoard())
        self.centralWidget.form.addRow(self.createChatGroup(), self.createButtonGroup())
        self.centralWidget.setLayout(self.centralWidget.form)

    def createMenuBar(self):
        menubar = self.menuBar()
        mainMenu = menubar.addMenu('File')
        start = QtGui.QAction('Start Game', self)
        start.setShortcut('Ctrl+S')
        start.triggered.connect(self.sendStartSignal)
        mainMenu.addAction(start)
        self.readyAction = QtGui.QAction('Ready to Start', self)
        self.readyAction.setShortcut('Ctrl+R')
        self.readyAction.triggered.connect(self.sendReadySignal)
        mainMenu.addAction(self.readyAction)
        q = QtGui.QAction('Exit', self)
        q.setShortcut('Ctrl+Q')
        q.triggered.connect(self.close)
        mainMenu.addAction(q)

    def sendStartSignal(self):
        self.client.send('function::start')

    def sendReadySignal(self):
        self.client.send('function::ready')
        self.readyAction.setEnabled(False)

    def createChatGroup(self):
        group = QtGui.QGroupBox()
        form = QtGui.QFormLayout()

        self.messageWindow = QtGui.QTextEdit(group)
        self.messageWindow.setFixedWidth(self.width() / 2)
        self.messageWindow.setFixedHeight(self.height() / 4)
        self.messageWindow.setReadOnly(True)

    	self.inputWindow = QtGui.QLineEdit(group)
    	self.inputWindow.setFixedWidth(self.width() / 2)
    	self.inputWindow.setReadOnly(True)
    	self.inputWindow.returnPressed.connect(self.sendMessage)
        
        form.addRow(self.messageWindow)
        form.addRow(self.inputWindow)
        
        group.setLayout(form)

        return group

    def createButtonGroup(self):
        group = QtGui.QGroupBox()
        grid = QtGui.QGridLayout()
        
        self.lButton = QtGui.QPushButton('Left')
        self.rButton = QtGui.QPushButton('Right')
        self.uButton = QtGui.QPushButton('Up')
        self.dButton = QtGui.QPushButton('Down')
        self.rdButton = QtGui.QPushButton('R Down')
        self.ldButton = QtGui.QPushButton('L Down')
        self.ruButton = QtGui.QPushButton('R Up')
        self.luButton = QtGui.QPushButton('L Up')
        
        grid.addWidget(self.ldButton, 0, 0)
        grid.addWidget(self.uButton, 0, 1)
        grid.addWidget(self.rdButton, 0, 2)
        grid.addWidget(self.lButton, 1, 0)
        grid.addWidget(self.rButton, 1, 2)
        grid.addWidget(self.ruButton, 2, 0)
        grid.addWidget(self.dButton, 2, 1)
        grid.addWidget(self.luButton, 2, 2)
            
        group.setLayout(grid)
        
        return group

    def sendMessage(self):
        self.client.send('message::'+str(self.inputWindow.text()))
        self.inputWindow.clear()

    def createBoard(self):
        self.gameboard = gameplay.board(self.width()/2, self.height()/2)
        return self.gameboard

    def createKeys(self):
        pass

    def createReceiveThread(self):
        def threaded():
            try:
                while True:
                    s = self.client.recv(1024).strip()
                    if s == 'username':
                        self.usernameSignal.emit()
                    elif ':' in s:
                        splt = s.split(':')
                        if splt[0] == 'characterAdded':
                            self.characterAddSignal.emit(splt[1])
                        elif splt[0] == 'usedChars':
                            self.characterSignal.emit(splt[1])
                    else:
                        self.receiveSignal.emit(str(s))
            except (SystemExit, KeyboardInterrupt):
                sys.exit()
        self.receiveThread = thread.start_new_thread(threaded, ())    

def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
