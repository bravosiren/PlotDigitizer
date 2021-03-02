#!/usr/bin/env python
# -*- coding: ascii -*-
"""
Inspired by DigiPlot_Charlie Taylor
"""
from __future__ import absolute_import
from __future__ import print_function

import math
import sys
from PIL import Image, ImageTk, ImageFont, ImageDraw

try:
    from PIL import ImageGrab

    HAS_IMAGEGRAB = True
except:
    HAS_IMAGEGRAB = False

if sys.version_info < (3,):
    from cStringIO import StringIO
else:
    from io import BytesIO as StringIO
import os
from pics import TEST_IMAGE

here = os.path.abspath(os.path.dirname(__file__))
font_path = os.path.join(here, 'fonts', 'AdelleSansPE-Regular.OTF')

freefont10 = ImageFont.truetype(font_path, 10)
freefont16 = ImageFont.truetype(font_path, 16)
freefont24 = ImageFont.truetype(font_path, 24)
freefont36 = ImageFont.truetype(font_path, 36)
freefont48 = ImageFont.truetype(font_path, 48)
freefont72 = ImageFont.truetype(font_path, 72)


def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n


class PlotArea(object):
    """
    Logic for interpreting a plot image on a display canvas.
    The image can be zoomed and panned within the canvas area.
    The image is ALWAYS displayed at UL corner (0,0), but can be at many zoom/pan levels.

    fi,fj are the fractional i,j locations within the original image. (value = 0.0 to 1.0)
    """

    def __init__(self, w_canv=1000, h_canv=1000):
        self.w_canv = w_canv
        self.h_canv = h_canv

        test_img_data = TEST_IMAGE
        self.img = Image.open(StringIO(test_img_data))
        self.w_img, self.h_img = self.img.size

        self.calc_nominal_zoom()

        self.fi_origin = 0.0
        self.fj_origin = 1.0  # lower left
        self.fimax = 1.0
        self.fjmax = 0.0

        self.fi_offset = 0.0  # when upper left of canvas is not upper left of image
        self.fj_offset = 0.0

        self.x_origin = 0.0  # units on the image plot
        self.y_origin = 0.0  # units on the image plot
        self.xmax = 10.0  # units on the image plot
        self.ymax = 10.0  # units on the image plot

        self.log_x = False
        self.log_y = False

        self.log10_x_origin = 1.0  # units on the image plot
        self.log10_y_origin = 1.0  # units on the image plot
        self.log10_xmax = 2.0  # units on the image plot
        self.log10_ymax = 2.0  # units on the image plot

    def set_log_x(self):
        self.log_x = True
        if self.x_origin <= 0.0:
            self.x_origin = 0.1
        self.log10_x_origin = math.log10(self.x_origin)

    def set_linear_x(self):
        self.log_x = False

    def set_log_y(self):
        self.log_y = True
        if self.y_origin <= 0.0:
            self.y_origin = 0.1
        self.log10_y_origin = math.log10(self.y_origin)

    def set_linear_y(self):
        self.log_y = False

    def set_fraction_offset(self, fi=0.0, fj=0.0):

        # calc max values to limit setting
        i_img_shown = min(self.w_img, self.w_canv / self.img_zoom)
        j_img_shown = min(self.h_img, self.h_canv / self.img_zoom)

        fi_off_max = clamp(1.0 - float(i_img_shown) / float(self.w_img), 0., 1.)
        fj_off_max = clamp(1.0 - float(j_img_shown) / float(self.h_img), 0., 1.)
        # print('fi_off_max=%g, fj_off_max=%g, fi=%g, fj=%g'%(fi_off_max, fj_off_max, fi, fj))

        self.fi_offset = clamp(fi, 0., fi_off_max)  # when upper left of canvas is not upper left of image
        self.fj_offset = clamp(fj, 0., fj_off_max)

    def set_canvas_wh(self, w_canv, h_canv):
        self.w_canv = w_canv
        self.h_canv = h_canv
        self.calc_nominal_zoom()

    def set_zoom(self, new_zoom):
        self.img_zoom = max(new_zoom, self.fit_img_zoom)

    def zoom_in(self, zoom_factor=0.1):
        self.set_zoom(self.img_zoom * (1.0 + zoom_factor))

    def zoom_out(self, zoom_factor=0.1):
        self.set_zoom(self.img_zoom / (1.0 + zoom_factor))

    def zoom_to_quadrant(self, qname='UL'):

        x_zoom = float(self.w_canv) / float(self.w_img)
        y_zoom = float(self.h_canv) / float(self.h_img)
        self.img_zoom = max(x_zoom, y_zoom) * 1.5

        qname = qname.upper()
        if qname == 'UL':
            self.set_fraction_offset(fi=0.0, fj=0.0)
        elif qname == 'UR':
            self.set_fraction_offset(fi=1.0, fj=0.0)
        elif qname == 'LR':
            self.set_fraction_offset(fi=1.0, fj=1.0)
        elif qname == 'LL':
            self.set_fraction_offset(fi=0.0, fj=1.0)
        else:
            self.fit_img_on_canvas()

    def zoom_into_ij(self, i, j, zoom_factor=0.1):
        fi = self.get_img_fi_from_canvas_i(i)
        fj = self.get_img_fj_from_canvas_j(j)

        # fi_max = self.get_img_fi_from_canvas_i( self.w_canv )
        # fj_max = self.get_img_fj_from_canvas_j( self.h_canv )
        # print('fi_max=%g,  fj_max=%g'%(fi_max, fj_max))

        # Want new fi, fj same as old values but with new zoom factor
        self.set_zoom(self.img_zoom * (1.0 + zoom_factor))

        fi_new = self.get_img_fi_from_canvas_i(i)
        fj_new = self.get_img_fj_from_canvas_j(j)

        fi_final = self.fi_offset + fi - fi_new
        fj_final = self.fj_offset + fj - fj_new

        self.set_fraction_offset(fi=fi_final, fj=fj_final)

    def zoom_out_from_ij(self, i, j, zoom_factor=0.1):
        fi = self.get_img_fi_from_canvas_i(i)
        fj = self.get_img_fj_from_canvas_j(j)

        # Want new fi, fj same as old values but with new zoom factor
        self.set_zoom(self.img_zoom / (1.0 + zoom_factor))

        fi_new = self.get_img_fi_from_canvas_i(i)
        fj_new = self.get_img_fj_from_canvas_j(j)

        # self.fi_offset += fi - fi_new
        # self.fj_offset += fj - fj_new
        self.set_fraction_offset(fi=self.fi_offset + fi - fi_new, fj=self.fj_offset + fj - fj_new)

    def fit_img_on_canvas(self):
        self.calc_nominal_zoom()
        self.fi_offset = 0.0  # when upper left of canvas is not upper left of image
        self.fj_offset = 0.0

    def calc_nominal_zoom(self):
        x_zoom = float(self.w_canv) / float(self.w_img)
        y_zoom = float(self.h_canv) / float(self.h_img)
        self.img_zoom = min(x_zoom, y_zoom)

        self.fit_img_zoom = self.img_zoom

    def open_img_file(self, img_path):
        try:
            img = Image.open(img_path)
            w_img, h_img = img.size
            print('Opened image file:', img_path, '  size=', img.size)
            self.set_img(img)
            return True
        except:
            print('==========> Error opening image file:', img_path)
            return False

    def set_img_from_clipboard(self):
        if not HAS_IMAGEGRAB:
            return False

        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            self.set_img(img)
            return True
        else:
            print('WARNING... Pasting Clipboard Image Failed.')
            return False

    def set_img(self, img):

        self.img = img
        self.w_img, self.h_img = img.size

        self.calc_nominal_zoom()

        self.fi_origin = 0.0
        self.fj_origin = 1.0  # lower left
        self.fimax = 1.0
        self.fjmax = 0.0

        self.fi_offset = 0.0  # when upper left of canvas is not upper left of image
        self.fj_offset = 0.0

        self.x_origin = 0.0  # units on the image plot
        self.y_origin = 0.0  # units on the image plot
        self.xmax = 10.0  # units on the image plot
        self.ymax = 10.0  # units on the image plot

        self.log_x = False
        self.log_y = False

        self.log10_x_origin = 1.0  # units on the image plot
        self.log10_y_origin = 1.0  # units on the image plot
        self.log10_xmax = 2.0  # units on the image plot
        self.log10_ymax = 2.0  # units on the image plot

    def get_zoomed_offset_img(self, greyscale=False, text='', show_linlog_text=False):

        fi_min = max(0.0, self.get_img_fi_from_canvas_i(0))
        fi_max = min(1.0, self.get_img_fi_from_canvas_i(self.w_canv))
        fj_min = max(0.0, self.get_img_fj_from_canvas_j(0))
        fj_max = min(1.0, self.get_img_fj_from_canvas_j(self.h_canv))

        imin = int(self.w_img * fi_min)
        imax = int(self.w_img * fi_max)
        jmin = int(self.h_img * fj_min)
        jmax = int(self.h_img * fj_max)

        img_slice = self.img.crop((imin, jmin, imax, jmax))
        wz = int((imax - imin + 1) * self.img_zoom)
        hz = int((jmax - jmin + 1) * self.img_zoom)
        img_slice_resized = img_slice.resize((wz, hz), Image.ANTIALIAS)

        if (wz > self.w_canv) or (hz > self.h_canv):
            bbox = (0, 0, min(wz, self.w_canv), min(hz, self.h_canv))
            img_slice_resized = img_slice_resized.crop(bbox)
            # print('... bbox resized to:', bbox)

        if greyscale:
            img_slice_resized = img_slice_resized.convert('LA')

        # place text onto plot
        if text or show_linlog_text:
            # Make RGBA image to put text on
            img_slice_resized = img_slice_resized.convert('RGBA')
            w, h = img_slice_resized.size

            d = max(w, h)
            img_square = Image.new('RGBA', (d, d))
            draw = ImageDraw.Draw(img_square)

            def get_font_for_size(s, w_lim):
                myfont = freefont10
                for test_font in [freefont16, freefont24, freefont36, freefont48, freefont72]:
                    wtext, htext = test_font.getsize(s)
                    if wtext >= w_lim:
                        return myfont
                    myfont = test_font
                return myfont

            # yaxis text
            if show_linlog_text:
                if self.log_y:
                    ylab = 'log scale'
                    color = (200, 230, 243, 200)
                else:
                    ylab = ' '
                    color = (0, 255, 0, 120)  # green
                myfont = get_font_for_size('logear scale', min(w, h) / 2)
                di, dj = myfont.getsize(ylab)
                itxt = (h - di) / 2
                draw.text((itxt, d - dj), ylab, font=myfont, fill=color)

            # rotate image
            img_temp = img_square.rotate(270)
            img_new = img_temp.crop((0, 0, w, h))
            draw = ImageDraw.Draw(img_new)

            # xaxis text
            if show_linlog_text:
                if self.log_x:
                    xlab = 'log scale'
                    color = (200, 230, 243, 200)  # red
                else:
                    xlab = ' '
                    color = (0, 255, 0, 150)  # green
                di, dj = myfont.getsize(xlab)
                itxt = (w - di) / 2
                draw.text((itxt, h - dj), xlab, font=myfont, fill=color)

            # center text (if any)
            if text:
                myfont = get_font_for_size(text, w)
                di, dj = myfont.getsize(text)
                itxt = (w - di) / 2
                jtxt = (h - dj) / 2

                draw.text((itxt, jtxt), text, font=myfont, fill=(57, 69, 83, 90))  # magenta

            # img_slice_resized = Image.blend(img_slice_resized, img_new, 0.5)
            img_slice_resized = Image.alpha_composite(img_slice_resized, img_new)

        return img_slice_resized

    def get_tk_photoimage(self, greyscale=False, text='', show_linlog_text=False):
        img_slice_resized = self.get_zoomed_offset_img(greyscale=greyscale, text=text,
                                                       show_linlog_text=show_linlog_text)
        return ImageTk.PhotoImage(img_slice_resized)

    # def get_img_fi_from_canvas_i(self, i):
    #    i_zoom = self.w_img * self.fi_offset * self.img_zoom + i
    #    i_zoom_max = self.w_img * self.img_zoom
    #    return float(i_zoom) / float(i_zoom_max)

    def get_img_i_from_img_fi(self, fi):
        return self.w_img * fi

    def get_img_j_from_img_fj(self, fj):
        return self.h_img * fj

    def get_canvas_i_from_img_fi(self, fi):
        i_off_screen = self.w_img * self.fi_offset
        i_total = self.w_img * fi
        return (i_total - i_off_screen) * self.img_zoom

    def get_canvas_j_from_img_fj(self, fj):
        j_off_screen = self.h_img * self.fj_offset
        j_total = self.h_img * fj
        return (j_total - j_off_screen) * self.img_zoom

    def get_img_fi_from_canvas_i(self, i):
        """Given i on canvas, get fraction of img width that i corresponds to."""
        i_off_screen = self.w_img * self.fi_offset
        i_zoom = float(i) / self.img_zoom
        # i_zoom_max = self.w_img * self.img_zoom
        return float(i_off_screen + i_zoom) / float(self.w_img)

    def get_img_fj_from_canvas_j(self, j):
        """Given j on canvas, get fraction of img height that j corresponds to."""
        j_off_screen = self.h_img * self.fj_offset
        j_zoom = float(j) / self.img_zoom
        # j_zoom_max = self.h_img * self.img_zoom
        return float(j_off_screen + j_zoom) / float(self.h_img)

    def adjust_offset(self, di, dj):
        dfi = float(di) / self.img_zoom / float(self.w_img)
        dfj = float(dj) / self.img_zoom / float(self.h_img)

        # self.fi_offset = clamp( dfi+self.fi_offset, 0., 1.)
        # self.fj_offset = clamp( dfj+self.fj_offset, 0., 1.)
        self.set_fraction_offset(fi=self.fi_offset + dfi, fj=self.fj_offset + dfj)

    def define_origin_ij(self, i, j):
        """
        Place the origin of the 2D plot at image coordinates i,j.
        i and j are in pixel coordinates of the visible/zoomed portion of the canvas.
        """
        self.fi_origin = self.get_img_fi_from_canvas_i(i)
        self.fj_origin = self.get_img_fj_from_canvas_j(j)

    def set_origin_xy(self, x, y):
        self.set_x_origin(x)
        self.set_y_origin(y)

    def set_x_origin(self, x):
        self.x_origin = x
        if self.log_x and self.x_origin <= 0.0:
            self.x_origin = 0.1
        if self.log_x:
            self.log10_x_origin = math.log10(self.x_origin)

    def set_y_origin(self, y):
        self.y_origin = y
        if self.log_y and self.y_origin <= 0.0:
            self.y_origin = 0.1
        if self.log_y:
            self.log10_y_origin = math.log10(self.y_origin)

    def set_x_max(self, x):
        self.xmax = x
        if self.log_x and self.xmax <= 0.0:
            self.xmax = 10.0
        if self.log_x:
            self.log10_xmax = math.log10(self.xmax)

    def set_y_max(self, y):
        self.ymax = y
        if self.log_y and self.ymax <= 0.0:
            self.ymax = 10.0
        if self.log_y:
            self.log10_ymax = math.log10(self.ymax)

    def set_ix_origin(self, i, x):
        self.fi_origin = self.get_img_fi_from_canvas_i(i)
        self.set_x_origin(x)

    def set_jy_origin(self, j, y):
        self.fj_origin = self.get_img_fj_from_canvas_j(j)
        self.set_y_origin(y)

    def set_imax_xmax(self, imax, xmax):
        self.fimax = self.get_img_fi_from_canvas_i(imax)
        self.set_x_max(xmax)

    def set_jmax_ymax(self, jmax, ymax):
        self.fjmax = self.get_img_fj_from_canvas_j(jmax)
        self.set_y_max(ymax)

    def get_xy_at_fifj(self, fi, fj):

        di = fi - self.fi_origin
        dj = self.fj_origin - fj  # note LL vs UL

        if self.log_x:
            dx = self.log10_xmax - self.log10_x_origin
        else:
            dx = self.xmax - self.x_origin

        if self.log_y:
            dy = self.log10_ymax - self.log10_y_origin
        else:
            dy = self.ymax - self.y_origin

        try:
            if self.log_x:
                x = 10.0 ** (self.log10_x_origin + dx * di / (self.fimax - self.fi_origin))
            else:
                x = self.x_origin + dx * di / (self.fimax - self.fi_origin)

            if self.log_y:
                y = 10.0 ** (self.log10_y_origin + dy * dj / (self.fj_origin - self.fjmax))  # note LL vs UL
            else:
                y = self.y_origin + dy * dj / (self.fj_origin - self.fjmax)  # note LL vs UL

        except:
            return None, None

        return x, y

    def get_fifj_at_ij(self, i, j):
        fi = self.get_img_fi_from_canvas_i(i)
        fj = self.get_img_fj_from_canvas_j(j)
        return fi, fj

    def get_xy_at_ij(self, i, j):
        fi = self.get_img_fi_from_canvas_i(i)
        fj = self.get_img_fj_from_canvas_j(j)
        return self.get_xy_at_fifj(fi, fj)

    def get_xyfifj_at_ij(self, i, j):
        fi = self.get_img_fi_from_canvas_i(i)
        fj = self.get_img_fj_from_canvas_j(j)
        x, y = self.get_xy_at_fifj(fi, fj)
        return x, y, fi, fj

    def get_canvas_i(self, x_float):
        try:
            if self.log_x:
                x10 = math.log10(x_float)
                fx = (x10 - self.log10_x_origin) / (self.log10_xmax - self.log10_x_origin)
            else:
                fx = (x_float - self.x_origin) / (self.xmax - self.x_origin)
        except:
            return -1

        f_plot = self.fimax - self.fi_origin  # fraction of canvas holding plot
        i_plot = fx * f_plot * self.w_img * self.img_zoom  # i value into plot from origin
        i_offset = self.fi_offset * self.w_img * self.img_zoom
        i_origin = self.fi_origin * self.w_img * self.img_zoom

        i = int(i_plot - i_offset + i_origin)

        if i >= 0 and i <= self.w_canv:
            return i
        else:
            return -1  # if not on canvas

    def get_canvas_j(self, y_float):
        try:
            if self.log_y:
                y10 = math.log10(y_float)
                fy = (y10 - self.log10_y_origin) / (self.log10_ymax - self.log10_y_origin)
            else:
                fy = (y_float - self.y_origin) / (self.ymax - self.y_origin)
        except:
            return -1

        f_plot = self.fj_origin - self.fjmax  # fraction of canvas holding plot
        j_plot = fy * f_plot * self.h_img * self.img_zoom  # i value into plot from origin

        j_offset = self.fj_offset * self.h_img * self.img_zoom
        j_origin = self.fj_origin * self.h_img * self.img_zoom

        j = int(j_origin - j_offset - j_plot)
        if j >= 0 and j <= self.h_canv:
            return j
        else:
            return -1  # if not on canvas

    def get_ij_at_xy(self, x, y):

        i = self.get_canvas_i(x)
        j = self.get_canvas_j(y)
        if i >= 0 and j >= 0:
            return i, j
        else:
            return -1, -1  # if not on canvas

    def x_is_visible(self, x):
        return self.get_canvas_i(x) >= 0

    def y_is_visible(self, y):
        return self.get_canvas_j(y) >= 0

