#Package imports
import socket
import threading
import yaml
import wx
import wx.media
import os
import json

#Global vars

#Denotes whether the client is connected to the server. If the predictor determines that a user will take action, this is set to True
connectedToServer = True

videoLoaded = False
actionHandled = False
currentVideoID = ""
currentVideoPath = ""
predictionArray = []
cSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class StaticText(wx.StaticText):
    def SetLabel(self, label):
        if label != self.GetLabel():
            wx.StaticText.SetLabel(self, label)

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

        try:
            self.mc = wx.media.MediaCtrl()
            ok = self.mc.Create(self, style=wx.SIMPLE_BORDER)
            if not ok:
                raise NotImplementedError
        except NotImplementedError:
            self.Destroy()
            raise

        self.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)

        play = wx.Button(self, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.OnPlay, play)
        self.playBtn = play

        pause = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.OnPause, pause)
        self.pauseBtn = pause

        forward = wx.Button(self, -1, "+5 Sec")
        self.Bind(wx.EVT_BUTTON, self.OnForward, forward)

        backward = wx.Button(self, -1, "-5 Sec")
        self.Bind(wx.EVT_BUTTON, self.OnBackward, backward)

        load1 = wx.Button(self, -1, "Load Video 1")
        self.Bind(wx.EVT_BUTTON, lambda event: self.requestVideo(event, "001"), load1)

        load2 = wx.Button(self, -1, "Load Video 2")
        self.Bind(wx.EVT_BUTTON, lambda event: self.requestVideo(event, "002"), load2)

        load3 = wx.Button(self, -1, "Load Video 3")
        self.Bind(wx.EVT_BUTTON, lambda event: self.requestVideo(event, "003"), load3)

        slider = wx.Slider(self, -1, 0, 0, 10)
        self.slider = slider
        slider.SetMinSize((150, -1))
        self.Bind(wx.EVT_SLIDER, self.OnSeek, slider)

        self.st_len  = StaticText(self, -1, size=(100,-1))
        self.st_pos  = StaticText(self, -1, size=(100,-1))
        self.st_status = StaticText(self, -1, size=(100,-1))

        # setup the layout
        sizer = wx.GridBagSizer(5,5)
        sizer.Add(self.mc, (1,1), span=(5,1), flag=wx.EXPAND)
        sizer.Add(self.st_pos, (1, 2))
        sizer.Add(play, (2,2))
        sizer.Add(pause, (3,2))
        sizer.Add(forward, (4,2))
        sizer.Add(backward, (5,2))
        sizer.Add(self.st_status, (7,2))
        sizer.Add(load1, (2,3))
        sizer.Add(load2, (3,3))
        sizer.Add(load3, (4,3))
        sizer.Add(slider, (6,1), flag=wx.EXPAND)
        sizer.Add(self.st_len, (6, 2))
        self.SetSizer(sizer)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(100)

    def requestVideo(self, evt, videoID):
        if not connectedToServer:
            return
        # Request video to client
        path = requestVideo(videoID)
        self.loadVideo(os.path.abspath("../" + str(path) + ".mp4"))
        wx.CallAfter(self.loadVideo, os.path.abspath("../" + str(path) + ".mp4"))

    def loadVideo(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
            self.playBtn.Disable()
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.playBtn.Enable()
            self.pauseBtn.Disable()

    def OnMediaLoaded(self, evt):
        self.playBtn.Enable()

    def OnPlay(self, evt):
        if not connectedToServer:
            return
        # Play action to client, wait for server to send action back
        while not sendAction("ply", int(self.mc.Tell()/10)):
            pass
        if not self.mc.Play():
            wx.MessageBox("Unable to Play media", "ERROR", wx.ICON_ERROR | wx.OK)
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.playBtn.Disable()
            self.pauseBtn.Enable()

    def OnPause(self, evt):
        if not connectedToServer:
            return
        # Pause action to client, wait for server to send action back
        while not sendAction("pse", int(self.mc.Tell()/10)):
            pass
        self.mc.Pause()
        self.playBtn.Enable()
        self.pauseBtn.Disable()

    def OnForward(self, evt):
        if not connectedToServer:
            return
        # Fastforward action to client, wait for server to send action back
        while not sendAction("ffw", int(self.mc.Tell()/10)):
            pass
        offset = self.slider.GetValue()
        self.mc.Seek(offset + 5000)

    def OnBackward(self, evt):
        if not connectedToServer:
            return
        # Rewind action to client, wait for server to send action back
        while not sendAction("rwd", int(self.mc.Tell()/10)):
            pass
        offset = self.slider.GetValue()
        self.mc.Seek(offset - 5000)

    def OnSeek(self, evt):
        offset = self.slider.GetValue()
        self.mc.Seek(offset)

    def OnTimer(self, evt):
        offset = self.mc.Tell()
        self.slider.SetValue(offset)
        self.st_len.SetLabel('{:.2f}'.format(self.mc.Length()/1000))
        self.st_pos.SetLabel('{:.2f}/{:.2f}'.format(offset/1000, self.mc.Length()/1000))
        global predictionArray, connectedToServer
        if len(predictionArray) > 6:
            try:
                int((offset/self.mc.Length())*100)
                #If video is about to start or is ending/at end -> client-server connection TRUE
                if int((offset/self.mc.Length())*100) <= 1 or int((offset/self.mc.Length())*100) >= 99:
                    connectedToServer = True
                    self.st_status.SetLabel('Connected: {}'.format(connectedToServer))
                #If current time of video is a time that an action is anticipated -> client-server connection TRUE
                elif int((offset/self.mc.Length())*100) in predictionArray:
                    connectedToServer = True
                    self.st_status.SetLabel('Connected: {}'.format(connectedToServer))
                #Every other case -> client-server connection FALSE
                else:
                    connectedToServer = False
                    self.st_status.SetLabel('Connected: {}'.format(connectedToServer))
            except:
                pass

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None, title="Smart VP")
        self._my_sizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = TestPanel(self, None)
        self._my_sizer.Add(panel1, 1, wx.EXPAND)
        self.SetSizer(self._my_sizer)
        self.Fit()
        self.Show()

