#!/usr/bin/python

import socket
import thread
import time
import sys
import cPickle as pickle
import uuid
import gameplay 

class server():
    users = {}
    sock = None
    activeGames = []
    availableGames = []
    
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind((str(host), int(port)))
        self.sock.listen(1)
        print "Listening on %s" % ("%s:%s" % self.sock.getsockname())
        
    def accept(self):
        return self.sock.accept()

    def acceptConnection(self, conn):
        def threaded():
            while True:
                conn.send('username')
                try:
                    name = conn.recv(1024).strip()
                except socket.error:
                    continue
                if name in self.users:
                    conn.send('Username already in use.\n')
                elif name:
                    conn.setblocking(False)
                    self.users[name] = conn
                    self.broadcastMessageToAll('+++ %s arrived +++' % name)
                    break
        self.acceptThread = thread.start_new_thread(threaded, ())

    def broadcastMessageToAll(self, message):
        # Send a message to all users from the given name.
        print message
        for name, conn in self.users.items():
            try:
                conn.send(message + '\n')
            except:
                pass

    def broadcastMessageToUser(self, name, message):
        print message
        try:
            self.users[name].send(message + '\n')
        except:
            pass

    def createNewGame(self):
        g = gameplay.game()
        self.availableGames.append(g)
        self.broadcastMessageToAll('Game created with id '+g.id)

def main():
    s = server('127.0.0.1', 4004)

    while True:
        try:
            # Accept new connections
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
                            pass
                        elif splt2[0] == 'requestingGames':
                            pass
                    elif splt[0] == 'message':
                        s.broadcastMessageToAll('%s> %s' % (name, splt[1]))
                else:
                    if not message:
                        # Empty string is given on disconnect
                        del s.users[name]
                        s.broadcastMessageToAll('--- %s leaves ---' % name)
            time.sleep(.1)
        except (SystemExit, KeyboardInterrupt):
            break

if __name__ == '__main__':
    main()