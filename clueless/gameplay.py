#!/usr/bin/python

from PyQt4 import QtGui, QtCore
import uuid
import random
import consts


class game():
    """
    Clue-Less game class that handles the main game logic.
    """
    id = ''
    players = {}
    deck = None
    caseFile = []
    turnOrder = []
    disproveOrder = []
    disproveList = []
    board = None

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.deck = carddeck()
        self.defaultOrder = ['Miss Scarlet', 'Colonel Mustard',
                             'Mrs. White', 'Mr. Green',
                             'Mrs. Peacock', 'Professor Plum']
        self.board = self.createGameBoard()

    def addPlayer(self, name, char):
        """
        Create a new player and add them to the game.
        Keyword Arguments:
        name -- string name of new player
        char -- string character identifier of new player
        """
        space = self.board[char+'Home']
        p = player(name, char, space)
        self.players[name] = p
        
    def createGameBoard(self):
        """
        Create the game board data structure and make connections for
        all rooms in the board.
        """
        board = {}
        rooms = {}
        hallways = {}
        homespaces = {}
        # Create all the rooms
        for r in consts.ROOMS:
            rooms[r] = room(r)
        # Create all the hallways
        for h in consts.HALLWAYS:
            hallways[h] = hallway(h)
        # Create all the homespaces
        for p in consts.SUSPECTS:
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
    
    def disproveSuggestion(self, suspect, weapon, room):
        """
        Search for a player who can disprove the suggestion that was made.
        Return player who can disprove.
        Keyword Arguments:
        suspect -- string identifier of suggested suspect
        weapon -- string identifier of suggested weapon
        room -- string identifier of suggested room
        """
        # Iterate through the disprove order
        for i in range(1,len(self.disproveOrder)):
            cards = self.disproveOrder[i].cards
            show = []
            if suspect in cards:
                show.append(cards[suspect])
            if room in cards:
                show.append(cards[room])
            if weapon in cards:
                show.append(cards[weapon])
            # If they have none of the suggested cards, move to the next person
            if len(show) == 0:
                continue
            else:
                self.disproveList = show
                return self.disproveOrder[i].name
        # If we fall through no one could disprove
        return None   
    
    def endTurn(self, name):
        """
        End player's turn.
        Keyword Arguments:
        name -- string name of player who ended their turn.
        """
        # Move player to end of turn list
        self.turnOrder.append(self.turnOrder.pop(0))
        # Update current player
        self.currentPlayer = self.turnOrder[0]
        
    def getDisproveList(self):
        """
        Return list of cards that were used for disproving suggestion.
        """
        return self.disproveList
        
    def getMoves(self):
        """
        Get all possible moves for current player and return moves as a list.
        """
        # Find all possible moves from current space
        conns = []
        for conn in self.currentPlayer.currentSpace.connections:
            if isinstance(conn, hallway):
                if not conn.occupied:
                    conns.append(conn)
            else:
                conns.append(conn)
                
        return conns
        
    def movePlayer(self, name, space):
        """
        Move player to specified space and return new space.
        Keyword Arguments:
        name -- string name of user to be moved.
        space -- string identifier of game board space.
        """
        player = self.players[name]
        oldSpace = player.currentSpace
        newSpace = self.board[space]
        # Update player's space 
        player.currentSpace = newSpace
        # If player moved to a hallway, set it occupied
        if isinstance(newSpace, hallway):
            newSpace.occupied = True
        # If player moved out of the hallway, set unoccupied
        if isinstance(oldSpace, hallway):
            oldSpace.occupied = False
            
        return newSpace
    
    def removePlayer(self, name):
        """
        Remove player from the game.
        Keyword Arguments:
        name -- string name of player who is being removed.
        """
        del self.players[name]
        
    def start(self):
        """
        Start the game.
        """
        # Choose winning scenario from the deck
        self.caseFile = self.deck.chooseCaseFile()
        # Shuffle
        self.deck.shuffleCards()
        # Deal remaining cards to players
        deal = self.deck.dealCards(len(self.players))
        for i in range(len(self.players.values())):
            self.players.values()[i].cards = deal.pop(i)
        # Determine order based on characters in game
        for char in self.defaultOrder:
            for player in self.players:
                if self.players[player].character == char:
                    self.turnOrder.append(self.players[player])

        self.currentPlayer = self.turnOrder[0]
        
        self.disproveOrder = self.turnOrder


class carddeck():
    """
    Clue-Less card deck holding all 21 Clue-Less game cards.
    """
    cards = []

    def __init__(self):
        self.suspects = [card(x) for x in consts.SUSPECTS]
        self.rooms = [card(x) for x in consts.ROOMS]
        self.weapons = [card(x) for x in consts.WEAPONS]
        self.cards = self.suspects + self.rooms + self.weapons

    def chooseCaseFile(self):
        """
        Choose three cards for the case file, one of each type.
        """
        caseFile = []
        # Randomly choose the winning cards
        caseFile.append(self.suspects[random.randint(0,len(consts.SUSPECTS)-1)])
        caseFile.append(self.rooms[random.randint(0, len(consts.ROOMS)-1)])
        caseFile.append(self.weapons[random.randint(0, len(consts.WEAPONS)-1)])
        # Remove the case file cards from the deck
        self.cards = [x for x in self.cards if x not in caseFile]

        return caseFile

    def dealCards(self, numPlayers):
        """
        Deal remaining cards to players.
        numPlayers -- number of players in the game as integer.
        """
        deal = {}
        # Create a dictionary of cards for each player
        for i in range(numPlayers):
            deal[i] = {}
        # Iterate through all cards giving players one card at a time
        j = 0
        for card in self.cards:
            deal[j][card.identifier] = card
            if j == len(deal)-1:
                j = 0
            else:
                j = j+1

        return deal
    
    def shuffleCards(self):
        """
        Shuffle the deck of cards.
        """
        random.shuffle(self.cards)
 

class card():
    """
    Clue-Less card type.
    """
    identifier = ''

    def __init__(self, cardId):
        self.identifier = cardId
        
        
class room():
    """
    Clue-Less room type.
    """
    identifier = ''
    connections = []
    numOccupants = 0

    def __init__(self, roomId):
        self.identifier = roomId


class hallway():
    """
    Clue-Less hallway type.
    """
    identifier = ''
    connections = []
    
    def __init__(self, hallId):
        self.identifier = hallId
        self.occupied = False


class player():
    """
    Clue-Less player type.
    """
    name = ''
    character = ''
    cards = {}
    currentSpace = None

    def __init__(self, name, char, space):
        self.name = name
        self.character = char
        self.currentSpace = space


class homespace():
    """
    Clue-Less space for each character's starting location.
    """
    identifier = ''
    connections = []

    def __init__(self, char):
        self.identifier = char