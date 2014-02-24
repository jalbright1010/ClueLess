#!/usr/bin/python

import socket
import time
import sys
import thread
import cPickle as pickle
import sip
import gameplay
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    receiveSignal = QtCore.pyqtSignal(str)
    usernameSignal = QtCore.pyqtSignal()
    characterSignal = QtCore.pyqtSignal(str)
    gameboardSignal = QtCore.pyqtSignal(str)
    turnSignal = QtCore.pyqtSignal(str)
    suggestionSignal = QtCore.pyqtSignal()
    cardSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()
        host = '98.218.228.27'
        #host = '127.0.0.1'
        #host = '192.168.41.27'
        port = 40004
        #port = 4004
        self.connectToServer(host, port)
        self.receiveSignal.connect(self.appendMessage)
        self.usernameSignal.connect(self.askForUsername)
        self.characterSignal.connect(self.createCharacterPicker)
        self.gameboardSignal.connect(self.drawGameboard)
        self.turnSignal.connect(self.createMoves)
        self.suggestionSignal.connect(self.createSuggestionPicker)
        self.cardSignal.connect(self.createCards)
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

    @QtCore.pyqtSlot(str)
    def createCharacterPicker(self, used):
        self.inputWindow.setReadOnly(True)
        self.getCharacter = QtGui.QWidget()
        self.getCharacter.resize(250,250)
        self.getCharacter.move(self.width()/2-62, self.height()/2-62)
        form = QtGui.QFormLayout()
        form.addRow(QtGui.QLabel('Pick your character for the game:'))
        self.getCharacter.charList = QtGui.QListWidget()
        for character in gameplay.PEOPLE:
            if character not in pickle.loads(str(used)):
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
        self.character = character
        self.getCharacter.close()
        self.inputWindow.setReadOnly(False)

    @QtCore.pyqtSlot(str)
    def drawGameboard(self, pickled):
        self.gameboard.players = pickle.loads(str(pickled))
        self.gameboard.update()

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

        self.cardGroup = QtGui.QGroupBox()
        self.cardGroup.setTitle('Cards')
        self.centralWidget.form = QtGui.QFormLayout()
        self.centralWidget.form.addRow(self.createBoard(),self.cardGroup)
        self.centralWidget.form.addRow(self.createChatGroup(), self.createMoveGroup())
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

    def createMoveGroup(self):
        self.moveGroup = QtGui.QGroupBox()
        form = QtGui.QFormLayout()

        form.addRow(QtGui.QLabel('Waiting for your turn...'))
        
        self.moveGroup.setLayout(form)
        
        return self.moveGroup

    @QtCore.pyqtSlot(str)
    def createMoves(self, pickled):
        moves = pickle.loads(str(pickled))
        form = QtGui.QFormLayout()
        
        for space in moves:
            label = QtGui.QLabel('Move to %s...' % space)
            button = QtGui.QPushButton('Move')
            button.clicked.connect(self.buttonClicked(space))
            form.addRow(label,button)

        for i in reversed(range(self.moveGroup.layout().count())):
            sip.delete(self.moveGroup.layout().itemAt(i).widget())
        sip.delete(self.moveGroup.layout())
        self.moveGroup.setLayout(form)

    def buttonClicked(self, space):
        def clicked():
            self.client.send('function::movePlayer:'+space)
            self.gameboard.players[self.character] = space
            self.gameboard.update()
            form = QtGui.QFormLayout()
            button = QtGui.QPushButton('End Turn')
            button.clicked.connect(self.sendEndTurnMessage)
            form.addRow(button)
            for i in reversed(range(self.moveGroup.layout().count())):
                sip.delete(self.moveGroup.layout().itemAt(i).widget())
            sip.delete(self.moveGroup.layout())
            self.moveGroup.setLayout(form)
        return clicked

    @QtCore.pyqtSlot()
    def createSuggestionPicker(self):
        self.suggestionPicker = QtGui.QWidget()
        form = QtGui.QFormLayout()
        form.addRow(QtGui.QLabel('Select the items for your suggestion:'))
        self.suspectCombo = QtGui.QComboBox()
        for suspect in gameplay.PEOPLE:
            self.suspectCombo.addItem(suspect)
        self.roomCombo = QtGui.QComboBox()
        for room in gameplay.ROOMS:
            self.roomCombo.addItem(room)
        self.weaponCombo = QtGui.QComboBox()
        for weapon in gameplay.WEAPONS:
            self.weaponCombo.addItem(weapon)
        button = QtGui.QPushButton('Make Suggestion')
        button.clicked.connect(self.sendSuggestionMessage)
        form.addRow(self.suspectCombo)
        form.addRow(self.roomCombo)
        form.addRow(self.weaponCombo)
        form.addRow(button)
        self.suggestionPicker.setLayout(form)
        self.suggestionPicker.show()

    def sendSuggestionMessage(self):
        suggestion = [self.suspectCombo.currentText(),
                      self.roomCombo.currentText(),
                      self.weaponCombo.currentText()]
        self.client.send('function::makingSuggestion:'+pickle.dumps(suggestion))
        self.suggestionPicker.close()

    def sendEndTurnMessage(self):
        self.client.send('function::endTurn')
        form = QtGui.QFormLayout()
        form.addRow(QtGui.QLabel('Awaiting your next turn....'))
        for i in reversed(range(self.moveGroup.layout().count())):
            sip.delete(self.moveGroup.layout().itemAt(i).widget())
        sip.delete(self.moveGroup.layout())
        self.moveGroup.setLayout(form)

    def sendMessage(self):
        self.client.send('message::'+str(self.inputWindow.text()))
        self.inputWindow.clear()

    def createBoard(self):
        self.gameboard = gameplay.board(self.width()/2, self.height()/2)
        return self.gameboard

    @QtCore.pyqtSlot(str)
    def createCards(self, pickled):
        cards = pickle.loads(str(pickled))
        form = QtGui.QFormLayout()
        for card in cards:
            form.addRow(QtGui.QLabel(card))
        self.cardGroup.setLayout(form)

    def createReceiveThread(self):
        def threaded():
            try:
                while True:
                    s = self.client.recv(1024).strip()
                    if s == 'username':
                        self.usernameSignal.emit()
                    elif s == 'suggestion':
                        self.suggestionSignal.emit()
                    elif ':' in s:
                        splt = s.split(':')
                        if splt[0] == 'updateGameboard':
                            self.gameboardSignal.emit(splt[1])
                        elif splt[0] == 'usedChars':
                            self.characterSignal.emit(splt[1])
                        elif splt[0] == 'yourTurn':
                            self.turnSignal.emit(splt[1])
                        elif splt[0] == 'cards':
                            self.cardSignal.emit(splt[1])
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
