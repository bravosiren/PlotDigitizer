__author__ = "Meng Gao"
__email__ = "bravosixme@gmail.com"
__status__ = "Development"

import os
from PIL import ImageGrab

from time import sleep

here = os.path.abspath(os.path.dirname(__file__))
import sys

if sys.version_info < (3,):
    from future import standard_library

    standard_library.install_aliases()
else:
    pass

if sys.version_info < (3,):
    from future import standard_library

    standard_library.install_aliases()
    import tkFileDialog
    import tkMessageBox
    import tkSimpleDialog
else:
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
    import tkinter.simpledialog as tkSimpleDialog

from builtins import object

from ttkthemes import ThemedTk

from tkinter import Menu, StringVar, Label, SUNKEN, SW, X, BOTTOM, Frame, NE, NW, \
    BOTH, TOP, Button, LEFT, SE, Scrollbar, VERTICAL, Text, RIGHT, Y, END, Tk, \
    Canvas, Listbox, Entry, N, S, E, W, YES, Toplevel, ALL, Checkbutton, ttk, FLAT, GROOVE, IntVar, PhotoImage, \
    filedialog

from PIL import Image, ImageTk, ImageFont, ImageDraw

import time
import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

try:
    from StringIO import StringIO as MemoryIO
except:
    from io import BytesIO as MemoryIO

try:
    import pytesseract

    HAS_OCR = True
except:
    HAS_OCR = False

from plot_area import PlotArea, HAS_IMAGEGRAB
from auto_detect_Dialog import _auto_detect
from screenshot import screenShot

import base64
from realign_Dialog import _ReAlign, fix_plot_img, cross_point, _AutoAlign
from text_recognition import decode_predictions


class Point(object):
    def __init__(self, x, y, fi, fj):
        self.x = x
        self.y = y
        self.fi = fi
        self.fj = fj

    def get_str(self):
        return '%g, %g' % (self.x, self.y)

    def set_xy(self, x, y, fi, fj):
        self.x = x
        self.y = y
        self.fi = fi
        self.fj = fj

    def get_xy(self):
        return self.x, self.y


