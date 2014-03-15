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
    revealSignal = QtCore.pyqtSignal(str,str)

    def __init__(self):
        super(MainWindow, self).__init__()
        # Make a connection to the Clue-Less server
        host = '69.255.109.89'
        #host = '127.0.0.1'
        #host = '192.168.41.27'
        port = 40004
        #port = 4004
        self.connectToServer(host, port)
        
        # Connect all signals to their respective slot
        self.receiveSignal.connect(self.appendMessage)
        self.usernameSignal.connect(self.showUsernameDialog)
        self.characterSignal.connect(self.showCharacterDialog)
        self.gameboardSignal.connect(self.updateGameboard)
        self.turnSignal.connect(self.createMoves)
        self.suggestionSignal.connect(self.showSuggestionDialog)
        self.cardSignal.connect(self.createCards)
        self.revealSignal.connect(self.showRevealDialog)
        
        # Create custom dialogs
        self.getUsername = UsernameDialog()
        self.getCharacter = CharacterDialog()
        self.getSuggestion = SuggestionDialog()
        self.getReveal = RevealDialog()
        
        self.initUI()
        self.createReceiveThread()
        
    # Initalize the GUI
    def initUI(self):
        self.initWidth = (QtGui.QDesktopWidget().availableGeometry().width() *.9)
        self.initHeight = (QtGui.QDesktopWidget().availableGeometry().height() * .9)
        self.resize(self.initWidth, self.initHeight)
        
        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.createMenuBar()

        self.centralWidget.form = QtGui.QFormLayout()
        
        self.cardGroup = QtGui.QGroupBox()
        self.cardGroup.setTitle('Cards')
        
        self.centralWidget.form.addRow(self.createBoard(),self.cardGroup)
        self.centralWidget.form.addRow(self.createChatGroup(), self.createMoveGroup())
        
        self.centralWidget.setLayout(self.centralWidget.form)
        
    # Appends a message to the message log area 
    # when a message is received
    @QtCore.pyqtSlot(str)
    def appendMessage(self, message):
	   self.messageWindow.append(message)
	   self.messageWindow.moveCursor(QtGui.QTextCursor.End)

    # Shows the custom dialog box for entering username
    @QtCore.pyqtSlot()
    def showUsernameDialog(self):
        self.setDisabled(True)
        self.setWindowOpacity(0.90)
    	self.getUsername.edit.returnPressed.connect(self.handleUsername)
    	self.getUsername.show()

    # Sends the user entered username to server
    def handleUsername(self):
    	self.connection.send(str(self.getUsername.edit.text()))
    	self.getUsername.close()
        self.setWindowOpacity(1.0)
        self.setDisabled(False)
      
    # Shows the custom dialog box for choosing a character
    @QtCore.pyqtSlot(str)
    def showCharacterDialog(self, used):
        self.setDisabled(True)
        self.setWindowOpacity(0.90)
        for character in gameplay.PEOPLE:
            if character not in pickle.loads(str(used)):
                self.getCharacter.characterList.addItem(character)
        self.getCharacter.characterList.setCurrentRow(0)
        self.getCharacter.button.clicked.connect(self.handleCharacterChoice)
        self.getCharacter.show()

    # Sends the character choice to the server
    # Stores a local copy of the character
    def handleCharacterChoice(self):
        self.character = str(self.getCharacter.characterList.currentItem().text())
        self.connection.send('function::joinGame:'+self.character)
        self.getCharacter.close()
        self.setWindowOpacity(1.0)
        self.setDisabled(False)

    @QtCore.pyqtSlot(str)
    def updateGameboard(self, pickled):
        self.gameboard.players = pickle.loads(str(pickled))
        self.gameboard.update()

    # Creates socket connection with the server
    def connectToServer(self, host, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.connect((host, port))
        except socket.error:
            print 'Could not connect to server'
            sys.exit()

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
        self.connection.send('function::start')

    def sendReadySignal(self):
        self.connection.send('function::ready')
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
            button.clicked.connect(self.handleMoveChoice(space))
            form.addRow(label,button)

        for i in reversed(range(self.moveGroup.layout().count())):
            sip.delete(self.moveGroup.layout().itemAt(i).widget())
        sip.delete(self.moveGroup.layout())
        self.moveGroup.setLayout(form)

    def handleMoveChoice(self, space):
        def clicked():
            self.connection.send('function::movePlayer:'+space)
            self.gameboard.players[self.character] = space
            self.gameboard.update()
            
            layout = QtGui.QFormLayout()
            button = QtGui.QPushButton('End Turn')
            button.clicked.connect(self.handleEndTurn)
            layout.addRow(button)
            for i in reversed(range(self.moveGroup.layout().count())):
                sip.delete(self.moveGroup.layout().itemAt(i).widget())
            sip.delete(self.moveGroup.layout())
            self.moveGroup.setLayout(layout)
        return clicked

    def handleEndTurn(self):
        self.connection.send('function::endTurn')
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel('Awaiting your next turn...'))
        for i in reversed(range(self.moveGroup.layout().count())):
            sip.delete(self.moveGroup.layout().itemAt(i).widget())
        sip.delete(self.moveGroup.layout())
        self.moveGroup.setLayout(layout)

    def sendMessage(self):
        self.connection.send('message::'+str(self.inputWindow.text()))
        self.inputWindow.clear()

    def createBoard(self):
        self.gameboard = gameplay.board(self.width()/2, self.height()/2)
        return self.gameboard

    @QtCore.pyqtSlot(str)
    def createCards(self, pickled):
        cards = pickle.loads(str(pickled))
        layout = QtGui.QFormLayout()
        for card in cards:
            layout.addRow(QtGui.QLabel(card))
        self.cardGroup.setLayout(layout)

    @QtCore.pyqtSlot()
    def showSuggestionDialog(self):
        self.setDisabled(True)
        self.setWindowOpacity(.90)
        self.getSuggestion.button.clicked.connect(self.handleSuggestion)
        self.getSuggestion.show()

    def handleSuggestion(self):
        suggestion = [self.getSuggestion.suspectCombo.currentText(),
                      self.getSuggestion.weaponCombo.currentText()]
        self.connection.send('function::makingSuggestion:'+
                             pickle.dumps(suggestion))
        self.getSuggestion.close()
        self.setWindowOpacity(1.)
        self.setDisabled(False)

    @QtCore.pyqtSlot(str,str)
    def showRevealDialog(self, pickled, name):
        self.setDisabled(True)
        self.setWindowOpacity(.90)
        cards = pickle.load(str(pickled))
        self.getReveal.player = name
        self.getReveal.label.setText('Choose which card to reveal to %s:' % name)
        for card in cards:
            self.getReveal.cardList.addItem(card)
        self.getReveal.cardList.setCurrentRow(0)
        self.getReveal.button.clicked.connect(self.handleRevealChoice)
        self.getReveal.show()
        
    def handleRevealChoice(self):
        choice = str(self.getReveal.cardList.currentItem().text())
        name = self.getReveal.player
        self.connection.send('function::revealCard:%s:%s' % (choice,name))
        self.getReveal.close()
        self.setWindowOpacity(1.)
        self.setDisabled(False)
        
    def createReceiveThread(self):
        def threaded():
            try:
                while True:
                    s = self.connection.recv(1024).strip()
                    if ':' in s:
                        splt = s.split(':')
                        if splt[0] == 'updateGameboard':
                            self.gameboardSignal.emit(splt[1])
                        elif splt[0] == 'usedChars':
                            self.characterSignal.emit(splt[1])
                        elif splt[0] == 'yourTurn':
                            self.turnSignal.emit(splt[1])
                        elif splt[0] == 'cards':
                            self.cardSignal.emit(splt[1])
                        elif splt[0] == 'revealCard':
                            self.revealSignal.emit(splt[1],splt[2])
                    else:
                        if s == 'username':
                            self.usernameSignal.emit()
                        elif s == 'suggestion':
                            self.suggestionSignal.emit()
                        else:
                            self.receiveSignal.emit(str(s))
            except (SystemExit, KeyboardInterrupt):
                sys.exit()
        self.receiveThread = thread.start_new_thread(threaded, ())    

class UsernameDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(UsernameDialog,self).__init__(parent)
        layout = QtGui.QFormLayout()
        self.name = ''
        
        self.label = QtGui.QLabel('Please enter your username:')
        self.edit = QtGui.QLineEdit('enter your username for gameplay')
        
        layout.addRow(self.label)
        layout.addRow(self.edit)
        
        self.setLayout(layout)

class CharacterDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(CharacterDialog,self).__init__(parent)
        layout = QtGui.QFormLayout()
        
        self.label = QtGui.QLabel('Please choose your character:')
        self.characterList = QtGui.QListWidget()
        self.button = QtGui.QPushButton('Pick')
        self.button.setFixedSize(65,25)
        
        layout.addRow(self.label)
        layout.addRow(self.characterList)
        layout.addRow(self.button)
        
        self.setLayout(layout)
  
class SuggestionDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(SuggestionDialog,self).__init__(parent)
        layout = QtGui.QFormLayout()
          
        self.label = QtGui.QLabel('Select the items for your suggestion:')
        self.suspectCombo = QtGui.QComboBox()
        self.weaponCombo = QtGui.QComboBox()
        self.button = QtGui.QPushButton('Make Suggestion')
        self.button.setFixedSize(125,25)
        
        for suspect in gameplay.PEOPLE:
            self.suspectCombo.addItem(suspect)
        for weapon in gameplay.WEAPONS:
            self.weaponCombo.addItem(weapon)
            
        layout.addRow(self.label)
        layout.addRow(self.suspectCombo)
        layout.addRow(self.weaponCombo)
        layout.addRow(self.button)
        
        self.setLayout(layout)
 
class RevealDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(RevealDialog,self).__init__(parent)
        layout = QtGui.QFormLayout()
        self.player = ''
        
        self.label = QtGui.QLabel()
        self.cardList = QtGui.QListWidget()
        self.button = QtGui.QPushButton('Reveal')
        self.button.setFixedSize(75,25)
        
        layout.addRow(self.label)
        layout.addRow(self.cardList)
        layout.addRow(self.button)
        
        self.setLayout(layout)
 
def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
