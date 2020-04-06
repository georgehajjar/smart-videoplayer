#Package imports
import sys
import socket
import threading
import yaml
import json

#Module imports
sys.path.insert(0, 'database')
import mongoConfig
from mongoModels import Video, Behaviour
import mlPredictor

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
                data = self.socket.recv(1024)
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
                print(data)
                clientDecode(self.socket, data)
        return

def clientDecode(sock, data):
    recievedData = json.loads(data)
    if recievedData['type'] == "req": #Recieve a request to load video.
        #Find video in database
        video = mongoConfig.findVideoById(recievedData['videoID'])
        #Generate prediction data everytime a user requests a video. This will update old values
        mlPredictor.generateGraphData(str(video.genre))
        #Send path to client
        sendData = {
            'type': 'req',
            'videoID': str(video.videoID),
            'title': str(video.title)
        }
        json_data = json.dumps(sendData).encode('utf-8')
        sock.sendall(json_data)
        #Get video genre and send the corresponding predictions
        sendData = {
            'type': 'prd',
            'prediction': mongoConfig.findPredictionByGenre(str(mongoConfig.findVideoById(str(video.videoID)).genre))
        }
        json_data = json.dumps(sendData).encode('utf-8')
        sock.sendall(json_data)
    elif recievedData['type'] == "act": #Recieve an action performed on video.
        #Save action to database.
        updateActions(recievedData['action'], recievedData['videoID'], recievedData['time'])
        #Send action back to client to perform.
        sendData = {
            'type': 'act',
            'action': recievedData['action']
        }
        json_data = json.dumps(sendData).encode('utf-8')
        sock.sendall(json_data)
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