class MyPlot(object):
    def __init__(self, master):
        super().__init__()
        self.initComplete = 0

        self.frame = Frame(master)
        self.frame.pack(fill=BOTH, expand=YES)
        self.master = master
        self.x, self.y, self.w, self.h = -1, -1, -1, -1

        # set the window location
        windowWidth = 1000
        windowHeight = 600
        self.screenWidth = self.master.winfo_screenwidth()
        self.screenHeight = self.master.winfo_screenheight()
        window_x = int((self.screenWidth - windowWidth) / 2)
        window_y = int((self.screenHeight - windowHeight) / 2)
        self.master.title("MyDigitizer")

        icon = open("tmp.ico", "wb+")
        icon.write(base64.b64decode(
            "AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAACMuAAAjLgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOmuPQDprj0A6a49AemuPQHprj0A6a49AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADprj0A6a48AOmuPQforDk86Ks3fuisOKDorDig6Ks3fuisOTzprj0H6a48AOmuPQAAAAAAAAAAAAAAAADprj0A6a07AOmuPCDprTqd67VO8fDHev/z1Jj/89SY//DHev/rtU7x6a06nemuPCDprTsA6a49AAAAAADprj0A6a49AOmuPB7prjy978Vz//rt1f///fv///////////////3//O/X//DFdP/prjy86a48HumuPQDprj0A6a49AOmuPQTprTqW8cVy//747f/////////////////6+vr/39/f/93e3//07uL/8MVy/+mtOpborj0E6a49AOmuPQDprToz6LFI6t3Osv/c3N3/7u7u///////v7+7/1NTT/6empP+vrq3/tbW0/+fYu//mr0bq6q06M+muPQDprj0A6q04buO4ZP+Pi4X/sK+t/5uZl//a2tn/rayq/8bFxP+Rj43/qqmo/9bW1f+koJr/3bFd/+uuOW7prj0A6a49AOqtOI/lwX3/lpWT//X19f/Ix8b/o6Kg/6Wkov/Hx8b/nZya/62sqv/c3Nv/np2b/967d//qrjmP6a49AOmuPQDqrTiO5cF9/5eWlP/19fX/zs3M/5+enP+0s7H/0dDP/6yrqf+fnpz/wsLA/6+urf/ivnr/6q05jumuPQDprj0A6q04bOK2Yv+NiYL/urm4/5iXlP/NzMv/y8rJ/+zs6//z8vL/4+Pi/93d3f/Ewbz/47di/+qtOGzprj0A6a49AOqtOjDnsEXo0sKj/8/P0P/i4eH//f39/+Pj4v/19fX////////////9/v//28us/+OsQujqrjsw6a49AOmuPQDorj0D6a06kfHEb//+9+r//////////////////////////////////fbo//DEb//prTqR6K09A+muPQAAAAAA6a49AOmuPBvprTy378Nu//rrz//+/fn////////////+/fn/+uvP/+/Dbv/prTy36a48G+muPQAAAAAAAAAAAOmuPQDprTwA6a48HOmtOpXrtEvt78V0//PRkv/z0ZL/78V0/+u0S+3prTqV6a48HOmtPADprj0AAAAAAAAAAAAAAAAAAAAAAOmuPADprj4G6aw5NeirN3XorDiX6Kw4l+irN3XprDk26a4+BumuPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/n8AAPAPAADgBwAAwAMAAIABAACAAQAAgAEAAIABAACAAQAAgAEAAIABAACAAQAAwAMAAOAHAADwDwAA//8AAA=="))
        icon.close()
        self.master.iconbitmap('tmp.ico')
        self.master.geometry("%sx%s+%s+%s" % (windowWidth, windowHeight, window_x, window_y))

        self.point_list = []
        self.option_list = []

        self.plot_anchoring = False
        self.plot_anchored = False

        self.image_imported = False
        self.original_img = None
        self.current_img = None

        # bind master to <Configure> in order to handle any resizing, etc.
        # postpone self.master.bind("<Configure>", self.Master_Configure)
        # self.master.bind('<Enter>', self.bindConfigure)
        # self.master.bind('<Button-1>', self.bindConfigure)
        # master.bind('<Escape>', self.Clear_Pending_Actions)

        # ======================  Make a Widget Frame =============

        self.notebook = ttk.Notebook(self.frame)
        tab_1 = ttk.Frame(self.notebook)
        tab_2 = ttk.Frame(self.notebook)
        tab_3 = ttk.Frame(self.notebook)
        tab_4 = ttk.Frame(self.notebook)
        self.notebook.add(tab_1, text="Import Image")
        self.notebook.add(tab_2, text="Detect Curve")
        self.notebook.add(tab_3, text="Add Points")
        self.notebook.add(tab_4, text="Export Data")
        self.notebook.pack(fill=BOTH, expand=1)

        # ------------ tab_1 -----------------
        tab_1_left_frame = ttk.Frame(tab_1)
        tab_1_left_frame.pack(fill=BOTH, side=LEFT, anchor=NW, expand=YES)
        tab_1_left_frame_1 = ttk.LabelFrame(tab_1_left_frame, text="Import Image")
        tab_1_left_frame_2 = ttk.LabelFrame(tab_1_left_frame, text="Anchor Plot")
        tab_1_left_frame_3 = ttk.LabelFrame(tab_1_left_frame, text="Status Bar")

        self.import_file = ttk.Button(tab_1_left_frame_1, text="From Files", width="14")
        self.import_file.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.import_file.bind("<ButtonRelease-1>", self.menu_File_Import_Image)

        self.import_screen = ttk.Button(tab_1_left_frame_1, text="Take Screenshot", width="14")
        self.import_screen.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.import_screen.bind("<ButtonRelease-1>", self.menu_Screen_Import_Image)

        self.import_clipboard = ttk.Button(tab_1_left_frame_1, text="From Clipboard", width="14")
        self.import_clipboard.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.import_clipboard.bind("<ButtonRelease-1>", self.menu_Paste_Clipboard_Image_event)

        tab_1_left_frame_1.pack(side=TOP, anchor=NW, fill=X, padx=10, pady=10)

        tab_1_left_frame_2_ch3 = ttk.Frame(tab_1_left_frame_2)
        self.anchor_plot = ttk.Button(tab_1_left_frame_2_ch3, text="Anchor Plot", width="14")
        self.anchor_plot.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.anchor_plot.bind("<ButtonRelease-1>", self.anchor_Plot)

        self.auto_detect = ttk.Button(tab_1_left_frame_2_ch3, text="Ticks OCR", width="14")
        self.auto_detect.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.auto_detect.bind("<ButtonRelease-1>", self.auto_Detect_Coordinate)

        self.update = ttk.Button(tab_1_left_frame_2_ch3, text="Update", width="14")
        self.update.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.update.bind("<ButtonRelease-1>", self.update_Value)

        tab_1_left_frame_2_ch3.pack(side=TOP, anchor=NW)

        tab_1_left_frame_2_ch1 = ttk.Frame(tab_1_left_frame_2)
        self.xmin_label = ttk.Label(tab_1_left_frame_2_ch1, text="X Min")
        self.xmin_label.pack(side=LEFT, anchor=W, padx=5, pady=5)

        self.xmin_entry = ttk.Entry(tab_1_left_frame_2_ch1, width="7")
        self.xmin_entry.pack(side=LEFT, anchor=W, padx=5, pady=5)

        self.xmax_label = ttk.Label(tab_1_left_frame_2_ch1, text="X Max")
        self.xmax_label.pack(side=LEFT, anchor=W, padx=5, pady=5)

        self.xmax_entry = ttk.Entry(tab_1_left_frame_2_ch1, width="7")
        self.xmax_entry.pack(side=LEFT, anchor=W, padx=5, pady=5)

        self.xlog_checkbutton = ttk.Checkbutton(tab_1_left_frame_2_ch1, text="Log X Scale")
        self.xlog_checkbutton.pack(side=LEFT, anchor=W, padx=15, pady=5)
        self.xlog_checkbutton_StringVar = StringVar()
        self.xlog_checkbutton_StringVar.set('no')
        self.xlog_checkbutton.configure(variable=self.xlog_checkbutton_StringVar, onvalue="yes", offvalue="no")
        self.xlog_checkbutton_StringVar_traceName = self.xlog_checkbutton_StringVar.trace_variable("w",
                                                                                                   self.xlog_checkbutton_StringVar_Callback)

        tab_1_left_frame_2_ch1.pack(side=TOP, anchor=NW, padx=5, pady=10)

        tab_1_left_frame_2_ch2 = ttk.Frame(tab_1_left_frame_2)

        self.ymin_label = ttk.Label(tab_1_left_frame_2_ch2, text="Y Min")
        self.ymin_label.pack(side=LEFT, anchor=W, padx=4, pady=5)

        self.ymin_entry = ttk.Entry(tab_1_left_frame_2_ch2, width="7")
        self.ymin_entry.pack(side=LEFT, anchor=W, padx=5, pady=5)

        self.ymax_label = ttk.Label(tab_1_left_frame_2_ch2, text="Y Max")
        self.ymax_label.pack(side=LEFT, anchor=W, padx=4, pady=5)

        self.ymax_entry = ttk.Entry(tab_1_left_frame_2_ch2, width="7")
        self.ymax_entry.pack(side=LEFT, anchor=W, padx=5, pady=5)

        self.ylog_checkbutton = ttk.Checkbutton(tab_1_left_frame_2_ch2, text="Log Y Scale")
        self.ylog_checkbutton.pack(side=LEFT, anchor=W, padx=15, pady=5)
        self.ylog_checkbutton_StringVar = StringVar()
        self.ylog_checkbutton_StringVar.set('no')
        self.ylog_checkbutton.configure(variable=self.ylog_checkbutton_StringVar, onvalue="yes", offvalue="no")
        self.ylog_checkbutton_StringVar_traceName = self.ylog_checkbutton_StringVar.trace_variable("w",
                                                                                                   self.ylog_checkbutton_StringVar_Callback)

        tab_1_left_frame_2_ch2.pack(side=TOP, anchor=NW, padx=5, pady=10)

        tab_1_left_frame_2.pack(side=TOP, anchor=N, fill=BOTH, padx=10)

        # Status Bar
        tab_1_left_frame_3_ch1 = ttk.Frame(tab_1_left_frame_3)
        status_scrollbar = ttk.Scrollbar(tab_1_left_frame_3_ch1, orient=VERTICAL)
        self.status_listbox = Listbox(tab_1_left_frame_3_ch1, width="50", bg="#e9eaeb", fg="#3daee9", relief=GROOVE,
                                      bd="2", height="14", yscrollcommand=status_scrollbar.set)
        status_scrollbar.config(command=self.status_listbox.yview)

        self.status_listbox.pack(side=LEFT, fill=Y, expand=YES, padx=5, pady=5)
        status_scrollbar.pack(side=LEFT, fill=Y, expand=YES, pady=5)

        tab_1_left_frame_3_ch1.pack(side=TOP, anchor=NW, fill=Y)

        tab_1_left_frame_3.pack(side=TOP, anchor=N, fill=BOTH, expand=YES, padx=10, pady=10)

        self.status_listbox.insert(END, "Welcome to MyPlotDigitizer! ")
        self.status_listbox.insert(END, "Please import your image...... ")

        # Tab1 Right Frame
        tab_1_right_frame = ttk.LabelFrame(tab_1, text="Plot Area")
        tab_1_right_frame.pack(fill=BOTH, expand=YES, side=LEFT, anchor=NE, pady=10)

        tab_1_right_frame_1 = ttk.Frame(tab_1_right_frame)

        self.auto_align = ttk.Button(tab_1_right_frame_1, text="Auto Align", width="12")
        self.auto_align.pack(side=LEFT, anchor=W, padx=9, pady=5)
        self.auto_align.bind("<ButtonRelease-1>", self.auto_Align)

        self.points_align = ttk.Button(tab_1_right_frame_1, text="3Points Align", width="12")
        self.points_align.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.points_align.bind("<ButtonRelease-1>", self.points_Align)

        self.save_image = ttk.Button(tab_1_right_frame_1, text="Save Image", width="12")
        self.save_image.pack(side=RIGHT, anchor=E, padx=9, pady=5)
        self.save_image.bind("<ButtonRelease-1>", self.save_Image)

        tab_1_right_frame_1.pack(side=TOP, anchor=NW, fill=X, pady=5)

        tab_1_right_frame_2 = ttk.Frame(tab_1_right_frame)

        self.grayscale_checkbutton = ttk.Checkbutton(tab_1_right_frame_2, text="Gray Scale")
        self.grayscale_checkbutton.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.grayscale_checkbutton_StringVar = StringVar()
        self.grayscale_checkbutton_StringVar.set('no')
        self.grayscale_checkbutton.configure(variable=self.grayscale_checkbutton_StringVar, onvalue="yes",
                                             offvalue="no")
        self.grayscale_checkbutton_StringVar_traceName = self.grayscale_checkbutton_StringVar.trace_variable("w",
                                                                                                             self.grayscale_checkbutton_StringVar_Callback)

        self.enhancement_checkbutton = ttk.Checkbutton(tab_1_right_frame_2, text="Enhancement")
        self.enhancement_checkbutton.pack(side=LEFT, anchor=W, padx=0, pady=5)
        self.enhancement_checkbutton_StringVar = StringVar()
        self.enhancement_checkbutton_StringVar.set('no')
        self.enhancement_checkbutton.configure(variable=self.enhancement_checkbutton_StringVar, onvalue="yes",
                                               offvalue="no")
        self.enhancement_checkbutton_StringVar_traceName = self.enhancement_checkbutton_StringVar.trace_variable("w",
                                                                                                                 self.enhancement_checkbutton_StringVar_Callback)

        self.cleanbg_checkbutton = ttk.Checkbutton(tab_1_right_frame_2, text="Clean Background")
        self.cleanbg_checkbutton.pack(side=LEFT, anchor=W, padx=0, pady=5)
        self.cleanbg_checkbutton_StringVar = StringVar()
        self.cleanbg_checkbutton_StringVar.set('no')
        self.cleanbg_checkbutton.configure(variable=self.cleanbg_checkbutton_StringVar, onvalue="yes", offvalue="no")
        self.cleanbg_checkbutton_StringVar_traceName = self.cleanbg_checkbutton_StringVar.trace_variable("w",
                                                                                                         self.cleanbg_checkbutton_StringVar_Callback)

        self.romovegrid_checkbutton = ttk.Checkbutton(tab_1_right_frame_2, text="Remove Grid")
        self.romovegrid_checkbutton.pack(side=LEFT, anchor=W, padx=0, pady=5)
        self.romovegrid_checkbutton_StringVar = StringVar()
        self.romovegrid_checkbutton_StringVar.set('no')
        self.romovegrid_checkbutton.configure(variable=self.romovegrid_checkbutton_StringVar, onvalue="yes",
                                              offvalue="no")
        self.romovegrid_checkbutton_StringVar_traceName = self.romovegrid_checkbutton_StringVar.trace_variable("w",
                                                                                                               self.romovegrid_checkbutton_StringVar_Callback)

        tab_1_right_frame_2.pack(side=TOP, anchor=NW, fill=X)

        tab_1_right_frame_3 = ttk.Frame(tab_1_right_frame_2)

        self.zoomin = ttk.Button(tab_1_right_frame_3, text="+", width="1")
        self.zoomin.pack(side=LEFT, anchor=W, padx=1, pady=5)
        self.zoomin.bind("<ButtonRelease-1>", self.tab1_Zoomin)

        self.zoomout = ttk.Button(tab_1_right_frame_3, text="-", width="1")
        self.zoomout.pack(side=LEFT, anchor=W, padx=1, pady=5)
        self.zoomout.bind("<ButtonRelease-1>", self.tab1_Zoomout)

        self.fit = ttk.Button(tab_1_right_frame_3, text="Fit", width="3")
        self.fit.pack(side=LEFT, anchor=W, padx=1, pady=5)
        self.fit.bind("<ButtonRelease-1>", self.tab1_Fit)

        tab_1_right_frame_3.pack(side=RIGHT, anchor=E, padx=8)

        self.plot_canvas = Canvas(tab_1_right_frame, width="600", height="600", bg="#e9eaeb", relief=GROOVE, bd="2")
        self.plot_canvas.pack(fill=BOTH, expand=YES, side=TOP, padx=5, pady=5)
        self.plot_canvas.bind("<Configure>", self.tab1_Plot_Canvas_Resize)
        self.plot_canvas.bind("<ButtonRelease-1>", self.tab1_Plot_Canvas_Click)

        ######
        ###tab3

        tab_3_left_frame = ttk.LabelFrame(tab_3, text="Points List")
        tab_3_left_frame.pack(fill=BOTH, side=LEFT, anchor=NW, expand=YES, padx=10, pady=10)

        tab_3_left_frame_1 = ttk.Frame(tab_3_left_frame)

        self.Del_Button = ttk.Button(tab_3_left_frame_1, text="Delete Point", width="10")
        self.Del_Button.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.Del_Button.bind("<ButtonRelease-1>", self.Del_Button_Click)

        self.Sort_Button = ttk.Button(tab_3_left_frame_1, text="Sort By X", width="10")
        self.Sort_Button.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.Sort_Button.bind("<ButtonRelease-1>", self.Sort_Button_Click)

        self.Delete_All_Button = ttk.Button(tab_3_left_frame_1, text="Delete All", width="10")
        self.Delete_All_Button.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.Delete_All_Button.bind("<ButtonRelease-1>", self.Delete_All_Button_Click)

        tab_3_left_frame_1.pack(side=TOP, anchor=N, fill=BOTH, expand=YES, padx=10)

        tab_3_left_frame_2 = ttk.Frame(tab_3_left_frame)

        tab_3_left_frame_2_1 = ttk.Frame(tab_3_left_frame_2)
        point_scrollbar = ttk.Scrollbar(tab_3_left_frame_2_1, orient=VERTICAL)
        self.point_listbox = Listbox(tab_3_left_frame_2_1, width="40", bg="#e9eaeb", fg="#3daee9", selectmode="single",
                                     relief=GROOVE,
                                     bd="2", height="35", yscrollcommand=point_scrollbar.set)
        point_scrollbar.config(command=self.point_listbox.yview)

        self.point_listbox.pack(side=LEFT, fill=Y, expand=YES, padx=5)
        point_scrollbar.pack(side=LEFT, fill=Y, expand=YES)

        tab_3_left_frame_2_1.pack(side=TOP, anchor=NW, fill=Y)

        tab_3_left_frame_2.pack(side=TOP, anchor=N, fill=BOTH, expand=YES, padx=10, pady=10)
        self.point_listbox.bind("<ButtonRelease-1>", self.point_listbox_Click)

        # tab3 right side
        tab_3_right_frame = ttk.LabelFrame(tab_3, text="Plot Area")
        tab_3_right_frame.pack(fill=BOTH, expand=YES, side=LEFT, anchor=NE, padx=10, pady=10)

        tab_3_right_frame_1 = ttk.Frame(tab_3_right_frame)
        self.detect_curve = ttk.Button(tab_3_right_frame_1, text="Detect Curve", width="18")
        self.detect_curve.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.detect_curve.bind("<ButtonRelease-1>", self.detect_Curve)

        self.add_point_with_errorbar = ttk.Button(tab_3_right_frame_1, text="Add Point(Error Bar)", width="18")
        self.add_point_with_errorbar.pack(side=LEFT, anchor=W, padx=5, pady=5)
        self.add_point_with_errorbar.bind("<ButtonRelease-1>", self.add_Errorbar)

        tab_3_right_frame_1.pack(side=TOP, anchor=NW, fill=X)

        tab_3_right_frame_2 = ttk.Frame(tab_3_right_frame_1)

        self.zoomin_tab3 = ttk.Button(tab_3_right_frame_2, text="+", width="1")
        self.zoomin_tab3.pack(side=LEFT, padx=1, pady=5)
        self.zoomin_tab3.bind("<ButtonRelease-1>", self.tab3_Zoomin)

        self.zoomout_tab3 = ttk.Button(tab_3_right_frame_2, text="-", width="1")
        self.zoomout_tab3.pack(side=LEFT, padx=1, pady=5)
        self.zoomout_tab3.bind("<ButtonRelease-1>", self.tab3_Zoomout)

        self.fit_tab3 = ttk.Button(tab_3_right_frame_2, text="Fit", width="3")
        self.fit_tab3.pack(side=LEFT, padx=1, pady=5)
        self.fit_tab3.bind("<ButtonRelease-1>", self.tab3_Fit)

        tab_3_right_frame_2.pack(side=RIGHT, anchor=E, padx=8)

        self.plot_canvas_tab3 = Canvas(tab_3_right_frame, width="600", height="600", bg="#e9eaeb", relief=GROOVE,
                                       bd="2")
        self.plot_canvas_tab3.pack(fill=BOTH, expand=YES, side=TOP, padx=5, pady=5)
        self.plot_canvas_tab3.bind("<Configure>", self.tab3_Plot_Canvas_Resize)
        self.plot_canvas_tab3.bind("<ButtonRelease-1>", self.tab3_Plot_Canvas_Click)

        # tab4
        tab_4_left_frame = ttk.LabelFrame(tab_4, text="Export Data")
        tab_4_left_frame.pack(fill=BOTH, side=LEFT, anchor=NW, expand=YES, padx=10, pady=10)

        tab_4_left_frame_1 = ttk.Frame(tab_4_left_frame)

        self.to_CSV = ttk.Button(tab_4_left_frame_1, text="Save CSV", width="14")
        self.to_CSV.pack(side=LEFT, anchor=NW, padx=5, pady=10)
        self.to_CSV.bind("<ButtonRelease-1>", self.export_to_CSV)

        self.to_Excel = ttk.Button(tab_4_left_frame_1, text="2Clipboard(Tab)", width="14")
        self.to_Excel.pack(side=LEFT, anchor=NW, padx=2, pady=10)
        self.to_Excel.bind("<ButtonRelease-1>", self.export_to_Excel)

        self.to_Clipboard = ttk.Button(tab_4_left_frame_1, text="2Clipboard(Comma)", width="14")
        self.to_Clipboard.pack(side=LEFT, anchor=NW, padx=2, pady=10)
        self.to_Clipboard.bind("<ButtonRelease-1>", self.export_to_Clipboard)

        tab_4_left_frame_1.pack(side=TOP, anchor=N, fill=BOTH, expand=YES, padx=10)

        tab_4_left_frame_2 = ttk.Frame(tab_4_left_frame)

        tab_4_left_frame_2_1 = ttk.Frame(tab_4_left_frame_2)
        result_scrollbar = ttk.Scrollbar(tab_4_left_frame_2_1, orient=VERTICAL)
        self.result_listbox = Listbox(tab_4_left_frame_2_1, width="40", bg="#e9eaeb", fg="#3daee9", selectmode="single",
                                      relief=GROOVE,
                                      bd="2", height="35", yscrollcommand=result_scrollbar.set)
        result_scrollbar.config(command=self.result_listbox.yview)

        self.result_listbox.pack(side=LEFT, fill=Y, expand=YES, padx=5)
        result_scrollbar.pack(side=LEFT, fill=Y, expand=YES)

        tab_4_left_frame_2_1.pack(side=TOP, anchor=NW, fill=Y)

        tab_4_left_frame_2.pack(side=TOP, anchor=N, fill=BOTH, expand=YES, padx=10, pady=10)

        tab_4_right_frame = ttk.LabelFrame(tab_4, text="Reconstruct Plot")
        tab_4_right_frame.pack(fill=BOTH, expand=YES, side=LEFT, anchor=NE, padx=10, pady=10)

        tab_4_right_frame_1 = ttk.Frame(tab_4_right_frame)
        self.reconstruct_plot = ttk.Button(tab_4_right_frame_1, text="Reconstruct Plot", width="18")
        self.reconstruct_plot.pack(side=LEFT, anchor=W, padx=5, pady=5)

        tab_4_right_frame_1.pack(side=TOP, anchor=NW, fill=X)

        self.plot_canvas_tab4 = Canvas(tab_4_right_frame, width="600", height="600", bg="#e9eaeb", relief=GROOVE,
                                       bd="2")
        self.plot_canvas_tab4.pack(fill=BOTH, expand=YES, side=TOP, padx=5, pady=5)

        # Mouse Wheel for Zooming in and out
        self.plot_canvas.bind("<MouseWheel>", self.tab1_MouseWheelHandler)  # Windows Binding
        self.plot_canvas.bind("<Button-4>", self.tab1_MouseWheelHandler)  # Linux Binding
        self.plot_canvas.bind("<Button-5>", self.tab1_MouseWheelHandler)  # Linux Binding
        self.plot_canvas.bind("<Button-1>", self.tab1_Canvas_Begin_End_Drag)
        self.plot_canvas.bind("<B3-Motion>", self.tab1_Canvas_Drag_Axes)
        self.plot_canvas.bind("<Motion>", self.tab1_Canvas_Hover)
        self.plot_canvas.bind("<Enter>", self.tab1_Canvas_Enter)
        self.plot_canvas.bind("<Leave>", self.tab1_Canvas_Leave)

        self.plot_canvas_tab3.bind("<MouseWheel>", self.tab3_MouseWheelHandler)  # Windows Binding
        self.plot_canvas_tab3.bind("<Button-4>", self.tab3_MouseWheelHandler)  # Linux Binding
        self.plot_canvas_tab3.bind("<Button-5>", self.tab3_MouseWheelHandler)  # Linux Binding
        self.plot_canvas_tab3.bind("<Button-1>", self.tab3_Canvas_Begin_End_Drag)
        self.plot_canvas_tab3.bind("<B3-Motion>", self.tab3_Canvas_Drag_Axes)
        self.plot_canvas_tab3.bind("<Motion>", self.tab3_Canvas_Hover)
        self.plot_canvas_tab3.bind("<Enter>", self.tab3_Canvas_Enter)
        self.plot_canvas_tab3.bind("<Leave>", self.tab3_Canvas_Leave)

        # PlotArea
        self.PA_tab1 = PlotArea(w_canv=600, h_canv=600)  # will hold PlotArea() when it is opened
        self.PA_tab3 = PlotArea(w_canv=600, h_canv=600)
        self.has_some_new_data = False

        self.tab1_is_dragging = False
        self.tab3_is_dragging = False
        self.last_right_click_pos = (0, 0)  # any action calling Canvas_Find_Closest will set

        self.last_hover_pos = (0, 0)
        self.tab3_in_canvas = False
        self.tab1_in_canvas = False

        # tooltip
        self.canvas_tooltip_num = 10

        # Units NEED to be fraction of img
        self.canvas_click_posL = [None, None, None, None]  # only useful if all None's replaced
        self.canvas_click_eventL = [None, None, None, None]
        self.distortion_flag = False

        master.protocol('WM_DELETE_WINDOW', self.cleanupOnQuit)

        self.master.update_idletasks()
        # give a few milliseconds before calling bindConfigure
        self.master.after(100, lambda: self.bindConfigure(None))

    def Initialize_Image_State(self):

        self.point_listbox.delete(0, END)
        self.xmin_entry.delete(0, END)
        self.ymin_entry.delete(0, END)
        self.xmax_entry.delete(0, END)
        self.xmax_entry.delete(0, END)

        self.ylog_checkbutton_StringVar.set('no')
        self.xlog_checkbutton_StringVar.set('no')
        self.grayscale_checkbutton_StringVar.set('no')
        self.enhancement_checkbutton_StringVar.set('no')
        self.cleanbg_checkbutton_StringVar.set('no')
        self.romovegrid_checkbutton_StringVar.set('no')

        self.point_list = []
        self.option_list = []

        self.has_some_new_data = False

        self.tab1_is_dragging = False
        self.tab3_is_dragging = False

        self.last_right_click_pos = (0, 0)  # any action calling Canvas_Find_Closest will set

        self.canvas_tooltip_num = 10

        # Units NEED to be fraction of img
        self.canvas_click_posL = [None, None, None, None]  # only useful if all None's replaced
        self.canvas_click_eventL = [None, None, None, None]
        self.distortion_flag = False

        self.plot_anchoring = False
        self.plot_anchored = False

        self.image_Fit()
        self.tab1_plot()

    def cleanupOnQuit(self):
        if (len(self.point_list) > 0) and self.has_some_new_data:
            if self.AskYesNo(title='MyDigitizer', message='Do you want to exit WITHOUT saving data?\n'):
                try:
                    self.master.destroy()
                except:
                    pass
                sys.exit(1)
        else:
            try:
                self.master.destroy()
            except:
                pass
            sys.exit(1)

    def bindConfigure(self, event):
        if not self.initComplete:
            self.initComplete = 1
            self.master.bind("<Configure>", self.Master_Configure)
            self.tab1_plot()
            self.tab3_plot()

    def Master_Configure(self, event):

        if event.widget != self.master:
            if self.w > -1:
                return

        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())

        if (self.x, self.y, self.w, self.h) == (-1, -1, -1, -1):
            self.x, self.y, self.w, self.h = x, y, w, h
            # self.lb_init_width = int(self.Defined_Points_Listbox_frame.winfo_width())
            # self.lb_init_height = int(self.Defined_Points_Listbox_frame.winfo_height())
            self.w_init = w
            self.h_init = h
            self.w_canv_init = int(self.plot_canvas.winfo_width())
            self.h_canv_init = int(self.plot_canvas.winfo_height())

        if self.w != w or self.h != h:
            self.w = w
            self.h = h

        self.frame.update()
        # self.status_listbox.insert(END, "Configure:x{},y{},w{},h{}".format(x, y, self.w_canv_init, self.h_canv_init))

    def menu_Paste_Clipboard_Image_event(self, event):
        # if (len(self.point_list) > 0) and self.has_some_new_data:
        if self.image_imported is True:
            if not self.AskYesNo(title='Import New Image?',
                                 message='Your current data will be DISGARDED!'):
                return
        self.menu_Paste_Clipboard_Image()

    def menu_Paste_Clipboard_Image(self):
        try:
            if self.PA_tab1.set_img_from_clipboard():
                self.original_img = self.PA_tab1.img
                self.current_img = self.PA_tab1.img
                self.PA_tab1.set_img(self.current_img)
                self.PA_tab3.set_img(self.current_img)
                self.Initialize_Image_State()
                self.image_imported = True
                self.status_listbox.insert(END, " Pasted Image from Clipboard! Size:{}x{}".format(self.PA_tab1.w_img,
                                                                                                  self.PA_tab1.h_img))
            else:
                self.status_listbox.insert(END, "Paste Image Failed!")
        except:
            self.status_listbox.insert(END, "Paste Image Failed!")

    def menu_File_Import_Image(self, another_P):
        # if (len(self.point_list) > 0) and self.has_some_new_data:
        if self.image_imported is True:
            if not self.AskYesNo(title='Import New Image?',
                                 message='Your current data will be DISGARDED!'):
                return

        filetypes = [
            ('Images', '*.png;*.jpg;*.gif;*.jpeg'),
            ('Any File', '*.*')]
        img_path = tkFileDialog.askopenfilename(parent=self.master, title='Open Image file',
                                                filetypes=filetypes)

        if img_path:
            if self.PA_tab1.open_img_file(img_path):
                head, fName = os.path.split(img_path)
                self.original_img = self.PA_tab1.img
                self.current_img = self.PA_tab1.img

                self.PA_tab1.set_img(self.current_img)
                self.PA_tab3.set_img(self.current_img)
                self.Initialize_Image_State()
                self.status_listbox.insert(END, 'File "{}" Opened!  Size:{}x{}'.format(fName, self.PA_tab1.w_img,
                                                                                       self.PA_tab1.h_img))
                self.image_imported = True
        else:
            self.status_listbox.insert(END, "Open Image Failed,Please Try Again")
            return

    def menu_Screen_Import_Image(self, another_P):
        try:
            screenShot(self.master, self.screenWidth, self.screenHeight)
            self.status_listbox.insert(END, 'Screenshot Saved!')

        except:
            pass

    def tab1_plot(self):
        # make coordinate axes
        self.plot_canvas.delete("all")
        # if self.image_imported:

        # try:
        #
        # except Exception as e:
        #     pass
        greyscale = str(self.grayscale_checkbutton_StringVar.get()) == 'yes'
        # self.process_Image()
        if self.canvas_tooltip_num > 3:
            self.text_on_canvas = ''
        elif self.canvas_tooltip_num == 0:
            self.text_on_canvas = 'Left Click X Min'
        elif self.canvas_tooltip_num == 1:
            self.text_on_canvas = 'Left Click X Max'
        elif self.canvas_tooltip_num == 2:
            self.text_on_canvas = 'Left Click Y Min'
        elif self.canvas_tooltip_num == 3:
            self.text_on_canvas = 'Left Click Y Max'

        self.photo_image_tab1 = self.PA_tab1.get_tk_photoimage(greyscale=greyscale, text=self.text_on_canvas,
                                                               show_linlog_text=True)
        self.plot_canvas.create_image(0, 0, anchor=NW, image=self.photo_image_tab1)

        # show x and y axes if they are visible
        if self.plot_anchored is True:
            pos_xmin, pos_xmax, pos_ymin, pos_ymax = self.canvas_click_posL
            i = self.PA_tab1.get_canvas_i_from_img_fi(pos_xmax[0])
            j = self.PA_tab1.get_canvas_j_from_img_fj(pos_xmax[1])
            self.plot_canvas.create_line(i, j - 10, i, j + 10, fill="#3daee9", width=3)
            self.plot_canvas.create_line(i - 10, j, i + 10, j, fill="#3daee9", width=3)
            i = self.PA_tab1.get_canvas_i_from_img_fi(pos_xmin[0])
            j = self.PA_tab1.get_canvas_j_from_img_fj(pos_xmin[1])
            self.plot_canvas.create_line(i, j - 10, i, j + 10, fill="#3daee9", width=3)
            self.plot_canvas.create_line(i - 10, j, i + 10, j, fill="#3daee9", width=3)
            i = self.PA_tab1.get_canvas_i_from_img_fi(pos_ymin[0])
            j = self.PA_tab1.get_canvas_j_from_img_fj(pos_ymin[1])
            self.plot_canvas.create_line(i, j - 10, i, j + 10, fill="#5ce0ec", width=3)
            self.plot_canvas.create_line(i - 10, j, i + 10, j, fill="#5ce0ec", width=3)
            i = self.PA_tab1.get_canvas_i_from_img_fi(pos_ymax[0])
            j = self.PA_tab1.get_canvas_j_from_img_fj(pos_ymax[1])
            self.plot_canvas.create_line(i, j - 10, i, j + 10, fill="#5ce0ec", width=3)
            self.plot_canvas.create_line(i - 10, j, i + 10, j, fill="#5ce0ec", width=3)

        # Show cross-hairs for picking axis points
        if self.tab1_in_canvas:
            x, y = self.last_hover_pos
            self.plot_canvas.create_line(x, 0, x, self.PA_tab1.h_canv, fill="#3daee9", width=2, dash=(15, 25))
            self.plot_canvas.create_line(0, y, self.PA_tab1.w_canv, y, fill="#3daee9", width=2, dash=(15, 25))

    def tab3_plot(self):
        self.plot_canvas_tab3.delete("all")

        self.photo_image_tab3 = self.PA_tab3.get_tk_photoimage(greyscale=False, text="",
                                                               show_linlog_text=True)
        self.plot_canvas_tab3.create_image(0, 0, anchor=NW, image=self.photo_image_tab3)

        iL = [i for i in self.point_listbox.curselection()]
        if (len(iL) > 0):
            isel = iL[0]
        else:
            isel = -1

        # Show points
        for ip, P in enumerate(self.point_list):
            x, y = P.get_xy()
            i, j = self.PA_tab3.get_ij_at_xy(x, y)

            if min(i, j) >= 0:
                if (isel >= 0) and (ip == isel):
                    self.plot_canvas_tab3.create_rectangle((i - 5, j - 5, i + 5, j + 5), outline="#3daee9",
                                                           fill="#3daee9")
                else:
                    self.plot_canvas_tab3.create_rectangle((i - 5, j - 5, i + 5, j + 5), outline="#3daee9",
                                                           fill="#5ce0ec")

        if self.plot_anchored is True:
            pos_xmin, pos_xmax, pos_ymin, pos_ymax = self.canvas_click_posL
            i = self.PA_tab3.get_canvas_i_from_img_fi(pos_xmax[0])
            j = self.PA_tab3.get_canvas_j_from_img_fj(pos_xmax[1])
            self.plot_canvas_tab3.create_line(i, j - 10, i, j + 10, fill="#3daee9", width=3)
            self.plot_canvas_tab3.create_line(i - 10, j, i + 10, j, fill="#3daee9", width=3)
            i = self.PA_tab3.get_canvas_i_from_img_fi(pos_xmin[0])
            j = self.PA_tab3.get_canvas_j_from_img_fj(pos_xmin[1])
            self.plot_canvas_tab3.create_line(i, j - 10, i, j + 10, fill="#3daee9", width=3)
            self.plot_canvas_tab3.create_line(i - 10, j, i + 10, j, fill="#3daee9", width=3)
            i = self.PA_tab3.get_canvas_i_from_img_fi(pos_ymin[0])
            j = self.PA_tab3.get_canvas_j_from_img_fj(pos_ymin[1])
            self.plot_canvas_tab3.create_line(i, j - 10, i, j + 10, fill="#5ce0ec", width=3)
            self.plot_canvas_tab3.create_line(i - 10, j, i + 10, j, fill="#5ce0ec", width=3)
            i = self.PA_tab3.get_canvas_i_from_img_fi(pos_ymax[0])
            j = self.PA_tab3.get_canvas_j_from_img_fj(pos_ymax[1])
            self.plot_canvas_tab3.create_line(i, j - 10, i, j + 10, fill="#5ce0ec", width=3)
            self.plot_canvas_tab3.create_line(i - 10, j, i + 10, j, fill="#5ce0ec", width=3)

        if self.tab3_in_canvas:
            x, y = self.last_hover_pos
            self.plot_canvas_tab3.create_line(x, 0, x, self.PA_tab3.h_canv, fill="#3daee9", width=2, dash=(15, 25))
            self.plot_canvas_tab3.create_line(0, y, self.PA_tab3.w_canv, y, fill="#3daee9", width=2, dash=(15, 25))

    def auto_Detect_Coordinate(self, event):
        if HAS_OCR is False:
            self.status_listbox.insert(END, "OCR Failed! Need Tesseract")
            return
        if not self.plot_anchored:
            self.status_listbox.insert(END, "Please Anchor Plot First")
            return

        w = self.PA_tab1.w_img
        h = self.PA_tab1.h_img

        x_area = int(self.canvas_click_posL[0][1] * h)
        y_area = int(self.canvas_click_posL[2][0] * w)

        rw = w - w % 32
        rh = h - h % 32
        img = PIL2OPENCV(self.PA_tab1.img)

        x_img = img[x_area:(x_area + 64), :]
        x_img = cv2.resize(x_img, (rw, 64))
        y_img = img[:, y_area-64:y_area]
        y_img = cv2.resize(y_img, (64, rh))

        (xh,xw) = x_img.shape[:2]
        (yh,yw) = y_img.shape[:2]

        rWx = w/rw
        rHx = 1

        # define the two output layer names for the EAST detector model that
        # we are interested -- the first is the output probabilities and the
        # second can be used to derive the bounding box coordinates of text
        layerNames = [
            "feature_fusion/Conv_7/Sigmoid",
            "feature_fusion/concat_3"]

        # load the pre-trained EAST text detector
        print("[INFO] loading EAST text detector...")
        self.status_listbox.insert(END, "OCR in progress...")
        net = cv2.dnn.readNet("frozen_east_text_detection.pb")

        # construct a blob from the image and then perform a forward pass of
        # the model to obtain the two output layer sets
        blob = cv2.dnn.blobFromImage(x_img, 1.0, (xw, xh),(123.68, 116.78, 103.94), swapRB=True, crop=False)
        net.setInput(blob)
        (scores, geometry) = net.forward(layerNames)

        # decode the predictions, then  apply non-maxima suppression to
        # suppress weak, overlapping bounding boxes
        (rects, confidences) = decode_predictions(scores, geometry, False)
        boxes = non_max_suppression(np.array(rects), probs=confidences)
        # boxes = np.array(rects)
        # initialize the list of results
        results = []

        orig = x_img.copy()
        # loop over the bounding boxes
        for (startX, startY, endX, endY) in boxes:
            # scale the bounding box coordinates based on the respective
            # ratios
            startX = int(startX * rWx)
            startY = int(startY * rHx)
            endX = int(endX * rWx)
            endY = int(endY * rHx)

            # in order to obtain a better OCR of the text we can potentially
            # apply a bit of padding surrounding the bounding box -- here we
            # are computing the deltas in both the x and y directions
            dX = int((endX - startX) * 0.03)
            dY = int((endY - startY) * 0.03)

            # apply padding to each side of the bounding box, respectively
            startX = max(0, startX - dX)
            startY = max(0, startY - dY)
            endX = min(w, endX + (dX * 2))
            endY = min(64, endY + (dY * 2))

            # extract the actual padded ROI
            roi = orig[startY:endY, startX:endX]

            # in order to apply Tesseract v4 to OCR text we must supply
            # (1) a language, (2) an OEM flag of 4, indicating that the we
            # wish to use the LSTM neural net model for OCR, and finally
            # (3) an OEM value, in this case, 7 which implies that we are
            # treating the ROI as a single line of text
            config = ("-l eng --oem 1 --psm 7")
            text = pytesseract.image_to_string(roi, config=config)

            # add the bounding box coordinates and OCR'd text to the list
            # of results
            results.append(((startX, startY, endX, endY), text))

        # sort the results bounding box coordinates from top to bottom
        results = sorted(results, key=lambda r: r[0][1])

        # loop over the results
        for ((startX, startY, endX, endY), text) in results:
            # display the text OCR'd by Tesseract
            print("OCR TEXT")
            print("========")
            print("{}\n".format(text))

            # strip out non-ASCII text so we can draw the text on the image
            # using OpenCV, then draw the text and a bounding box surrounding
            # the text region of the input image
            text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
            output = orig.copy()
            cv2.rectangle(output, (startX, startY), (endX, endY),
                          (0, 0, 255), 2)
            cv2.putText(output, text, (startX, startY - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            # show the output image
            cv2.imshow("Text Detection", output)
            cv2.waitKey(0)

        cv2.imshow("x", x_img)
        cv2.waitKey(0)

        cv2.imshow("y", y_img)
        cv2.waitKey(0)

    def anchor_Plot(self, event):

        self.plot_anchoring = True
        self.canvas_tooltip_num = 0
        self.PA_tab1.zoom_to_quadrant(qname='LL')
        self.status_listbox.insert(END, "Please Follow the Instructions on the Plot Area to Anchor Plot.")
        self.tab1_plot()

    def update_Value(self, event):
        if self.plot_anchored == False:
            self.status_listbox.insert(END, "Please Anchor Plot First")
            return

        xmin = self.xmin_entry.get()
        xmax = self.xmax_entry.get()
        ymin = self.ymin_entry.get()
        ymax = self.ymax_entry.get()

        try:
            float(xmin)
            float(xmax)
            float(ymin)
            float(ymax)
        except:
            self.status_listbox.insert(END, "Please Check Your Input!")
            return

        # self.PA_tab1.set_ix_origin(self.canvas_click_eventL[0][0], float(xmin))
        # self.PA_tab1.set_imax_xmax(self.canvas_click_eventL[1][0], float(xmax))
        # self.PA_tab1.set_jy_origin(self.canvas_click_eventL[2][1], float(ymin))
        # self.PA_tab1.set_jmax_ymax(self.canvas_click_eventL[3][1], float(ymax))
        #
        # self.PA_tab3.set_ix_origin(self.canvas_click_eventL[0][0], float(xmin))
        # self.PA_tab3.set_imax_xmax(self.canvas_click_eventL[1][0], float(xmax))
        # self.PA_tab3.set_jy_origin(self.canvas_click_eventL[2][1], float(ymin))
        # self.PA_tab3.set_jmax_ymax(self.canvas_click_eventL[3][1], float(ymax))

        self.PA_tab3.fi_origin = self.canvas_click_posL[0][0]
        self.PA_tab3.set_x_origin(float(xmin))
        self.PA_tab3.fimax = self.canvas_click_posL[1][0]
        self.PA_tab3.set_x_max(float(xmax))
        self.PA_tab3.fj_origin = self.canvas_click_posL[2][1]
        self.PA_tab3.set_y_origin(float(ymin))
        self.PA_tab3.fjmax = self.canvas_click_posL[3][1]
        self.PA_tab3.set_y_max(float(ymax))

        self.status_listbox.insert(END,
                                   "Axes Values Updated!Xmin:{},Xmax:{},Ymin:{},Ymax:{}".format(xmin, xmax, ymin, ymax))

        pos_xmin, pos_xmax, pos_ymin, pos_ymax = self.canvas_click_posL

        xy_xmin = self.PA_tab3.get_xy_at_fifj(*pos_xmin)
        xy_xmax = self.PA_tab3.get_xy_at_fifj(*pos_xmax)
        xy_ymin = self.PA_tab3.get_xy_at_fifj(*pos_ymin)
        xy_ymax = self.PA_tab3.get_xy_at_fifj(*pos_ymax)

        x_err = xy_ymax[0] - xy_ymin[0]
        y_err = xy_xmax[1] - xy_xmin[1]

        pcent_x_err = abs(x_err) * 100.0 / max(abs(self.PA_tab3.x_origin), abs(self.PA_tab3.xmax))
        pcent_y_err = abs(y_err) * 100.0 / max(abs(self.PA_tab3.y_origin), abs(self.PA_tab3.ymax))

        self.status_listbox.insert(END,
                                   "Distortion Error: Xerr=%g%%, Yerr=%g%%" % (pcent_x_err, pcent_y_err))

    def tab1_Zoomin(self, event):
        self.PA_tab1.zoom_in(zoom_factor=0.1)
        self.tab1_plot()

    def tab1_Zoomout(self, event):
        self.PA_tab1.zoom_out(zoom_factor=0.1)
        self.tab1_plot()

    def tab1_Fit(self, event):
        self.image_Fit()

    def image_Fit(self):
        self.PA_tab1.fit_img_on_canvas()
        self.tab1_plot()

    def tab3_Zoomin(self, event):
        self.PA_tab3.zoom_in(zoom_factor=0.1)
        self.tab3_plot()

    def tab3_Zoomout(self, event):
        self.PA_tab3.zoom_out(zoom_factor=0.1)
        self.tab3_plot()

    def tab3_Fit(self, event):
        self.PA_tab3.fit_img_on_canvas()
        self.tab3_plot()

    def auto_Align(self, event):
        if self.current_img is None:
            self.status_listbox.insert(END, "Please Import Your Image First!")
            return
        img = PIL2OPENCV(self.current_img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gaussian = cv2.GaussianBlur(gray, (3, 3), 0)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edged = cv2.Canny(gaussian, 80, 180, apertureSize=3)
        openededge = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        openededge = cv2.morphologyEx(openededge, cv2.MORPH_CLOSE, kernel)
        print(img.shape)

        # Hough Transform
        lines = cv2.HoughLines(openededge, 1, np.pi / 180, int(0.55 * min(gray.shape[1], gray.shape[0])))
        counterh = 0
        counterv = 0
        ptsv = []
        ptsh = []
        result = img.copy()
        if lines is None:
            self.status_listbox.insert(END, "Auto Align Failed!")
            return

        for line in lines:
            rho = line[0][0]
            theta = line[0][1]
            # print(rho)
            # print(theta)
            if (theta < (np.pi / 8.)) or (theta > (7. * np.pi / 8.0)):
                if counterv == 0:
                    pt1 = (int(rho / np.cos(theta)), 0)
                    pt2 = (int((rho - result.shape[0] * np.sin(theta)) / np.cos(theta)), result.shape[0])
                    ptsv.append([pt1, pt2])
                    # cv2.line( result, pt1, pt2, (0,255,0),2)
                    counterv = counterv + 1
                else:
                    pt1 = (int(rho / np.cos(theta)), 0)
                    pt2 = (int((rho - result.shape[0] * np.sin(theta)) / np.cos(theta)), result.shape[0])
                    if (abs(ptsv[counterv - 1][0][0] - pt1[0]) > 5 or abs(ptsv[counterv - 1][1][0] - pt2[0]) > 5):
                        ptsv.append([pt1, pt2])
                        # cv2.line( result, pt1, pt2, (0,255,0),2)
                        counterv = counterv + 1
                    else:
                        ptsv[counterv - 1] == [(int(0.5 * (ptsv[counterv - 1][0][0] + pt1[0])),
                                                int(0.5 * (ptsv[counterv - 1][0][1] + pt1[1]))), (
                                                   int(0.5 * (ptsv[counterv - 1][1][0] + pt2[0])),
                                                   int(0.5 * (ptsv[counterv - 1][1][1] + pt2[1])))]



            elif ((3 * np.pi / 8.) < theta < (5 * np.pi / 8.)):
                if counterh == 0:
                    pt1 = (0, int(rho / np.sin(theta)))
                    pt2 = (result.shape[1], int((rho - result.shape[1] * np.cos(theta)) / np.sin(theta)))
                    ptsh.append([pt1, pt2])
                    # cv2.line( result, pt1, pt2, (0,255,0),2)
                    counterh = counterh + 1
                else:
                    pt1 = (0, int(rho / np.sin(theta)))
                    pt2 = (result.shape[1], int((rho - result.shape[1] * np.cos(theta)) / np.sin(theta)))
                    if (abs(ptsh[counterh - 1][0][1] - pt1[1]) > 5 or abs(ptsh[counterh - 1][1][1] - pt2[1]) > 5):
                        ptsh.append([pt1, pt2])
                        # cv2.line( result, pt1, pt2, (0,255,0),2)
                        counterh = counterh + 1
                    else:
                        ptsh[counterh - 1] == [(int(0.5 * (ptsh[counterh - 1][0][0] + pt1[0])),
                                                int(0.5 * (ptsh[counterh - 1][0][1] + pt1[1]))), (
                                                   int(0.5 * (ptsh[counterh - 1][1][0] + pt2[0])),
                                                   int(0.5 * (ptsh[counterh - 1][1][1] + pt2[1])))]
                # pt1 = (0,int(rho/np.sin(theta)))
                # pt2 = (result.shape[1], int((rho-result.shape[1]*np.cos(theta))/np.sin(theta)))
                # cv2.line(result, pt1, pt2, (0,0,255),2)
                # counterh = counterh+1

        # print(counterh, counterv)
        # print(ptsv)
        # print(ptsh)
        if counterh < 2 or counterv < 2:
            self.status_listbox.insert(END, "Auto Align Failed!")
            return
        ptsv_sorted = sorted(ptsv, key=lambda b: b[0][0])
        ptsh_sorted = sorted(ptsh, key=lambda b: b[0][1], reverse=True)
        UL = cross_point(ptsv_sorted[0], ptsh_sorted[counterh - 1])
        UR = cross_point(ptsv_sorted[counterv - 1], ptsh_sorted[counterh - 1])
        LL = cross_point(ptsv_sorted[0], ptsh_sorted[0])
        LR = cross_point(ptsv_sorted[counterv - 1], ptsh_sorted[0])
        result2 = img.copy()
        cv2.line(result2, UL, UR, (219, 199, 173), 4)
        cv2.line(result2, LL, LR, (219, 199, 173), 4)
        cv2.line(result2, UL, LL, (219, 199, 173), 4)
        cv2.line(result2, UR, LR, (219, 199, 173), 4)
        cv2.circle(result2, UL, 7, (237, 226, 92), -1)
        cv2.circle(result2, LL, 7, (237, 226, 92), -1)
        cv2.circle(result2, UR, 7, (237, 226, 92), -1)
        cv2.circle(result2, LR, 7, (237, 226, 92), -1)

        dialog_img = fix_plot_img(UL, UR, LR, LL, OPENCV2PIL(result2))
        result = fix_plot_img(UL, UR, LR, LL, self.current_img)

        dialog = _AutoAlign(self.master, "Please Check the Auto Align Result", \
                            dialogOptions={'img': dialog_img})
        if dialog.result is 1:
            self.PA_tab1.set_img(result)
            self.PA_tab3.set_img(result)
            self.original_img = self.PA_tab1.img
            self.current_img = self.PA_tab1.img
            self.PA_tab1.set_img(self.current_img)
            self.Initialize_Image_State()
            self.status_listbox.insert(END, "Image Re-Aligned!")
        dialog.destroy()

    def points_Align(self, event):
        if self.image_imported == False:
            self.status_listbox.insert(END, "Please Import Your Image First!")
            return

        dialog = _ReAlign(self.master, "Re-Align Plot Axes (Make Orthogonal)", \
                          dialogOptions={'img': self.current_img, 'use_3_point': True})
        if dialog.result is not None:
            self.PA_tab1.set_img(dialog.result["img_fixed"])
            self.PA_tab3.set_img(dialog.result["img_fixed"])
            self.original_img = self.PA_tab1.img
            self.current_img = self.PA_tab1.img
            self.PA_tab1.set_img(self.current_img)
            self.Initialize_Image_State()
            self.status_listbox.insert(END, "Image Re-Aligned!")

        dialog.destroy()

    def save_Image(self, event):
        if self.current_img is None:
            return
        fileName = filedialog.asksaveasfilename(title='Save Current Image', filetypes=[('image', '*.jpg *.png')],
                                                defaultextension='.png')

        if fileName:
            self.current_img.save(fileName)
            self.status_listbox.insert(END, "Current Image Saved!")

    def tab1_Plot_Canvas_Resize(self, event):
        self.PA_tab1.set_canvas_wh(event.width, event.height)
        self.tab1_plot()

    def tab3_Plot_Canvas_Resize(self, event):
        self.PA_tab3.set_canvas_wh(event.width, event.height)
        self.tab3_plot()

    def tab1_Plot_Canvas_Click(self, event):
        if self.plot_anchoring is False:
            return

        x, y, fi, fj = self.PA_tab1.get_xyfifj_at_ij(event.x, event.y)

        if self.canvas_tooltip_num < 4:

            self.canvas_click_posL[self.canvas_tooltip_num] = self.PA_tab1.get_fifj_at_ij(event.x,
                                                                                          event.y)  # can detect img distortion
            self.canvas_click_eventL[self.canvas_tooltip_num] = (event.x, event.y)

            if self.canvas_tooltip_num == 0:
                # self.PA_tab1.zoom_to_quadrant(qname='LL')
                self.canvas_tooltip_num = self.canvas_tooltip_num + 1


            elif self.canvas_tooltip_num == 1:
                # self.PA_tab1.zoom_to_quadrant(qname='LR')
                self.canvas_tooltip_num = self.canvas_tooltip_num + 1

            elif self.canvas_tooltip_num == 2:
                # self.PA_tab1.zoom_to_quadrant(qname='LL')
                self.canvas_tooltip_num = self.canvas_tooltip_num + 1

            elif self.canvas_tooltip_num == 3:
                # self.PA_tab1.zoom_to_quadrant(qname='UL')
                self.canvas_tooltip_num = self.canvas_tooltip_num + 1
                self.PA_tab1.fit_img_on_canvas()
                self.canvas_tooltip_num = 10
                self.plot_anchoring = False
                self.plot_anchored = True
                print(self.canvas_click_posL)
                print(self.canvas_click_eventL)
                self.status_listbox.insert(END, "X Min,X Max,Y Min,Y Max Have Been Set!")

            if self.canvas_tooltip_num == 0:
                self.PA_tab1.zoom_to_quadrant(qname='LL')
            elif self.canvas_tooltip_num == 1:
                self.PA_tab1.zoom_to_quadrant(qname='LR')
            elif self.canvas_tooltip_num == 2:
                self.PA_tab1.zoom_to_quadrant(qname='LL')
            elif self.canvas_tooltip_num == 3:
                self.PA_tab1.zoom_to_quadrant(qname='UL')

            self.tab1_plot()




    def tab3_Plot_Canvas_Click(self, event):
        x, y, fi, fj = self.PA_tab3.get_xyfifj_at_ij(event.x, event.y)
        self.add_point(x, y, fi, fj)

    def add_point(self, x_float, y_float, fi, fj):

        self.has_some_new_data = True

        itemL = list(self.point_listbox.get(0, END))
        iL = [i for i in self.point_listbox.curselection()]

        if len(itemL) == 0:
            self.point_list.append(Point(x_float, y_float, fi, fj))
            self.point_listbox.insert(END, self.point_list[-1].get_str())
            self.select_point_list(0)
        else:

            if len(iL) == 0:
                self.point_list.append(Point(x_float, y_float, fi, fj))
                self.point_listbox.insert(END, self.point_list[-1].get_str())
                self.select_point_list(END)
            else:
                self.point_list.insert(iL[0] + 1, Point(x_float, y_float, fi, fj))
                self.point_listbox.insert(iL[0] + 1, self.point_list[iL[0] + 1].get_str())
                self.select_point_list(iL[0] + 1)

    def Sort_Button_Click(self, event):

        self.point_list.sort(key=lambda P: (P.x, P.y))

        # Clear entries in Listbox
        self.point_listbox.delete(0, END)

        for P in self.point_list:
            self.point_listbox.insert(END, P.get_str())

        self.point_listbox.select_set(END)
        self.tab3_plot()

    def Delete_All_Button_Click(self, event):
        if self.AskOK_Cancel(title='MyPlotDigitizer',
                             message='Do You Want to Delete All Data Points?'):
            self.point_listbox.delete(0, END)
            self.point_list = []
            self.has_some_new_data = False
            self.tab3_plot()

    def Del_Button_Click(self, event):

        iL = [i for i in self.point_listbox.curselection()]
        if len(iL) > 0:

            self.point_listbox.delete(iL[0])
            self.point_list.pop(iL[0])

            isel = iL[0] - 1
            if isel < 0:
                isel = 0
            if len(self.point_list) > 0:
                self.select_point_list(isel)

        self.tab3_plot()

    def select_point_list(self, i):

        self.point_listbox.selection_clear(0, END)
        if i == END:
            self.point_listbox.select_set(END)
            i = len(self.point_list) - 1
        else:
            self.point_listbox.select_set(i)

        self.tab3_plot()

    def detect_Curve(self, event):
        if len(self.point_list) < 4:
            message = 'You need to "rough-out" the curve\nto use Automatic Curve Detection.' + \
                      '\n\nRoughly pick at least 4 points along the curve\nand try again.'
            self.ShowError(title='Auto-Detect Error',
                           message=message)
            return

        dialog = _auto_detect(self.master, "Automatic Curve Detection", \
                              dialogOptions={'PA': self.PA_tab3, 'pointL': self.point_list})

        # print( dialog.result )

        if dialog.result is not None:
            new_point_list = dialog.result["calc_pointL"]
            replace_pts = dialog.result["replace_pts"]

            if replace_pts == 'yes':
                self.Delete_All_Button_Click(None)

            for x, y, fi, fj in new_point_list:
                self.add_point(x, y, fi, fj)

        dialog.destroy()

    def add_Errorbar(self, event):
        return

    def export_to_Excel(self, event):
        if len(self.point_list) == 0:
            self.ShowWarning(title='No Data Warning', message='No Data to put on Clipboard.')
            return

        self.frame.clipboard_clear()
        for P in self.point_list:
            self.frame.clipboard_append(P.get_str().replace(', ', '\t') + '\n')

    def export_to_Clipboard(self, event):
        if len(self.point_list) == 0:
            self.ShowWarning(title='No Data Warning', message='No Data to put on Clipboard.')
            return

        self.frame.clipboard_clear()
        for P in self.point_list:
            self.frame.clipboard_append(P.get_str() + '\n')

    def export_to_CSV(self, event):
        self.saveFile('*.csv')

    def saveFile(self, fileDesc='*.csv'):
        fsave = tkFileDialog.asksaveasfilename(parent=self.master, title='Saving CSV file',
                                               initialfile=fileDesc)

        if fsave:
            if fsave.find('.') < 0:
                fsave += '.csv'

            fOut = open(fsave, 'w')

            for P in self.point_list:
                fOut.write('%s\n' % P.get_str())
            fOut.close()

            self.has_some_new_data = False  # after successful save

    def tab1_MouseWheelHandler(self, event):
        if event.num == 5 or event.delta < 0:
            result = -1
            self.PA_tab1.zoom_into_ij(event.x, event.y, zoom_factor=0.1)
        else:
            result = 1
            self.PA_tab1.zoom_out_from_ij(event.x, event.y, zoom_factor=0.1)

        self.tab1_plot()

    def tab1_Canvas_Begin_End_Drag(self, event):
        self.tab1_is_dragging = not self.tab1_is_dragging
        ix = int(event.x)
        iy = int(event.y)

        self.last_right_click_pos = (ix, iy)

    def tab1_Canvas_Drag_Axes(self, event):
        di = self.last_right_click_pos[0] - event.x
        dj = self.last_right_click_pos[1] - event.y
        self.PA_tab1.adjust_offset(di, dj)

        self.last_right_click_pos = (event.x, event.y)

        self.tab1_plot()

    def tab1_Canvas_Enter(self, event):
        self.tab1_in_canvas = True
        self.tab1_plot()

    def tab1_Canvas_Hover(self, event):
        x = int(event.x)
        y = int(event.y)

        x_move, y_move = self.PA_tab1.get_xy_at_ij(x, y)

        self.last_hover_pos = (event.x, event.y)
        self.tab1_plot()

    def tab1_Canvas_Leave(self, event):
        self.tab1_in_canvas = False
        self.tab1_plot()

    def tab3_MouseWheelHandler(self, event):
        if event.num == 5 or event.delta < 0:
            result = -1
            self.PA_tab3.zoom_into_ij(event.x, event.y, zoom_factor=0.1)
        else:
            result = 1
            self.PA_tab3.zoom_out_from_ij(event.x, event.y, zoom_factor=0.1)

        self.tab3_plot()

    def tab3_Canvas_Begin_End_Drag(self, event):
        self.tab3_is_dragging = not self.tab3_is_dragging
        ix = int(event.x)
        iy = int(event.y)

        self.last_right_click_pos = (ix, iy)

    def tab3_Canvas_Drag_Axes(self, event):
        di = self.last_right_click_pos[0] - event.x
        dj = self.last_right_click_pos[1] - event.y
        self.PA_tab3.adjust_offset(di, dj)

        self.last_right_click_pos = (event.x, event.y)

        self.tab3_plot()

    def tab3_Canvas_Enter(self, event):
        self.tab3_in_canvas = True
        self.tab3_plot()

    def tab3_Canvas_Hover(self, event):
        x = int(event.x)
        y = int(event.y)

        x_move, y_move = self.PA_tab3.get_xy_at_ij(x, y)

        self.last_hover_pos = (event.x, event.y)
        self.tab3_plot()

    def tab3_Canvas_Leave(self, event):
        self.tab3_in_canvas = False
        self.tab3_plot()

    def xlog_checkbutton_StringVar_Callback(self, varName, index, mode):

        is_log = str(self.xlog_checkbutton_StringVar.get()) == 'yes'
        if is_log:
            self.PA_tab1.set_log_x()
            self.PA_tab3.set_log_x()
            # self.status_listbox.insert(END, "Set X Axis to Log Scale")
        else:
            self.PA_tab1.set_linear_x()
            self.PA_tab3.set_linear_x()
            # self.status_listbox.insert(END, "Set X Axis to Linear")

        self.tab1_plot()

    def ylog_checkbutton_StringVar_Callback(self, varName, index, mode):
        is_log = str(self.ylog_checkbutton_StringVar.get()) == 'yes'
        if is_log:
            self.PA_tab1.set_log_y()
            self.PA_tab3.set_log_y()
            # self.status_listbox.insert(END, "Set Y Axis to Log Scale")
        else:
            self.PA_tab1.set_linear_y()
            self.PA_tab3.set_linear_y()
            # self.status_listbox.insert(END, "Set Y Axis to Linear")

        self.tab1_plot()

    def grayscale_checkbutton_StringVar_Callback(self, varName, index, mode):
        return

    def enhancement_checkbutton_StringVar_Callback(self, varName, index, mode):
        if str(self.enhancement_checkbutton_StringVar.get()) == 'yes':
            self.option_list.append("enhancement")

        elif str(self.enhancement_checkbutton_StringVar.get()) == 'no':
            try:
                self.option_list.remove("enhancement")
            except:
                pass
        self.process_Image()

    def cleanbg_checkbutton_StringVar_Callback(self, varName, index, mode):
        if str(self.cleanbg_checkbutton_StringVar.get()) == 'yes':
            self.option_list.append("cleanbg")

        elif str(self.cleanbg_checkbutton_StringVar.get()) == 'no':
            try:
                self.option_list.remove("cleanbg")
            except:
                pass
        self.process_Image()

    def romovegrid_checkbutton_StringVar_Callback(self, varName, index, mode):
        if str(self.romovegrid_checkbutton_StringVar.get()) == 'yes':
            self.option_list.append("romovegrid")

        elif str(self.romovegrid_checkbutton_StringVar.get()) == 'no':
            try:
                self.option_list.remove("romovegrid")
            except:
                pass
        self.process_Image()

    def AskYesNo(self, title='Title', message='your question here.'):
        return tkMessageBox.askyesno(title, message)

    def AskOK_Cancel(self, title='Title', message='your question here.'):
        return tkMessageBox.askokcancel(title, message)

    def ShowError(self, title='Title', message='your message here.'):
        tkMessageBox.showerror(title, message)
        return

    def ShowWarning(self, title='Title', message='your message here.'):
        tkMessageBox.showwarning(title, message)
        return

    def point_listbox_Click(self, event):
        labelL = []
        for i in self.point_listbox.curselection():
            labelL.append(self.point_listbox.get(i))
        self.tab3_plot()

    def process_Image(self):
        if self.image_imported:
            # print(self.option_list)
            img = self.original_img.copy()
            # print(1)
            for option in self.option_list:
                if option == "enhancement":
                    # img = PIL2OPENCV(img)
                    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # fi = img / 255.0
                    # gamma = 0.4
                    # img = np.power(fi, gamma)
                    # img = OPENCV2PIL(img)
                    print(1)


                elif option == "cleanbg":
                    # img = self.current_img.copy()
                    w, h = img.size
                    pixels = img.getcolors(w * h)
                    most_frequent_pixel = pixels[0][1]
                    print(most_frequent_pixel)
                    datas = img.getdata()
                    new_image_data = []
                    for item in datas:
                        # change all white (also shades of whites) pixels to yellow
                        if item[0] in list(range(most_frequent_pixel[0] - 80, 256)) and item[1] in list(
                                range(most_frequent_pixel[1] - 80, 256)) and item[2] in list(
                            range(most_frequent_pixel[2] - 80, 256)):
                            new_image_data.append((255, 255, 255))
                        else:
                            new_image_data.append(item)
                    img.putdata(new_image_data)
                    # self.current_img = img

                elif option == "romovegrid":
                    w, h = img.size
                    pixels = img.getcolors(w * h)
                    most_frequent_pixel = pixels[0][1]
                    most_frequent_pixel_open = (most_frequent_pixel[2], most_frequent_pixel[1], [0])
                    img = PIL2OPENCV(img)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    gaussian = cv2.GaussianBlur(gray, (3, 3), 0)
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    edged = cv2.Canny(gaussian, 80, 180, apertureSize=3)
                    openededge = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
                    openededge = cv2.morphologyEx(openededge, cv2.MORPH_CLOSE, kernel)

                    # Hough Transform
                    lines = cv2.HoughLines(openededge, 1, np.pi / 180, int(0.45 * min(gray.shape[1], gray.shape[0])))
                    counterh = 0
                    counterv = 0
                    ptsv = []
                    ptsh = []
                    result = img.copy()
                    if lines is None:
                        return

                    for line in lines:
                        rho = line[0][0]
                        theta = line[0][1]
                        print(rho)
                        print(theta)
                        if (theta < (np.pi / 8.)) or (theta > (7. * np.pi / 8.0)):
                            if counterv == 0:
                                pt1 = (int(rho / np.cos(theta)), 0)
                                pt2 = (int((rho - result.shape[0] * np.sin(theta)) / np.cos(theta)), result.shape[0])
                                ptsv.append([pt1, pt2])
                                # cv2.line( result, pt1, pt2, (0,255,0),2)
                                counterv = counterv + 1
                            else:
                                pt1 = (int(rho / np.cos(theta)), 0)
                                pt2 = (int((rho - result.shape[0] * np.sin(theta)) / np.cos(theta)), result.shape[0])
                                if (abs(ptsv[counterv - 1][0][0] - pt1[0]) > 5 or abs(
                                        ptsv[counterv - 1][1][0] - pt2[0]) > 5):
                                    ptsv.append([pt1, pt2])
                                    # cv2.line( result, pt1, pt2, (0,255,0),2)
                                    counterv = counterv + 1
                                else:
                                    ptsv[counterv - 1] == [(int(0.5 * (ptsv[counterv - 1][0][0] + pt1[0])),
                                                            int(0.5 * (ptsv[counterv - 1][0][1] + pt1[1]))), (
                                                               int(0.5 * (ptsv[counterv - 1][1][0] + pt2[0])),
                                                               int(0.5 * (ptsv[counterv - 1][1][1] + pt2[1])))]



                        elif ((3 * np.pi / 8.) < theta < (5 * np.pi / 8.)):
                            if counterh == 0:
                                pt1 = (0, int(rho / np.sin(theta)))
                                pt2 = (result.shape[1], int((rho - result.shape[1] * np.cos(theta)) / np.sin(theta)))
                                ptsh.append([pt1, pt2])
                                # cv2.line( result, pt1, pt2, (0,255,0),2)
                                counterh = counterh + 1
                            else:
                                pt1 = (0, int(rho / np.sin(theta)))
                                pt2 = (result.shape[1], int((rho - result.shape[1] * np.cos(theta)) / np.sin(theta)))
                                if (abs(ptsh[counterh - 1][0][1] - pt1[1]) > 5 or abs(
                                        ptsh[counterh - 1][1][1] - pt2[1]) > 5):
                                    ptsh.append([pt1, pt2])
                                    # cv2.line( result, pt1, pt2, (0,255,0),2)
                                    counterh = counterh + 1
                                else:
                                    ptsh[counterh - 1] == [(int(0.5 * (ptsh[counterh - 1][0][0] + pt1[0])),
                                                            int(0.5 * (ptsh[counterh - 1][0][1] + pt1[1]))), (
                                                               int(0.5 * (ptsh[counterh - 1][1][0] + pt2[0])),
                                                               int(0.5 * (ptsh[counterh - 1][1][1] + pt2[1])))]
                    if counterh < 3 or counterv < 3:
                        return
                    ptsv_sorted = sorted(ptsv, key=lambda b: b[0][0])
                    ptsh_sorted = sorted(ptsh, key=lambda b: b[0][1], reverse=True)
                    for i in range(counterv - 2):
                        cv2.line(img, ptsv_sorted[i + 1][0], ptsv_sorted[i + 1][1], (255, 255, 255), 3)
                    for i in range(counterh - 2):
                        cv2.line(img, ptsh_sorted[i + 1][0], ptsh_sorted[i + 1][1], (255, 255, 255), 3)

                    img = OPENCV2PIL(img)

            self.current_img = img
            self.PA_tab1.set_img(img)
            self.PA_tab3.set_img(img)


def PIL2OPENCV(img):
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def OPENCV2PIL(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def main():
    root = ThemedTk(theme="breeze")
    # root = Tk()
    app = MyPlot(root)
    root.mainloop()


if __name__ == '__main__':
    main()