#Test
if __name__ == '__main__':
    PA = PlotArea(w_canv=600, h_canv=600)
    # PA.open_img_file( 'Cu_cte.png' )
    # PA.set_fraction_offset(fi=0.2, fj=0.3)
    # PA.zoom_out(zoom_factor=0.5)

    img_slice_resized = PA.get_zoomed_offset_img(greyscale=True, show_linlog_text=True)
    print('img_slice_resized.size=', img_slice_resized.size)
    img_slice_resized.save('test_img.png')

    PA.set_ix_origin(76, 0.0)
    PA.set_jy_origin(432, 0.0)

    PA.set_imax_xmax(540, 20.0)
    PA.set_jmax_ymax(48, 120.0)

    if 0:
        for x, i_exp in [(0., 76), (5., 190), (10., 306), (15., 424), (20., 540)]:
            print('x=%g,  i=%i, i_exp=%i' % (x, PA.get_canvas_i(x), i_exp))

        print('=' * 55)
        for y, j_exp in [(0., 432), (20., 369), (40., 304), (80., 177), (120., 49)]:
            print('y=%g,  j=%i, j_exp=%i' % (y, PA.get_canvas_j(y), j_exp))

        print()
        print('x,y at 306,304 =', PA.get_xy_at_ij(306, 304))
        print('x,y,fi,fj at 306,304 =', PA.get_xyfifj_at_ij(306, 304))
        print()
    else:
        print('=' * 20, ' Offset')
        PA.set_fraction_offset(fi=0.1, fj=0.1)

        for x, i_exp in [(0., 16), (5., 131), (10., 248), (15., 365), (20., 482)]:
            print('x=%g,  i=%i, i_exp=%i' % (x, PA.get_canvas_i(x), i_exp))

        print('=' * 55)
        for y, j_exp in [(0., 383), (20., 322), (40., 257), (80., 130), (120., 0)]:
            print('y=%g,  j=%i, j_exp=%i' % (y, PA.get_canvas_j(y), j_exp))

        print()
        print('x,y at 481,0 =', PA.get_xy_at_ij(481, 0))
        print('x,y,fi,fj at 481,0 =', PA.get_xyfifj_at_ij(481, 0))

        img_slice_resized = PA.get_zoomed_offset_img(greyscale=True, show_linlog_text=True)
        img_slice_resized.save('test_offset_img.png')
