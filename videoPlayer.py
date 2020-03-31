#Package imports
import wx
import wx.media
import os

#Module imports
import client

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

        # setup the layout
        sizer = wx.GridBagSizer(5,5)
        sizer.Add(self.mc, (1,1), span=(5,1), flag=wx.EXPAND)
        sizer.Add(self.st_pos, (1, 2))
        sizer.Add(play, (2,2))
        sizer.Add(pause, (3,2))
        sizer.Add(forward, (4,2))
        sizer.Add(backward, (5,2))
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
        path = client.requestVideo(videoID)
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
        client.sendAction("ply", int(self.mc.Tell()/10))
        if not self.mc.Play():
            wx.MessageBox("Unable to Play media", "ERROR", wx.ICON_ERROR | wx.OK)
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.playBtn.Disable()
            self.pauseBtn.Enable()

    def OnPause(self, evt):
        client.sendAction("pse", int(self.mc.Tell()/10))
        self.mc.Pause()
        self.playBtn.Enable()
        self.pauseBtn.Disable()

    def OnForward(self, evt):
        client.sendAction("ffw", int(self.mc.Tell()/10))
        offset = self.slider.GetValue()
        self.mc.Seek(offset + 5000)

    def OnBackward(self, evt):
        client.sendAction("rwd", int(self.mc.Tell()/10))
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

    def ShutdownDemo(self):
        self.timer.Stop()
        del self.timer

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None, title="Smart VP")
        self._my_sizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = TestPanel(self, None)
        self._my_sizer.Add(panel1, 1, wx.EXPAND)
        self.SetSizer(self._my_sizer)
        self.Fit()
        self.Show()

if __name__ == '__main__':
    import sys,os
    app = wx.App()
    top = MyFrame()
    top.Show()
    app.MainLoop()