#Client methods
def recieve(sock, next):
    print("Connected to server: " + str(sock.getsockname()))
    connected = True
    while connected:
        try:
            data = sock.recv(1024)
        except:
            print("Server has disconnected")
            connected = False
            sock.close()
        else:
            data = data.decode("utf-8")
            if not data:
                print("Server has disconnected")
                connected = False
                sock.close()
                break
            print(data)
            next(sock, data)

def controlDecode(sock, data):
    recievedData = json.loads(data)
    if recievedData['type'] == "req":
        global currentVideoID, currentVideoPath, videoLoaded
        currentVideoID = recievedData['videoID']
        currentVideoPath = recievedData['title']
        videoLoaded = True
    elif recievedData['type'] == "prd":
        global predictionArray
        predictionArray = recievedData['prediction']
    elif recievedData['type'] == "act":
        global actionHandled
        actionHandled = True
    return

#Method gets called when user requests video from list
def requestVideo(videoID):
    global videoLoaded
    #Send video id to control server
    sendData = {
        'type': 'req',
        'videoID': str(videoID)
    }
    json_data = json.dumps(sendData).encode('utf-8')
    cSock.sendall(json_data)
    while not videoLoaded:
        #Wait for responce back
        pass
    videoLoaded = False
    return currentVideoPath

#Method gets called when user performs action on video
def sendAction(action, time):
    global actionHandled
    #Send action to control server for 2 reasons
        #To perform the action: action -> control server -> client
        #To save the action: action -> database
    sendData = {
        'type': 'act',
        'action': action,
        'videoID': currentVideoID,
        'time': time
    }
    json_data = json.dumps(sendData).encode('utf-8')
    cSock.sendall(json_data)
    while not actionHandled:
        #Wait for responce back
        pass
    actionHandled = False
    return True

def connect():
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

def setup():
    connect()
    #Create new thread for control server connection
    receiveThread = threading.Thread(target = recieve, args = (cSock, controlDecode))
    receiveThread.start()

if __name__ == '__main__':
    setup()
    app = wx.App()
    top = MyFrame()
    top.Show()
    app.MainLoop()
