import os
import tkinter
import tkinter.filedialog
import time


import platform
sys = platform.system()
if sys == "Linux":
    import pyscreenshot as ImageGrab
else:
    from PIL import ImageGrab

#Code For Screenshot

class FreeCapture():
    def __init__(self, root, img,screenWidth,screenHeight):
        self.finish = False
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)
        screenWidth = screenWidth
        screenHeight = screenHeight
        self.top = tkinter.Toplevel(root, width=screenWidth, height=screenHeight)
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top, bg='white', width=screenWidth, height=screenHeight)
        self.image = tkinter.PhotoImage(file=img)
        self.canvas.create_image(screenWidth // 2, screenHeight // 2, image=self.image)

        self.lastDraw = None

        def onLeftButtonDown(event):
            self.X.set(event.x)
            self.Y.set(event.y)
            self.sel = True

        self.canvas.bind('<Button-1>', onLeftButtonDown)

        def onLeftButtonMove(event):
            if not self.sel:
                return
            try:
                self.canvas.delete(self.lastDraw)
            except Exception as e:
                pass
            self.lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='#3daee9')

        def onLeftButtonUp(event):
            self.sel = False
            try:
                self.canvas.delete(self.lastDraw)
            except Exception as e:
                pass

            time.sleep(0.5)
            left, right = sorted([self.X.get(), event.x])
            top, bottom = sorted([self.Y.get(), event.y])
            pic = ImageGrab.grab((left + 1, top + 1, right, bottom))
            fileName = tkinter.filedialog.asksaveasfilename(title='Save', filetypes=[('image', '*.jpg *.png')],
                                                            defaultextension='.png')

            if fileName:
                pic.save(fileName)
            pic.save("temp_screenshot.png")
            pic.close()
            self.top.destroy()

        self.canvas.bind('<B1-Motion>', onLeftButtonMove)
        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)


def screenShot(self,screenWidth,screenHeight):
    time.sleep(0.2)
    im = ImageGrab.grab()
    im.save('temp.png')
    im.close()
    pic = FreeCapture(self, 'temp.png',screenWidth,screenHeight)
    os.remove('temp.png')

