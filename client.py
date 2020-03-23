#Package imports
import socket
import threading
import yaml

#Module imports


#Global vars
currentVideoID = "001"
cSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def recieve(sock, name, next, control):
    if control:
        sock, address = sock.accept()
    print("Connected to " + str(name) + str(sock.getsockname()))
    connected = True

    while connected:
        try:
            data = sock.recv(32)
        except:
            print(str(name) + str(sock.getsockname()) + " has disconnected")
            connected = False
            sock.close()
        else:
            data = data.decode("utf-8")
            if not data:
                print(str(name) + str(sock.getsockname()) + " has disconnected")
                connected = False
                sock.close()
                break
            next(sock, data)
    return

#Method gets called when user requests video from list
def requestVideo(videoID):
    currentVideoID = videoID
    #Send video id to control server
    cSock.send(str.encode("req" + str(videoID)))

#Method gets called when user performs action on video
def sendAction(action, time):
    videoID = str(currentVideoID)
    action = str(action) #action types (3 chars long): ply, pse, ffw, rwd
    time = str(time)
    #Send action to control server for 2 reasons
        #To perform the action: action -> streaming server -> client
        #To save the action: action -> database
    cSock.send(str.encode("act" + str(action) + str(videoID) + str(time)))

def controlDecode(sock, data):
    print(str(sock) + "sends : " + str(data))
    return

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
    receiveThread = threading.Thread(target = recieve, args = (cSock, "control server", controlDecode, False))
    receiveThread.start()

setup()
