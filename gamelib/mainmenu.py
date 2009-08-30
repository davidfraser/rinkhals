import pygame
from pgu import gui

class MainMenu(gui.Table):
    def __init__(self,**params):
        gui.Table.__init__(self,**params)

        def fullscreen_changed(btn):
            #pygame.display.toggle_fullscreen()
            print "TOGGLE FULLSCREEN"

        def stars_changed(slider):
            n = slider.value - len(stars)
            if n < 0:
                for i in range(n,0): 
                    stars.pop()
            else:
                for i in range(0,n):
                    stars.append([random.randrange(-W*span,W*span),
                                  random.randrange(-H*span,H*span),
                                  random.randrange(1,dist)])

        fg = (255,255,255)

        self.tr()
        self.td(gui.Label("Phil's Pygame GUI",color=fg),colspan=2)
        
        self.tr()
        self.td(gui.Label("Speed: ",color=fg),align=1)
        e = gui.HSlider(100,-500,500,size=20,width=100,height=16,name='speed')
        self.td(e)
        
        self.tr()
        self.td(gui.Label("Size: ",color=fg),align=1)
        e = gui.HSlider(2,1,5,size=20,width=100,height=16,name='size')
        self.td(e)
        
        self.tr()
        self.td(gui.Label("Quantity: ",color=fg),align=1)
        e = gui.HSlider(100,1,1000,size=20,width=100,height=16,name='quantity')
        e.connect(gui.CHANGE, stars_changed, e)
        self.td(e)
        
        self.tr()
        self.td(gui.Label("Color: ",color=fg),align=1)
        
        
        default = "#ffffff"
        color = gui.Color(default,width=64,height=10,name='color')
#         color_d = ColorDialog(default)

#         color.connect(gui.CLICK,color_d.open,None)
#         color_d.connect(gui.CHANGE,gui.action_setvalue,(color_d,color))
        self.td(color)
        
        btn = gui.Switch(value=False,name='fullscreen')
        btn.connect(gui.CHANGE, fullscreen_changed, btn)

        self.tr()
        self.td(gui.Label("Full Screen: ",color=fg),align=1)
        self.td(btn)
        
        self.tr()
        self.td(gui.Label("Warp Speed: ",color=fg),align=1)
        self.td(gui.Switch(value=False,name='warp'))
        
