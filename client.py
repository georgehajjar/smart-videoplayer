#Package imports
import socket
import threading
import yaml

#Module imports

#Global vars
videoLoaded = False
currentVideoID = ""
currentVideoPath = ""
cSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def recieve(sock, next):
    print("Connected to server: " + str(sock.getsockname()))
    connected = True
    while connected:
        try:
            data = sock.recv(32)
        except:
            print("Server " + str(sock.getsockname()) + " has disconnected")
            connected = False
            sock.close()
        else:
            data = data.decode("utf-8")
            if not data:
                print("Server " + str(sock.getsockname()) + " has disconnected")
                connected = False
                sock.close()
                break
            # print(data)
            next(sock, data)
    return

def controlDecode(sock, data):
    if data[:3] == "req":
        global videoLoaded, currentVideoID, currentVideoPath
        currentVideoID = data[3:6]
        currentVideoPath = data[6:]
        videoLoaded = True
    elif data[:3] == "act":
        handleAction(data[3:])
    return

#Method gets called when user requests video from list
def requestVideo(videoID):
    global videoLoaded
    #Send video id to control server
    cSock.send(str.encode("req" + str(videoID)))
    while not videoLoaded:
        #Wait for responce back
        pass
    videoLoaded = False
    return currentVideoPath

#Method gets called when user performs action on video
def sendAction(action, time):
    #Send action to control server for 2 reasons
        #To perform the action: action -> control server -> client
        #To save the action: action -> database
    cSock.send(str.encode("act" + str(action) + str(currentVideoID) + str(time)))

def handleAction(action):
    if action == "ply":
        print("User has pressed play")
    elif action == "pse":
        print("User has pressed pause")
    elif action == "ffw":
        print("User has fastforwarded")
    elif action == "rwd":
        print("User has rewound")
    else:
        print(action)

def setup():
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    #Client(s) to control server
    cHost = config["sockets"]["c2c"]["host"]
    cPort = config["sockets"]["c2c"]["port"]

    #Attempt connection to control server
    try:
        cSock.connect((cHost, cPort))
    except:
        #Error case if cannot establish connection
        print("Could not make a connection to the control server")

    #Create new thread for control server connection
    receiveThread = threading.Thread(target = recieve, args = (cSock, controlDecode))
    receiveThread.start()

setup()
