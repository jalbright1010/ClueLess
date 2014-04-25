#!/usr/bin/python

import socket
import time
import sys
import thread
import cPickle as pickle
import sip
#import gameplay
import gameboard
import dialogs
import consts
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QMainWindow):
    """
    The MainWindow class is the GUI client for Clue-Less game play.
    """
    # Custom signals to handle messages coming from server
    receiveSignal = QtCore.pyqtSignal(str)
    usernameSignal = QtCore.pyqtSignal()
    characterSignal = QtCore.pyqtSignal(str)
    gameboardSignal = QtCore.pyqtSignal(str)
    turnSignal = QtCore.pyqtSignal(str)
    suggestionSignal = QtCore.pyqtSignal()
    cardSignal = QtCore.pyqtSignal(str)
    revealSignal = QtCore.pyqtSignal(str, str)
    falseAccusationSignal = QtCore.pyqtSignal()
    gameOverSignal = QtCore.pyqtSignal(str)
    winSignal = QtCore.pyqtSignal()
    cardShownSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.hasAccusation = True
        
        # Make a connection to the Clue-Less server
        #host = '69.255.109.89'
        #port = 40004
        host = '192.168.100.14'
        port = 4004
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
        self.falseAccusationSignal.connect(self.eliminateMoves)
        self.gameOverSignal.connect(self.gameOver)
        self.winSignal.connect(self.youWin)
        self.cardShownSignal.connect(self.showCard)

        # Create custom dialogs
        self.getUsername = dialogs.UsernameDialog(self)
        self.getUsername.edit.returnPressed.connect(self.handleUsername)
        self.getCharacter = dialogs.CharacterDialog(self)
        self.getCharacter.button.clicked.connect(self.handleCharacterChoice)
        self.getSuggestion = dialogs.SuggestionDialog(self)
        self.getSuggestion.button.clicked.connect(self.handleSuggestion)
        self.getReveal = dialogs.RevealDialog(self)
        self.getReveal.button.clicked.connect(self.handleRevealChoice)
        self.getAccusation = dialogs.AccusationDialog(self)
        self.getAccusation.button.clicked.connect(self.handleAccusationChoice)

        # Timer to alert user when it is their turn
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.handleTimer)
        self.timerState = False

        # Initialize the user interface
        self.initUI()
        
        # Create the main listening thread to receive messages from server
        self.createReceiveThread()
        
    def initUI(self):
        """
        Initialize the user interface.
        """
        self.setWindowTitle('Clue-Less')
        self.setStyleSheet('QMainWindow { background-color: rgb(0,120,0) }')
        self.initWidth = (QtGui.QDesktopWidget().availableGeometry().width() * .8)
        self.initHeight = (QtGui.QDesktopWidget().availableGeometry().height() * .9)
        self.resize(self.initWidth, self.initHeight)
        
        self.createMenuBar()
        
        self.centralWidget = QtGui.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.form = QtGui.QFormLayout()
              
        self.splitter = QtGui.QSplitter()
        
        self.cardGroup = QtGui.QGroupBox()
        self.cardGroup.setTitle('Cards')
        self.notepad = self.createNotepad()

        self.splitter.addWidget(self.cardGroup)
        self.splitter.addWidget(self.notepad)

        self.centralWidget.form.addRow(self.createBoard(), self.splitter)
        self.splitter.hide()
        self.centralWidget.form.addRow(self.createGameLogArea(), self.createMoveGroup())
        
        self.centralWidget.setLayout(self.centralWidget.form)


    #####################################
    ###         Slots                 ###
    #####################################
    @QtCore.pyqtSlot(str)
    def appendMessage(self, message):
        """
        Appends message to the message log area when received from server.
        Keyword Arguments:
        message -- string message received from server
        """
        self.messageWindow.append(message)
        self.messageWindow.moveCursor(QtGui.QTextCursor.End)
     
    # Creates the card images to be displayed   
    @QtCore.pyqtSlot(str)
    def createCards(self, pickled):
        """
        Creates card images to be displayed and adds them to the card group. 
        Keyword Arguments:
        pickled -- pickled list of card identifiers received from server
        """
        cards = pickle.loads(str(pickled))
        layout = QtGui.QFormLayout()
        row1 = QtGui.QHBoxLayout()
        row2 = QtGui.QHBoxLayout()
        row3 = QtGui.QHBoxLayout()
        row4 = QtGui.QHBoxLayout()
        for card in cards[:3]:
            label = QtGui.QLabel()
            pixmap = QtGui.QPixmap('images/' + card + '.jpg')
            label.setPixmap(pixmap.scaled(self.width()/12, self.width()/8))
            row1.addWidget(label)
            row2.addWidget(QtGui.QLabel(card))
        for card in cards[3:6]:
            label = QtGui.QLabel()
            pixmap = QtGui.QPixmap('images/' + card + '.jpg')
            label.setPixmap(pixmap.scaled(self.width()/12, self.width()/8))
            row3.addWidget(label)
            row4.addWidget(QtGui.QLabel(card))
        layout.addRow(row1)
        layout.addRow(row2)
        layout.addRow(row3)
        layout.addRow(row4)
        self.cardGroup.setLayout(layout)
        self.splitter.show()
    
    @QtCore.pyqtSlot(str)
    def createMoves(self, pickled):
        """
        Creates the buttons for all possible moves.
        Notifies user that it is their turn by launching QMessageBox.
        Keyword Arguments:
        pickled -- pickled list of gameboard space identifiers from server.
        """
        moves = pickle.loads(str(pickled))
        layout = QtGui.QFormLayout()
        
        # Create buttons for all possible moves received
        for space in moves:
            if '-' in space:
                label = QtGui.QLabel('Move to %s Hallway...' % space)
            else:
                label = QtGui.QLabel('Move to %s...' % space)
            button = QtGui.QPushButton('Move')
            button.clicked.connect(self.handleMoveChoice(space))
            layout.addRow(label, button)
        
        # Create accusation button if user has that ability
        if self.hasAccusation:
            accButton = QtGui.QPushButton('Make Accusation')
            accButton.clicked.connect(self.handleAccusation)
            layout.addRow(accButton)

        # Remove all previous buttons and set new layout
        for i in reversed(range(self.moveGroup.layout().count())):
            sip.delete(self.moveGroup.layout().itemAt(i).widget())
        sip.delete(self.moveGroup.layout())
        self.moveGroup.setLayout(layout)

        # Send popup notification
        if not self.isActiveWindow():
            self.timer.start()
        notify = QtGui.QMessageBox.information(self, 'Your Turn',
                                               'It is now your turn!')
     
    @QtCore.pyqtSlot()      
    def eliminateMoves(self):
        """
        Notifies user that they have made an incorrect accusation.
        """
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel('You can no longer move.'))
        for i in reversed(range(self.moveGroup.layout().count())):
            sip.delete(self.moveGroup.layout().itemAt(i).widget())
        sip.delete(self.moveGroup.layout())
        self.moveGroup.setLayout(layout) 
    
    @QtCore.pyqtSlot(str)  
    def gameOver(self, name):
        """
        Notifies user that the game is over.
        Keyword Arguments:
        name -- string identifier of player who won the game.
        """
        over = QtGui.QMessageBox.information(self, 'Game Over', 'Game Over! %s wins!' % name,
                                             QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
    
    def handleTimer(self):
        """
        Alerts user that it is their turn by changing title of window.
        """
        if self.isActiveWindow():
            self.timer.stop()
            self.timerState = False
        
        if self.timerState:
            self.setWindowTitle('Your turn!')
            self.timerState = False
        else:
            self.setWindowTitle('Clue-Less')
            self.timerState = True
    
    @QtCore.pyqtSlot(str)
    def showCard(self, message):
        """
        Informs user of what card they have been shown by a fellow player.
        Keyword Arguments:
        message -- string containing pertinent information.
        """
        shownCard = QtGui.QMessageBox.information(self, 'Card Revealed',
                                                  message)
    
    @QtCore.pyqtSlot(str)
    def showCharacterDialog(self, used):
        """
        Shows the custom dialog box for choosing a character.
        Keyword Arguments:
        used -- pickled list of unavailable character identifiers.
        """
        unavailable = pickle.loads(str(used))
        for character in consts.SUSPECTS:
            if character not in unavailable:
                self.getCharacter.characterList.addItem(character)
        self.getCharacter.characterList.setCurrentRow(0)
        self.getCharacter.show()
       
    @QtCore.pyqtSlot(str, str)
    def showRevealDialog(self, pickled, name):
        """
        Shows the custom dialog box for revealing a card.
        Keyword Arguments:
        pickled -- pickled list of card identifiers to choose from.
        name -- string identifier of player whom you are revealing to.
        """
        cards = pickle.loads(str(pickled))
        self.getReveal.player = name
        self.getReveal.label.setText('Choose which card to reveal to %s:' % name)
        self.getReveal.cardList.clear()
        for card in cards:
            self.getReveal.cardList.addItem(card)
        self.getReveal.cardList.setCurrentRow(0)
        self.getReveal.show()
        
    @QtCore.pyqtSlot()
    def showSuggestionDialog(self):
        """
        Shows the custom dialog box for making a suggestion.
        """
        self.getSuggestion.show()
        
    @QtCore.pyqtSlot()
    def showUsernameDialog(self):
        """
        Shows the custom dialog box for entering username.
        """
        self.getUsername.show()
        
    @QtCore.pyqtSlot(str)
    def updateGameboard(self, pickled):
        """
        Redraw the game board display.
        Keyword Arguments:
        pickled -- pickled dictionary of player locations
        """
        self.gameboard.players = pickle.loads(str(pickled))
        self.gameboard.update()
        
    @QtCore.pyqtSlot()
    def youWin(self):
        """
        Notifies user when they have won the game.
        """
        win = QtGui.QMessageBox.information(self, 'Congratulations!', 
                                            'Congratulations! You Win!',
                                            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        
        
    #####################################
    ###      Slot Handlers            ###
    #####################################
    def handleAccusationChoice(self):
        """
        Send the accusation selections to the server as a pickled list of
        string identifiers.
        """
        # Get accusation selections from dialog box
        accusation = [self.getAccusation.suspectCombo.currentText(),
                      self.getAccusation.weaponCombo.currentText(),
                      self.getAccusation.roomCombo.currentText()]
        # Send pickled list of selections to server
        self.connection.send(self.encrypt('function::makingAccusation:' + 
                             pickle.dumps(accusation)))
        self.getAccusation.closeEvent(QtGui.QCloseEvent(), valid=True)
        # Only get one accusation per game
        self.hasAccusation = False
        
    def handleCharacterChoice(self):
        """
        Send the character selection to the server as a string identifier.
        """
        # Get character selection from dialog box
        self.character = str(self.getCharacter.characterList.currentItem().text())
        # Request to join game as chosen character
        self.connection.send(self.encrypt('function::joinGame:' + self.character))
        self.getCharacter.closeEvent(QtGui.QCloseEvent(), valid=True)
        self.inputWindow.setReadOnly(False)
        
    def handleEndTurn(self):
        """
        Send the signal as a string to the server to end user's turn.
        """
        # Send signal to end turn to server
        self.connection.send(self.encrypt('function::endTurn'))
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel('Awaiting your next turn...'))
        # Remove all move buttons
        for i in reversed(range(self.moveGroup.layout().count())):
            sip.delete(self.moveGroup.layout().itemAt(i).widget())
        sip.delete(self.moveGroup.layout())
        # Set new layout
        self.moveGroup.setLayout(layout)
        
    def handleMoveChoice(self, space):
        """ 
        Send the selected move to the server as a string identifier of
        selected space.
        Keyword Arguments:
        space -- string identifier of selected space
        """
        def clicked():
            # Send signal to move player to desired space
            self.connection.send(self.encrypt('function::movePlayer:' + space))
            # Update user's gameboard with move
            self.gameboard.players[self.character] = space
            self.gameboard.update()
            # Create end turn and accusation moves
            layout = QtGui.QFormLayout()
            button = QtGui.QPushButton('End Turn')
            button.clicked.connect(self.handleEndTurn)
            layout.addRow(button)
            if self.hasAccusation:
                accButton = QtGui.QPushButton('Make Accusation')
                accButton.clicked.connect(self.handleAccusation)
                layout.addRow(accButton)
            # Remove all previous move buttons
            for i in reversed(range(self.moveGroup.layout().count())):
                sip.delete(self.moveGroup.layout().itemAt(i).widget())
            sip.delete(self.moveGroup.layout())
            # Set new layout
            self.moveGroup.setLayout(layout)
        return clicked
    
    def handleRevealChoice(self):
        """
        Send the card that the user has chosen to reveal to the server
        as a string identifier.
        """
        # Get the selected card from dialog box
        choice = str(self.getReveal.cardList.currentItem().text())
        # Get the name of the person user is revealing to
        name = self.getReveal.player
        # Send signal to server to reveal chosen card
        self.connection.send(self.encrypt('function::revealCard:%s:%s' % (choice, name)))
        self.getReveal.closeEvent(QtGui.QCloseEvent(), valid=True)
    
    def handleSuggestion(self):
        """
        Send the suggestion selections to the server as a pickled list of
        string identifiers.
        """
        # Get suggestion selections from dialog box
        suggestion = [self.getSuggestion.suspectCombo.currentText(),
                      self.getSuggestion.weaponCombo.currentText()]
        # Send signal to server to make suggestion
        self.connection.send(self.encrypt('function::makingSuggestion:' + 
                             pickle.dumps(suggestion)))
        self.getSuggestion.closeEvent(QtGui.QCloseEvent(), valid=True)
        
    def handleUsername(self):
        """
        Send the user entered username to the server as string.
        """
        # Get username from dialog box and send it to server
        self.connection.send(self.encrypt(str(self.getUsername.edit.text())))
        self.getUsername.close()
    

    #####################################
    ###        GUI Functions          ###
    #####################################
    def createBoard(self):
        """
        Create the game board display and return this instance of the board.
        """
        self.gameboard = gameboard.board(self.width() / 2, self.height() / 2)
        return self.gameboard
    
    def createGameLogArea(self):
        """
        Create the message log area group and return this group.
        """
        group = QtGui.QGroupBox()
        form = QtGui.QFormLayout()

        # Create message window, initially read only
        self.messageWindow = QtGui.QTextEdit(group)
        self.messageWindow.setFixedWidth(self.width() / 2)
        self.messageWindow.setFixedHeight(self.height() / 4)
        self.messageWindow.setReadOnly(True)

        # Create message input window, initially read only
        self.inputWindow = QtGui.QLineEdit(group)
        self.inputWindow.setFixedWidth(self.width() / 2)
        self.inputWindow.setReadOnly(True)
        self.inputWindow.returnPressed.connect(self.sendMessage)
        
        form.addRow(self.messageWindow)
        form.addRow(self.inputWindow)
        
        group.setLayout(form)

        return group
    
    def createMenuBar(self):
        """
        Create the MainWindow menuBar with File menu containing Start,
        Ready, and Exit actions.
        """
        menubar = self.menuBar()
        mainMenu = menubar.addMenu('File')
        # Create start action
        self.startAction = QtGui.QAction('Start Game', self)
        self.startAction.setShortcut('Ctrl+S')
        self.startAction.triggered.connect(self.sendStartSignal)
        mainMenu.addAction(self.startAction)
        # Create ready action
        self.readyAction = QtGui.QAction('Ready to Start', self)
        self.readyAction.setShortcut('Ctrl+R')
        self.readyAction.triggered.connect(self.sendReadySignal)
        mainMenu.addAction(self.readyAction)
        # Create exit action
        q = QtGui.QAction('Exit', self)
        q.setShortcut('Ctrl+Q')
        q.triggered.connect(self.close)
        mainMenu.addAction(q)
        
    def createMoveGroup(self):
        """
        Create the group that move buttons will be added to and return
        this group.
        """
        self.moveGroup = QtGui.QGroupBox()
        form = QtGui.QFormLayout()
        form.addRow(QtGui.QLabel('Waiting for your turn...'))
        self.moveGroup.setLayout(form)
        return self.moveGroup
        
    def createNotepad(self):
        """
        Create Clue-Less notepad for users to keep track of which cards they
        know about as a group of Suspect, Room, and Weapon groups containing
        check-boxes for each game card and return the main group.
        """
        group = QtGui.QGroupBox()
        group.setTitle('Notepad')
        layout = QtGui.QFormLayout()
        # Create suspect group and check-boxes
        suspectGroup = QtGui.QGroupBox()
        suspectGroup.setTitle('Suspects')
        suspectLayout = QtGui.QGridLayout()
        for i in range(0, 3):
            suspectLayout.addWidget(QtGui.QCheckBox(consts.SUSPECTS[i]), 0, i)
        for i in range(3, 6):
            suspectLayout.addWidget(QtGui.QCheckBox(consts.SUSPECTS[i]), 1, i - 3)
        suspectGroup.setLayout(suspectLayout)
        # Create room group and check-boxes
        roomGroup = QtGui.QGroupBox()
        roomGroup.setTitle('Rooms')
        roomLayout = QtGui.QGridLayout()
        for i in range(0, 3):
            roomLayout.addWidget(QtGui.QCheckBox(consts.ROOMS[i]), 0, i)
        for i in range(3, 6):
            roomLayout.addWidget(QtGui.QCheckBox(consts.ROOMS[i]), 1, i - 3)
        for i in range(6, 9):
            roomLayout.addWidget(QtGui.QCheckBox(consts.ROOMS[i]), 2, i - 6)
        roomGroup.setLayout(roomLayout)
        # Create weapon group and check-boxes
        weaponGroup = QtGui.QGroupBox()
        weaponGroup.setTitle('Weapons')
        weaponLayout = QtGui.QGridLayout()
        for i in range(0, 3):
            weaponLayout.addWidget(QtGui.QCheckBox(consts.WEAPONS[i]), 0, i)
        for i in range(3, 6):
            weaponLayout.addWidget(QtGui.QCheckBox(consts.WEAPONS[i]), 1, i - 3)
        weaponGroup.setLayout(weaponLayout)
        # Add all groups to main group and set layout
        layout.addRow(suspectGroup)
        layout.addRow(roomGroup)
        layout.addRow(weaponGroup)
        group.setLayout(layout)
        
        return group
    
    def handleAccusation(self):
        """
        Display custom accusation dialog box.
        """
        self.getAccusation.show()


    ##################################
    ###  Client Socket Functions   ###
    ################################## 
    def connectToServer(self, host, port):
        """
        Create a socket connection with the Clue-Less server.
        Keyword Arguments:
        host -- server ip address as a string.
        port -- open server port as an integer.
        """
        # Create client socket instance
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Attempt to connect to Clue-Less server
        try:
            self.connection.connect((host, port))
        except socket.error:
            print 'Could not connect to server'
            sys.exit()

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
      
    def sendReadySignal(self):
        """
        Notify server that the user is ready to play.
        """
        self.connection.send(self.encrypt('function::ready'))
        self.readyAction.setEnabled(False)
            
    def sendStartSignal(self):
        """
        Notify server that the user has started the game.
        """
        self.connection.send(self.encrypt('function::start'))
        self.startAction.setEnabled(False) 

    def sendMessage(self):
        """
        Send a user entered message from message input window.
        """
        self.connection.send(self.encrypt('message::' + str(self.inputWindow.text())))
        self.inputWindow.clear()

    
    ##################################
    ###    Listening Thread        ###
    ##################################
    # Creates thread to listen for messages from server    
    def createReceiveThread(self):
        """
        Create receive thread with function to listen for messages from server.
        """
        def threaded():
            try:
                while True:
                    r = self.connection.recv(1024).strip()
                    s = self.decrypt(r)
                    if '::' in s:
                        splt = s.split('::')
                        if splt[0] == 'message':
                            self.receiveSignal.emit(str(splt[1]))
                        elif splt[0] == 'function':
                            splt2 = splt[1].split(':')
                            if splt2[0] == 'updateGameboard':
                                self.gameboardSignal.emit(splt2[1])
                            elif splt2[0] == 'usedChars':
                                self.characterSignal.emit(splt2[1])
                            elif splt2[0] == 'yourTurn':
                                self.turnSignal.emit(splt2[1])
                            elif splt2[0] == 'cards':
                                self.cardSignal.emit(splt2[1])
                            elif splt2[0] == 'revealCard':
                                self.revealSignal.emit(splt2[1], splt2[2])
                            elif splt2[0] == 'gameOver':
                                self.gameOverSignal.emit(splt2[1])
                            elif splt2[0] == 'username':
                                self.usernameSignal.emit()
                            elif splt2[0] == 'suggestion':
                                self.suggestionSignal.emit()
                            elif splt2[0] == 'falseAccusation':
                                self.falseAccusationSignal.emit()
                            elif splt2[0] == 'winner':
                                self.winSignal.emit()
                            elif splt2[0] == 'shown':
                                self.cardShownSignal.emit(splt2[1])
            except (SystemExit, KeyboardInterrupt):
                sys.exit()
        self.receiveThread = thread.start_new_thread(threaded, ())    

    
def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.raise_()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
