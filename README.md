ClueLess
========

This is a python implementation of Clue-Less, a simplified version of the popular board game, Clue®. This project is for Foundations of Software Engineering at JHU. 

In Clue-Less there are the same nine rooms, six weapons, and six people as in the board game. The main simplification is that navigation of the game board. The rules are essentially the asme except for the movement between the rooms.

** Navigation of the Game Board **
* The rooms are laid out in a 3x3 grid with a hallway separating each pair of adjacent rooms.
* Each hallway only holds one person. If someone is currently in a hallway, you may not move there.
* When it is your turn, you do not need to roll a die.
* Your options for moving are limited to the following:
	* If you are in a room. you may do one of the following:
		* Move through one of the doors to the hallway (if it is not blocked).
		* Take a secret pasage to a diagonally opposite room (if there is one) and make a suggestion.
		* If you were moved to the room by another player making a suggestion, you may, if you wish, stay in that room and make a suggestion. Otherwise you may move through a doorway or take a secret passage as described above.
	* If you are in a hallway, you must:
		* Move to one of the two rooms accessible from that hallway and make a suggestion.
* If all of the exits are blocked (i.e., there are people in all of the hallways) and you are not in one of the corner rooms (with a secret passage), and you were not moved to the room by another player making a suggestion, you lose your turn (except for possibly making an accusation).
* Your first move must be to the hallway that is adjacent to your home square.
* Whenever a suggestion is made, the room must be the room that one making the suggestion is currently in. The suspect in the suggestion is moved to the room in the suggestion.
* You may make an accusation at any time during your turn.

** Requirements of the Game **
* Each player should access the game from a separate computer, with a graphical user interface.
* The game rules are the same as in regular Clue® except for the navigation (described above).
* Each time the game state changes (a person is moved, a suggestion is made, a player disproves a suggestion, or a player is unable to disprove a suggestion) all players should be notified.

You can find the official Clue® game rules by downloading the following pdf file. Some of the rules may have changed in more recent editions of the game, however we will be following the original rules:

[http://www.hasbro.com/common/instruct/clueins.pdf](http://www.hasbro.com/common/instruct/clueins.pdf)

The official Hasbro Clue® game website is:

[http://www.hasbro.com/games/en_US/clue/](http://www.hasbro.com/games/en_US/clue/)

