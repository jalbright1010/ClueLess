#!/usr/bin/python

import time
import socket
import server

def main():
    #s = server('192.168.100.14', 4004)
    s = server.server('10.0.1.10', 4004)
    
    while True:
        try:
            # Accept new connections
            if s.acceptingConnections:
                while True:
                    try:
                        conn, addr = s.accept()
                    except:
                        break
                    s.acceptConnection(conn)

            # Read from connections
            for name, conn in s.users.items():
                try:
                    message = conn.recv(1024).strip()
                except socket.error:
                    continue
                if '::' in message:
                    splt = message.split('::')
                    if splt[0] == 'function':
                        splt2 = splt[1].split(':')
                        if splt2[0] == 'createNewGame':
                            s.createNewGame()
                        elif splt2[0] == 'joinGame':
                            s.joinGame(name, splt2[1])
                        elif splt2[0] == 'ready':
                            s.broadcastMessageToAll(0, '%s is ready to start!' % name)
                            s.playersReady.append(name)
                        elif splt2[0] == 'start':
                            s.startGame(name)
                        elif splt2[0] == 'movePlayer':
                            s.movePlayer(name,splt2[1])
                        elif splt2[0] == 'endTurn':
                            s.endTurn(name)
                        elif splt2[0] == 'makingSuggestion':
                            s.makeSuggestion(name,splt2[1])
                        elif splt2[0] == 'revealCard':
                            s.revealCard(name,splt2[1],splt2[2])
                        elif splt2[0] == 'makingAccusation':
                            s.handleAccusation(name,splt2[1])
                    elif splt[0] == 'message':
                        s.broadcastMessageToAll(0, '%s> %s' % (name, splt[1]))
                else:
                    if not message:
                        # Empty string is given on disconnect
                        del s.users[name]
                        if s.game:
                            if name in s.game.players:
                                del s.game.players[name]
                        s.broadcastMessageToAll(0, '--- %s leaves ---' % name)
            time.sleep(.1)
        except (SystemExit, KeyboardInterrupt):
            break

if __name__ == '__main__':
    main()
