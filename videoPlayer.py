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

        btn1 = wx.Button(self, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.OnPlay, btn1)
        self.playBtn = btn1

        btn2 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.OnPause, btn2)

        btn3 = wx.Button(self, -1, "Load Video 1")
        self.Bind(wx.EVT_BUTTON, lambda event: self.requestVideo(event, 1), btn3)

        btn4 = wx.Button(self, -1, "Load Video 2")
        self.Bind(wx.EVT_BUTTON, lambda event: self.requestVideo(event, 2), btn4)

        btn5 = wx.Button(self, -1, "Load Video 3")
        self.Bind(wx.EVT_BUTTON, lambda event: self.requestVideo(event, 3), btn5)

        slider = wx.Slider(self, -1, 0, 0, 10)
        self.slider = slider
        slider.SetMinSize((150, -1))
        self.Bind(wx.EVT_SLIDER, self.OnSeek, slider)

        self.st_len  = StaticText(self, -1, size=(100,-1))
        self.st_pos  = StaticText(self, -1, size=(100,-1))

        # setup the layout
        sizer = wx.GridBagSizer(5,5)
        sizer.Add(self.mc, (1,1), span=(5,1))#, flag=wx.EXPAND)
        sizer.Add(btn1, (1,3))
        sizer.Add(btn2, (2,3))
        sizer.Add(btn3, (3,3))
        sizer.Add(btn4, (4,3))
        sizer.Add(btn5, (5,3))
        sizer.Add(slider, (6,1), flag=wx.EXPAND)
        sizer.Add(self.st_len,  (1, 5))
        sizer.Add(self.st_pos,  (2, 5))
        self.SetSizer(sizer)

        self.loadVideo(os.path.abspath("database/video.mp4"))
        wx.CallAfter(self.loadVideo, os.path.abspath("database/video.mp4"))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(100)

    def loadVideo(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
            self.playBtn.Disable()
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.playBtn.Enable()

    def OnMediaLoaded(self, evt):
        self.playBtn.Enable()

    def requestVideo(self, evt, videoID):
        client.requestVideo(videoID)

    def OnPlay(self, evt):
        client.sendAction("ply", self.mc.Tell())
        if not self.mc.Play():
            wx.MessageBox("Unable to Play media : Unsupported format?", "ERROR", wx.ICON_ERROR | wx.OK)
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())

    def OnPause(self, evt):
        client.sendAction("pse", self.mc.Tell())
        self.mc.Pause()

    def OnSeek(self, evt):
        client.sendAction("ffw", self.mc.Tell())
        offset = self.slider.GetValue()
        self.mc.Seek(offset)

    def OnTimer(self, evt):
        offset = self.mc.Tell()
        self.slider.SetValue(offset)
        self.st_len.SetLabel('length: %d seconds' % (self.mc.Length()/1000))
        self.st_pos.SetLabel('position: %d' % offset)

    def ShutdownDemo(self):
        self.timer.Stop()
        del self.timer

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None, title="Video Player")
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
