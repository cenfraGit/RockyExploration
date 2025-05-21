# camera.py

import wx
import cv2
import numpy as np
from src.utils import dip
#from ultralytics import YOLO
import math

class PanelCamera(wx.Panel):
    def __init__(self, parent, capture, fps=200):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.capture = capture
        self.current_frame = None
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.fps = fps
        self.timer.Start(int(1000.0 / self.fps))
        self.panel_size = self.GetSize()
        #self.model = YOLO("yolo11n.pt", verbose=False)

    def OnSize(self, event):
        self.panel_size = self.GetSize()

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        #dc.SetBrush(wx.BLACK_BRUSH)
        #dc.DrawRectangle(0, 0, *self.GetSize())
        if self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            frame_aspect = w / float(h)
            panel_width, panel_height = self.GetSize()
            panel_aspect = panel_width / float(panel_height)

            if frame_aspect > panel_aspect:
                new_width = panel_width
                new_height = int(panel_width / frame_aspect)
                start_y = (panel_height - new_height) // 2
                start_x = 0
            else:
                new_height = panel_height
                new_width = int(panel_height * frame_aspect)
                start_x = (panel_width - new_width) // 2
                start_y = 0
                
            resized_frame = cv2.resize(self.current_frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            # resized_frame = cv2.flip(resized_frame, 0)

            # results = self.model(resized_frame, stream=True, verbose=False)
            # img = resized_frame
            # for r in results:
            #     boxes = r.boxes
            #     for box in boxes:
            #         x1, y1, x2, y2 = box.xyxy[0]
            #         x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            # confidence = math.ceil((box.conf[0]*100))/100
            # cls = self.model.names[int(box.cls[0])]
            # cv2.putText(img, cls, [x1, y1], cv2.FONT_HERSHEY_SIMPLEX,
            #             1, (255, 0, 255), 2)
            # resized_frame = img
            
            bmp = wx.Bitmap.FromBuffer(new_width, new_height, resized_frame)
            dc.DrawBitmap(bmp, start_x, start_y)

    def OnTimer(self, event):
        ret, frame = self.capture.read()
        if ret:
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.Refresh()
