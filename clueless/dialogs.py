#!/usr/bin/python

from PyQt4 import QtGui
import consts

class AccusationDialog(QtGui.QDialog):
    """
    Custom dialog for making an accusation.
    """
    def __init__(self, parent=None):
        super(AccusationDialog, self).__init__(parent)
        self.setModal(True)
        # Create dialog widgets
        layout = QtGui.QFormLayout()  
        label = QtGui.QLabel('Select the items for your accusation:')
        self.suspectCombo = QtGui.QComboBox()
        self.roomCombo = QtGui.QComboBox()
        self.weaponCombo = QtGui.QComboBox()
        self.button = QtGui.QPushButton('Make Accusation')
        self.button.setFixedSize(125, 25)
        cancel = QtGui.QPushButton('Cancel')
        cancel.setFixedSize(75, 25)
        cancel.clicked.connect(self.handleCancel)
        # Fill combo-boxes
        for suspect in consts.SUSPECTS:
            self.suspectCombo.addItem(suspect)
        for room in consts.ROOMS:
            self.roomCombo.addItem(room)
        for weapon in consts.WEAPONS:
            self.weaponCombo.addItem(weapon)
        # Add all widgets to the layout and set layout
        layout.addRow(label)
        layout.addRow(self.suspectCombo)
        layout.addRow(self.roomCombo)
        layout.addRow(self.weaponCombo)
        layout.addRow(self.button, cancel)
        self.setLayout(layout)

    def closeEvent(self, event, valid=False):
        """
        Override closeEvent.
        Keyword Arguments:
        event -- QtGui.QCloseEvent().
        valid -- boolean value to determine whether or not to close widget.
        """
        if not valid:
            event.ignore()
        else:
            super(AccusationDialog, self).closeEvent(event)
            
    def handleCancel(self):
        self.closeEvent(QtGui.QCloseEvent(), valid=True)


class CharacterDialog(QtGui.QDialog):
    """
    Custom dialog for choosing a Clue-Less character.
    """
    def __init__(self, parent=None):
        super(CharacterDialog, self).__init__(parent)
        self.setModal(True)
        # Create dialog widgets
        layout = QtGui.QFormLayout()
        label = QtGui.QLabel('Please choose your character:')
        self.characterList = QtGui.QListWidget()
        self.button = QtGui.QPushButton('Pick')
        self.button.setFixedSize(65, 25)
        # Add all widgets to layout and set layout
        layout.addRow(label)
        layout.addRow(self.characterList)
        layout.addRow(self.button)  
        self.setLayout(layout)
        
    def closeEvent(self, event, valid=False):
        """
        Override closeEvent.
        Keyword Arguments:
        event -- QtGui.QCloseEvent().
        valid -- boolean value to determine whether or not to close widget.
        """
        if not valid:
            event.ignore()
        else:
            super(CharacterDialog, self).closeEvent(event)
 

class RevealDialog(QtGui.QDialog):
    """
    Custom dialog for choosing which card to reveal to another player.
    """
    def __init__(self, parent=None):
        super(RevealDialog, self).__init__(parent)
        self.setModal(True)
        # Create dialog widgets
        layout = QtGui.QFormLayout()
        self.player = ''
        self.label = QtGui.QLabel()
        self.cardList = QtGui.QListWidget()
        self.button = QtGui.QPushButton('Reveal')
        self.button.setFixedSize(75, 25)
        # Add all widget to layout and set layout
        layout.addRow(self.label)
        layout.addRow(self.cardList)
        layout.addRow(self.button)
        self.setLayout(layout)
        
    def closeEvent(self, event, valid=False):
        """
        Override closeEvent.
        Keyword Arguments:
        event -- QtGui.QCloseEvent().
        valid -- boolean value to determine whether or not to close widget.
        """
        if not valid:
            event.ignore()
        else:
            super(RevealDialog, self).closeEvent(event)
        
  
class SuggestionDialog(QtGui.QDialog):
    """
    Custom dialog for making a suggestion.
    """
    def __init__(self, parent=None):
        super(SuggestionDialog, self).__init__(parent)
        self.setModal(True)
        # Create dialog widgets
        layout = QtGui.QFormLayout()
        label = QtGui.QLabel('Select the items for your suggestion:')
        self.suspectCombo = QtGui.QComboBox()
        self.weaponCombo = QtGui.QComboBox()
        self.button = QtGui.QPushButton('Make Suggestion')
        self.button.setFixedSize(125, 25)
        # Fill combo-boxes
        for suspect in consts.SUSPECTS:
            self.suspectCombo.addItem(suspect)
        for weapon in consts.WEAPONS:
            self.weaponCombo.addItem(weapon)
        # Add all widgets to layout and set layout
        layout.addRow(label)
        layout.addRow(self.suspectCombo)
        layout.addRow(self.weaponCombo)
        layout.addRow(self.button)
        self.setLayout(layout)
        
    def closeEvent(self, event, valid=False):
        """
        Override closeEvent.
        Keyword Arguments:
        event -- QtGui.QCloseEvent().
        valid -- boolean value to determine whether or not to close widget.
        """
        if not valid:
            event.ignore()
        else:
            super(SuggestionDialog, self).closeEvent(event)
    

class UsernameDialog(QtGui.QDialog):
    """
    Custom dialog for getting username.
    """
    def __init__(self, parent=None):
        super(UsernameDialog, self).__init__(parent)
        self.setModal(True)
        # Create dialog widgets
        layout = QtGui.QFormLayout()
        label = QtGui.QLabel('Please enter your username:')
        self.edit = QtGui.QLineEdit(self)
        self.edit.setFocus()
        # Add all widgets to layout and set layout
        layout.addRow(label)
        layout.addRow(self.edit)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        """
        Override closeEvent.
        Keyword Arguments:
        event -- QtGui.QCloseEvent().
        """
        # Only close dialog if text has been entered
        if len(self.edit.text()) == 0:
            event.ignore()
        else:
            event.accept()
            
