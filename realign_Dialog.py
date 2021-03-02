
#!/usr/bin/env python
# -*- coding: ascii -*-
from __future__ import absolute_import
from __future__ import print_function

import sys, os

if sys.version_info < (3,):
    from future import standard_library
    standard_library.install_aliases()
    from tkSimpleDialog import Dialog
    import tkMessageBox
else:
    # this is only called incorrectly by pylint using python2
    from tkinter.simpledialog import Dialog
    import tkinter.messagebox as tkMessageBox


from tkinter import *

# Import Pillow:
from PIL import Image, ImageTk

from plot_area import PlotArea
import numpy

class _Dialog(Dialog):
    # use dialogOptions dictionary to set any values in the dialog
    def __init__(self, parent, title = None, dialogOptions=None):
        self.initComplete = 0
        self.dialogOptions = dialogOptions
        Dialog.__init__(self, parent, title)
        
        
class _ReAlign(_Dialog):

    def body(self, body):
        
        body.pack(padx=5, pady=5, fill=BOTH, expand=True) 
        
        dialogframe = Frame(body, width=663, height=627)
        dialogframe.pack(fill=BOTH, expand=YES, side=TOP)
        self.dialogframe = dialogframe

        lbframe = Frame( dialogframe )
        self.Canvas_1_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Canvas_1 = Canvas(lbframe, width="600", height="600", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.Canvas_1.yview)
        #scrollbar.pack(side=RIGHT, fill=Y)
        self.Canvas_1.pack(side=LEFT, fill=BOTH, expand=YES)
        lbframe.pack(fill=BOTH, expand=YES, side=TOP)

        self.Canvas_1.bind("<ButtonRelease-1>", self.Canvas_1_Click)

        
        # Mouse Wheel for Zooming in and out
        self.Canvas_1.bind("<MouseWheel>",self.MouseWheelHandler) # Windows Binding
        self.Canvas_1.bind("<Button-4>",self.MouseWheelHandler) # Linux Binding
        self.Canvas_1.bind("<Button-5>",self.MouseWheelHandler) # Linux Binding   

        self.Canvas_1.bind('<Up>', self.MakeBigger)
        self.Canvas_1.bind('<Down>', self.MakeSmaller)
        
        #body.unbind_all('<Escape>')
        self.Canvas_1.bind_all('<Key-1>', self.Key_Actions)
        self.Canvas_1.bind_all('<Key-2>', self.Key_Actions)
        self.Canvas_1.bind_all('<Key-3>', self.Key_Actions)
        self.Canvas_1.bind_all('<Key-4>', self.Key_Actions)

        
        self.Canvas_1.bind("<Button-3>", self.Canvas_Begin_End_Drag)
        self.Canvas_1.bind("<B3-Motion>", self.Canvas_Drag_Axes)
        self.Canvas_1.bind("<Motion>", self.Canvas_Hover)
        self.Canvas_1.bind("<Enter>", self.Canvas_Enter)
        self.Canvas_1.bind("<Leave>", self.Canvas_Leave)
        
        self.Canvas_1.bind("<Configure>", self.Canvas_1_Resize)
        
        self.resizable(1,1) # Linux may not respect this
        # >>>>>>insert any user code below this comment for section "top_of_init"
        
        self.Canvas_1.focus_set()

        self.PA = PlotArea(w_canv=600, h_canv=600) # will hold PlotArea() when it is opened
        
        # use a copy of submitted image
        self.PA.set_img( self.dialogOptions['img'].copy() )
        
        self.is_dragging = False
        self.last_right_click_pos = (0,0) # any action calling Canvas_Find_Closest will set

        self.last_hover_pos = (0,0)
        self.in_canvas = False

        self.canvas_tooltip_num = 0
        self.canvas_tooltip_inc = 1 # set > 1 to skip some options
        self.canvas_tooltip_strL = ['Left Click Upper Left.', 'Left Click Upper Right',
                                    'Left Click Lower Right.', 'Left Click Lower Left']
        # Units NEED to be fraction of img
        self.canvas_click_posL = [None, None, None, None] # only useful if all None's replaced
        
        if self.dialogOptions.get('use_3_point',False):
            self.canvas_click_posL[1] = (1000, 1000)
        
        self.is_first_display = True
        self.all_done = False
        

    def Key_Actions(self, event):
        #print('event.char =',event.char)
        if event.char=='1':
            self.PA.zoom_to_quadrant(qname='UL')
        elif event.char=='2':
            self.PA.zoom_to_quadrant(qname='UR')
        elif event.char=='3':
            self.PA.zoom_to_quadrant(qname='LR')
        elif event.char=='4':
            self.PA.zoom_to_quadrant(qname='LL')
            
        self.fill_canvas()

    def MakeBigger(self, event):
        #print('MakeBigger')
        self.PA.zoom_in(zoom_factor=0.1)
        self.fill_canvas()
        
    def MakeSmaller(self, event):
        #print('MakeSmaller')
        self.PA.zoom_out(zoom_factor=0.1)
        self.fill_canvas()

    def fill_canvas(self):
        if self.all_done:
            return
        
        if self.is_first_display:
            self.PA.zoom_to_quadrant(qname='UL')
            self.is_first_display = False
        
        # make coordinate axes
        try:
            self.Canvas_1.delete("all")
        except:
            pass
        
        # Place click directions onto canvas
        if self.canvas_tooltip_num < len(self.canvas_tooltip_strL):
            tt_str = self.canvas_tooltip_strL[ self.canvas_tooltip_num ]
        else:
            tt_str = ''
        
        self.photo_image = self.PA.get_tk_photoimage(greyscale=True, text=tt_str)
        self.Canvas_1.create_image(0,0, anchor=NW, image=self.photo_image )
        

        # Show cross-hairs for picking axis points
        if self.in_canvas:
            x,y = self.last_hover_pos
            self.Canvas_1.create_line(x, 0, x, self.PA.h_canv, fill="#3daee9", width=2, dash=(15, 25))
            self.Canvas_1.create_line(0, y, self.PA.w_canv, y, fill="#3daee9", width=2, dash=(15, 25))

        

    def Canvas_1_Resize(self, event):
        #w_canv = int( self.Canvas_1.winfo_width() )
        #h_canv = int( self.Canvas_1.winfo_height() )
        #if w_canv>0 and h_canv>0:
            
        self.PA.set_canvas_wh(event.width, event.height)
        self.fill_canvas()

    def MouseWheelHandler(self, event):
        #print('MouseWheelHandler event.num =', event.num)

        if event.num == 5 or event.delta < 0:
            result = -1 
            #self.PA.zoom_in(zoom_factor=0.1)
            self.PA.zoom_into_ij(event.x, event.y, zoom_factor=0.1)
        else:
            result = 1 
            #self.PA.zoom_out(zoom_factor=0.1)
            self.PA.zoom_out_from_ij(event.x, event.y, zoom_factor=0.1)
            
        self.fill_canvas()

    def Canvas_Begin_End_Drag(self, event):
        
        self.is_dragging = not self.is_dragging
        ix = int(event.x)
        iy = int(event.y)
        
        self.last_right_click_pos = (ix, iy)
        

    def Canvas_Drag_Axes(self, event):
        
        di = self.last_right_click_pos[0] - event.x
        dj = self.last_right_click_pos[1] - event.y
        self.PA.adjust_offset(di, dj)
        
        self.last_right_click_pos = (event.x, event.y)
        
        self.fill_canvas()

    def Canvas_Enter(self, event):
        self.in_canvas = True
        self.fill_canvas()
                
        
    def Canvas_Leave(self, event):
        self.in_canvas = False
        self.fill_canvas()


    def Canvas_Hover(self, event):
            
        self.last_hover_pos = (event.x, event.y)
        self.fill_canvas()
            

    # tk_happy generated code. DO NOT EDIT THE FOLLOWING. section "compID=2"
    def Canvas_1_Click(self, event): #click method for component ID=2
        pass
        # >>>>>>insert any user code below this comment for section "compID=2"
        # replace, delete, or comment-out the following
        #print("executed method Canvas_1_Click")
        #print("clicked in canvas at x,y =",event.x,event.y)
        #w = int(self.Canvas_1.cget("width"))
        #h = int(self.Canvas_1.cget("height"))
        
        w = int(self.Canvas_1.winfo_width())
        h = int(self.Canvas_1.winfo_height())

        if self.canvas_tooltip_num < len(self.canvas_tooltip_strL):
            tt_str = self.canvas_tooltip_strL[ self.canvas_tooltip_num ]
            
            # For Now, units are fi,fj
            fi, fj = self.PA.get_fifj_at_ij(event.x, event.y)
            self.canvas_click_posL[self.canvas_tooltip_num] = \
                        (self.PA.get_img_i_from_img_fi(fi),  \
                         self.PA.get_img_j_from_img_fj(fj) )
            
            if self.canvas_tooltip_num==0:
                self.title("Upper Left = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                
                if self.dialogOptions.get('use_3_point',False):
                    self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==1:
                self.title("Upper Right = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==2:
                self.title("Lower Right = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                
            elif self.canvas_tooltip_num==3:
                self.title("Lower Left = " + str(self.canvas_click_posL[self.canvas_tooltip_num]))
                self.canvas_tooltip_num += self.canvas_tooltip_inc
                    
                
            
            self.canvas_tooltip_inc = 1 # Just in case it is >1 for single options

        
            if self.canvas_tooltip_num==0:
                self.PA.zoom_to_quadrant(qname='UL')
            elif self.canvas_tooltip_num==1:
                self.PA.zoom_to_quadrant(qname='UR')
            elif self.canvas_tooltip_num==2:
                self.PA.zoom_to_quadrant(qname='LR')
            elif self.canvas_tooltip_num==3:
                self.PA.zoom_to_quadrant(qname='LL')
            else:
                self.PA.fit_img_on_canvas()


            if not None in self.canvas_click_posL:
                UL, UR, LR, LL = self.canvas_click_posL
                
                # May need to assume that UR is assumed to be a rotation
                if self.dialogOptions.get('use_3_point',False):
                    di = LR[0] - LL[0]
                    dj = LR[1] - LL[1]
                    UR = (UL[0]+di, UL[1]+dj)
                
                print('UL, UR, LR, LL =',UL, UR, LR, LL)
                self.img_fixed = fix_plot_img( UL, UR, LR, LL, self.PA.img)
                self.PA.set_img( self.img_fixed )
                
                self.ShowInfo( title='Image Is Realigned', message='''Use Cross-Hairs to examine orthogonality
                If satisfied, hit "OK" button on main screen.''')
                
            
            self.fill_canvas()
                

    # standard message dialogs... showinfo, showwarning, showerror
    def ShowInfo(self, title='Title', message='your message here.'):
        tkMessageBox.showinfo( title, message )
        return
        

    # tk_happy generated code. DO NOT EDIT THE FOLLOWING. section "dialog_validate"
    def validate(self):
        self.result = {} # return a dictionary of results
        
        #self.Canvas_1.unbind_all('<Key>')
        self.all_done = True
        
        self.result["img_fixed"] = self.img_fixed.copy()
        return 1
# tk_happy generated code. DO NOT EDIT THE FOLLOWING. section "end"


    def apply(self):
        #print('apply called')
        pass


class _AutoAlign(_Dialog):

    def body(self, body):

        body.pack(padx=5, pady=5, fill=BOTH, expand=True)

        dialogframe = Frame(body, width=663, height=627)
        dialogframe.pack(fill=BOTH, expand=YES, side=TOP)
        self.dialogframe = dialogframe

        lbframe = Frame(dialogframe)
        self.Canvas_1_frame = lbframe
        self.Canvas_1 = Canvas(lbframe, width="600", height="600")
        self.Canvas_1.pack(side=LEFT, fill=BOTH, expand=YES)
        lbframe.pack(fill=BOTH, expand=YES, side=TOP)


        # Mouse Wheel for Zooming in and out
        self.Canvas_1.bind("<MouseWheel>", self.MouseWheelHandler)  # Windows Binding
        self.Canvas_1.bind("<Button-4>", self.MouseWheelHandler)  # Linux Binding
        self.Canvas_1.bind("<Button-5>", self.MouseWheelHandler)  # Linux Binding

        self.Canvas_1.bind('<Up>', self.MakeBigger)
        self.Canvas_1.bind('<Down>', self.MakeSmaller)


        self.Canvas_1.bind("<Button-3>", self.Canvas_Begin_End_Drag)
        self.Canvas_1.bind("<B3-Motion>", self.Canvas_Drag_Axes)
        self.Canvas_1.bind("<Motion>", self.Canvas_Hover)
        self.Canvas_1.bind("<Enter>", self.Canvas_Enter)
        self.Canvas_1.bind("<Leave>", self.Canvas_Leave)

        self.Canvas_1.bind("<Configure>", self.Canvas_1_Resize)

        self.resizable(1, 1)  # Linux may not respect this
        # >>>>>>insert any user code below this comment for section "top_of_init"

        self.Canvas_1.focus_set()

        self.PA = PlotArea(w_canv=600, h_canv=600)  # will hold PlotArea() when it is opened

        self.PA.set_img(self.dialogOptions['img'].copy())

        self.is_dragging = False
        self.last_right_click_pos = (0, 0)  # any action calling Canvas_Find_Closest will set

        self.last_hover_pos = (0, 0)
        self.in_canvas = False


        self.is_first_display = True
        self.all_done = False



    def MakeBigger(self, event):
        # print('MakeBigger')
        self.PA.zoom_in(zoom_factor=0.1)
        self.fill_canvas()

    def MakeSmaller(self, event):
        # print('MakeSmaller')
        self.PA.zoom_out(zoom_factor=0.1)
        self.fill_canvas()

    def fill_canvas(self):
        if self.all_done:
            return


        # make coordinate axes
        try:
            self.Canvas_1.delete("all")
        except:
            pass


        self.photo_image = self.PA.get_tk_photoimage(greyscale=FALSE, text='')
        self.Canvas_1.create_image(0, 0, anchor=NW, image=self.photo_image)

        # Show cross-hairs for picking axis points
        if self.in_canvas:
            x, y = self.last_hover_pos
            self.Canvas_1.create_line(x, 0, x, self.PA.h_canv, fill="#3daee9", width=2, dash=(15, 25))
            self.Canvas_1.create_line(0, y, self.PA.w_canv, y, fill="#3daee9", width=2, dash=(15, 25))

    def Canvas_1_Resize(self, event):
        # w_canv = int( self.Canvas_1.winfo_width() )
        # h_canv = int( self.Canvas_1.winfo_height() )
        # if w_canv>0 and h_canv>0:

        self.PA.set_canvas_wh(event.width, event.height)
        self.fill_canvas()

    def MouseWheelHandler(self, event):
        # print('MouseWheelHandler event.num =', event.num)

        if event.num == 5 or event.delta < 0:
            result = -1
            # self.PA.zoom_in(zoom_factor=0.1)
            self.PA.zoom_into_ij(event.x, event.y, zoom_factor=0.1)
        else:
            result = 1
            # self.PA.zoom_out(zoom_factor=0.1)
            self.PA.zoom_out_from_ij(event.x, event.y, zoom_factor=0.1)

        self.fill_canvas()

    def Canvas_Begin_End_Drag(self, event):

        self.is_dragging = not self.is_dragging
        ix = int(event.x)
        iy = int(event.y)

        self.last_right_click_pos = (ix, iy)

    def Canvas_Drag_Axes(self, event):

        di = self.last_right_click_pos[0] - event.x
        dj = self.last_right_click_pos[1] - event.y
        self.PA.adjust_offset(di, dj)

        self.last_right_click_pos = (event.x, event.y)

        self.fill_canvas()

    def Canvas_Enter(self, event):
        self.in_canvas = True
        self.fill_canvas()

    def Canvas_Leave(self, event):
        self.in_canvas = False
        self.fill_canvas()

    def Canvas_Hover(self, event):

        self.last_hover_pos = (event.x, event.y)
        self.fill_canvas()

    def validate(self):
        self.result = 0

        # self.Canvas_1.unbind_all('<Key>')
        self.all_done = True

        self.result =1
        return 1



def find_coeffs(pa, pb):
    """
    pa and pb contain 4 corresponding points on image in order UL,UR,LR,LL
    UL=(0,0), UR=(w,0), LR=(w,h), LL=(0,h)

    Units for pa and pb are pixels.
    pa is target plane (e.g. [(0, 0), (256, 0), (256, 256), (0, 256)])
    pb is source plane (e.g. [(0, 0), (256, 0), (new_width, height), (xshift, height)])
    """
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

    A = numpy.matrix(matrix, dtype=numpy.float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    # take commenters advice to avoid A.T
    # res = numpy.linalg.solve(A, B)
    return numpy.array(res).reshape(8)


def fix_plot_img(UL, UR, LR, LL, img):
    """
    Correct plot so that xmin and xmax have same y value.
    And, ymin/ymax have same x value
    """

    # source points
    pb = [UL, UR, LR, LL]

    xlo = (LL[0] + UL[0]) / 2
    xhi = (UR[0] + LR[0]) / 2

    yhi = (UL[1] + UL[1]) / 2
    ylo = (LL[1] + LR[1]) / 2

    # make target points
    UL = (xlo, yhi)
    UR = (xhi, yhi)
    LR = (xhi, ylo)
    LL = (xlo, ylo)
    pa = [UL, UR, LR, LL]

    # get most common color in original
    w, h = img.size
    img_rgba = img.convert('RGBA')
    pixels = img_rgba.getcolors(w * h)
    most_frequent_pixel = pixels[0][1]
    print('For background, using most_frequent_pixel =',
          most_frequent_pixel)  # (count, (color))  e.g. (505888, (255, 255, 255, 255))

    # fix original image (may have black corners from rotation/transform)
    coeffs = find_coeffs(pa, pb)
    img_fixed = img_rgba.transform(img.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    fff = Image.new('RGBA', img_rgba.size, most_frequent_pixel)
    img_out = Image.composite(img_fixed, fff, img_fixed)

    return img_out


def cross_point(line1, line2):
    x1 = line1[0][1]  # ?????
    y1 = line1[0][0]
    x2 = line1[1][1]
    y2 = line1[1][0]

    x3 = line2[0][1]
    y3 = line2[0][0]
    x4 = line2[1][1]
    y4 = line2[1][0]

    k1 = (y2 - y1) * 1.0 / (x2 - x1)  # ??k1,?????????????????
    b1 = y1 * 1.0 - x1 * k1 * 1.0  # ?????????
    if (x4 - x3) == 0:  # L2?????????
        k2 = None
        b2 = 0
    else:
        k2 = (y4 - y3) * 1.0 / (x4 - x3)  # ??????
        b2 = y3 * 1.0 - x3 * k2 * 1.0
    if k2 == None:
        x = x3
    else:
        x = (b2 - b1) * 1.0 / (k1 - k2)
    y = k1 * x * 1.0 + b1 * 1.0
    return (int(y), int(x))
