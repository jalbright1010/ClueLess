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

    def __init__(self):
        super(MainWindow, self).__init__()
        host = '127.0.0.1'
        port = 4004
        self.connectToServer(host, port)
	self.receiveSignal.connect(self.appendMessage)
	self.usernameSignal.connect(self.askForUsername)
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
	self.centralWidget.form.addRow(self.createMessageWindow())
	self.centralWidget.form.addRow(self.createInputWindow())
        self.centralWidget.setLayout(self.centralWidget.form)

    def createMenuBar(self):
        menubar = self.menuBar()
        mainMenu = menubar.addMenu('File')
        create = QtGui.QAction('Create Game', self)
        create.setShortcut('Ctrl+G')
        create.triggered.connect(self.createGame)
        mainMenu.addAction(create)
        join = QtGui.QAction('Join Game', self)
        join.setShortcut('Ctrl+J')
        #join.triggered.connect(self.sendGameRequest)
        mainMenu.addAction(join)
        quit = QtGui.QAction('Exit', self)
        quit.setShortcut('Ctrl+Q')
        quit.triggered.connect(self.close)
        mainMenu.addAction(quit)

    def createMessageWindow(self):
	self.messageWindow = QtGui.QTextEdit()
	self.messageWindow.setFixedWidth(self.width()/2)
        self.messageWindow.setFixedHeight(self.height()/4)
	self.messageWindow.setReadOnly(True)
	return self.messageWindow

    def createInputWindow(self):
	self.inputWindow = QtGui.QLineEdit()
	self.inputWindow.setFixedWidth(self.width()/2)
	self.inputWindow.setReadOnly(True)
	self.inputWindow.returnPressed.connect(self.sendMessage)
	return self.inputWindow

    def sendMessage(self):
	self.client.send('message::'+str(self.inputWindow.text()))
	self.inputWindow.clear()

    def createBoard(self):
        self.gameboard = gameplay.board(self.width()/2, self.height()/2)
        return self.gameboard

    def createReceiveThread(self):
	def threaded():
            try:
                while True:
                    s = self.client.recv(1024).strip()
                    if s == 'username':
                        self.usernameSignal.emit()
                    else:
                        self.receiveSignal.emit(str(s))
            except (SystemExit, KeyboardInterrupt):
                sys.exit()
        self.receiveThread = thread.start_new_thread(threaded, ())    

    @QtCore.pyqtSlot()
    def createGame(self):
        self.client.send('function::createNewGame')

def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
