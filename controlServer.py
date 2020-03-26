#Package imports
import sys
import socket
import threading
import yaml

#Module imports
sys.path.insert(0, 'database')
import mongoConfig
from mongoModels import Video, Behaviour

clientConnections = []
total_connections = 0

#Client class, new instance created for each connected client
#Each instance has the socket and address that is associated with items
#Along with an assigned ID
def newClientConnection(socket):
    while True:
        sock, address = socket.accept()
        global total_connections
        clientConnections.append(Client(sock, address, total_connections, True))
        clientConnections[len(clientConnections) - 1].start()
        total_connections += 1
        print("Total Connections " + str(total_connections))

class Client(threading.Thread):
    def __init__(self, socket, address, id, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.signal = signal

    def run(self):
        global total_connections
        while self.signal:
            try:
                data = self.socket.recv(32)
            except:
                print("Client " + str(self.address) + " has disconnected")
                self.signal = False
                self.socket.close()
                clientConnections.remove(self)
                total_connections -= 1
            else:
                data = data.decode("utf-8")
                if not data:
                    print("Client " + str(self.address) + " has disconnected")
                    self.signal = False
                    self.socket.close()
                    clientConnections.remove(self)
                    total_connections -= 1
                    break
                # print(data)
                clientDecode(self.socket, data)
        return

def clientDecode(sock, data):
    if data[:3] == "req": #Recieve a request to load video.
        #Find video in database
        video = mongoConfig.findVideoById(data[3:])
        #Send path to client
        sock.send(str.encode("req" + str(video.videoID) + str(video.title)))
    elif data[:3] == "act": #Recieve an action performed on video.
        #Save action to database.
        updateActions(data[3:6], data[6:9], data[9:])
        #Send action back to client to perform.
        sock.send(str.encode("act" + str(data[3:6])))
    return

# Append time to specific action in videoBehaviour database
def updateActions(action, videoID, time):
    if action == "ply":
        mongoConfig.addPlayBehaviour(Behaviour(videoID=str(videoID), played=[int(time)]))
    elif action == "pse":
        mongoConfig.addPauseBehaviour(Behaviour(videoID=str(videoID), paused=[int(time)]))
    elif action == "ffw":
        mongoConfig.addFFBehaviour(Behaviour(videoID=str(videoID), fastforwarded=[int(time)]))
    elif action == "rwd":
        mongoConfig.addRWBehaviour(Behaviour(videoID=str(videoID), rewound=[int(time)]))
    else:
        print("Error with updateActions")
    return

def setup():
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    #Control server to client(s)
    cHost = config["sockets"]["c2c"]["host"]
    cPort = config["sockets"]["c2c"]["port"]

    #Create new socket for client(s) to connect to
    cSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cSock.bind((cHost, cPort))
    cSock.listen(5)
    print("Control server to client communcation socket on " + cHost + ":" + str(cPort))

    #Create new thread for client connections
    newClientConnectionThread = threading.Thread(target = newClientConnection, args = (cSock,))
    newClientConnectionThread.start()

setup()
