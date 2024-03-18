from tkinter import *

from tkinter import filedialog
from collections import deque
from tkinter import messagebox
import sys
import os

from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.visualizer.visualizer import Visualizer
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources.opentrons.deck import OTDeck
from pylabrobot.resources import set_tip_tracking, set_volume_tracking
from pylabrobot.resources.opentrons import opentrons_96_tiprack_20ul, opentrons_96_tiprack_1000ul
from pylabrobot.resources import ( PLT_CAR_L5AC_A00, Cos_96_DW_1mL, HTF_L)
from pylabrobot.resources.opentrons import corning_96_wellplate_360ul_flat
from pylabrobot.resources.coordinate import Coordinate
from pylabrobot.resources.resource import Resource
from pylabrobot.resources.deck import Deck
from pylabrobot.resources.trash import Trash
from pylabrobot.resources.liquid import Liquid
from pylabrobot.resources.plate import Plate
from pylabrobot.resources.well import Well
from pylabrobot.resources.tip_rack import TipRack, TipSpot
from pylabrobot.resources.petri_dish import PetriDish, PetriDishHolder
from pylabrobot.resources.tube_rack import Tube
from pylabrobot.resources.tube_rack import TubeRack

from resourceCoordinates import ResourceCoordinates

class UiWindow:

    def ym(self, y:float)->float:
         return self.liquidHandler.deck._size_y-y
    
    def yGcode(self, y:float)->float:
         return -y+self.liquidHandler.deck._size_y

    def drawAll(self):
        self.drawResourceAndChildrenImages(self.liquidHandler.deck)

    # this takes the deck which is the top resource and visualize it and children on the screen  
    def drawResourceAndChildrenImages(self, r:Resource):
        self.createResourceImage(r)
        if len(r.children)>0:
            for child in r.children:
                if not isinstance(child,Resource):
                     print("!!!!!!!!!!!!!!!!WARNING child is not a resource", child.name)
                else:
                    self.drawResourceAndChildrenImages(child)

    def createResourceImage(self, r:Resource):
        # if self.firstDraw:
        #     print ("child:",r.name)
        #print(r.category)
        z=self.zoom
        if isinstance(r,Deck):
            self.createResourceShapes(r, theFillCol="orange")            
            # draw deck and slots
            for i in range(len(self.liquidHandler.deck.slot_locations)):
                slot=self.liquidHandler.deck.slot_locations[i]
                self.createRectangle(z*slot.x, z*slot.y, z*self.slotSizeX, z*self.slotSizeY, fillCol="slate grey", outlineCol="black")
                self.createRectangle(z*slot.x, z*slot.y, z*self.slotPocketSizeX, z*self.slotPocketSizeY, fillCol="light grey", outlineCol="light grey")
                self.canvas.create_text(z*slot.x+8, z*self.ym(slot.y)-8, text=str(i+1), fill="black", font=('Helvetica 10'))            
        elif isinstance(r,Trash):
            self.createResourceShapes(r, theFillCol="gray40")                      
        elif isinstance(r,TipRack):
            self.createResourceShapes(r, theFillCol="aquamarine")            
        elif isinstance(r,TipSpot):
            self.createResourceShapes(r, addCircle=True,theFillCol="white")            
        elif isinstance(r,Plate):
            self.createResourceShapes(r, theFillCol="cyan4")            
        elif isinstance(r,Well):
            self.createResourceShapes(r, addCircle=True,theFillCol="blue")          
        elif isinstance(r,TubeRack):
            self.createResourceShapes(r, theFillCol="red")    
        elif isinstance(r,Tube):
            self.createResourceShapes(r, addCircle=True,theFillCol="blue")    
        elif isinstance(r,PetriDishHolder):
            self.createResourceShapes(r, theFillCol="red")    
        elif isinstance(r,PetriDish):
            self.createResourceShapes(r, addCircle=True,theFillCol="blue") 
        elif isinstance(r,Resource) and r.name=="trash_container":
                self.createResourceShapes(r, theFillCol="black")     
        else:
            messagebox.showinfo("Found unknown type", type(r), r)

    def createResourceShapes(self,r:Resource, addCircle=False, theFillCol="peach puff",theOutlineCol="peach puff"):
        absX=r.get_absolute_location().x
        absY=r.get_absolute_location().y
        typeName=type(r).__name__
        if addCircle:
            self.canvas.create_oval(absX, self.ym(absY), r.get_absolute_location().x+r.get_size_x(), self.ym(absY)-r.get_size_y(), fill="white", outline=theOutlineCol)
        else:
            self.createRectangle(absX, absY, r.get_size_x(), r.get_size_y(), fillCol=theFillCol, outlineCol=theOutlineCol)
        if(self.firstDraw):
            self.screenElements.insert(0,ResourceCoordinates(absX,absY, r.get_size_x(), r.get_size_y(),r))
        if  isinstance(r,Plate) or isinstance(r,TipRack) or isinstance(r,Trash):
            self.canvas.create_text(r.get_absolute_location().x+r.get_size_x()/2, self.ym( r.get_absolute_location().y+6), text=r.name, fill="black", font=('Arial 8'))
            #self.canvas.create_text(r.get_absolute_location().x+r.get_size_x()/2, self.ym( r.get_absolute_location().y+8), text=r.name+str(type(r)), fill="red", font=('Helvetica 8'))
        if isinstance(r,PetriDish):
            self.canvas.create_text(r.get_absolute_location().x+2, self.ym( r.get_absolute_location().y+6), text=r.name, fill="black", font=('Arial 8'))
            #self.canvas.create_text(r.get_absolute_location().x+r.get_size_x()/2, self.ym( r.get_absolute_location().y+8), text=r.name+str(type(r)), fill="red", font=('Helvetica 8'))                
            if hasattr(r,"drops"):
                for drop in r.drops:
                    self.canvas.create_oval(drop[0]-1, self.ym(drop[1]-1), drop[0]+1, self.ym(drop[1]+1), fill="green", outline=theOutlineCol)
                
    def createRectangle(self, x0,y0,xSize,ySize, fillCol, outlineCol, widthBorder=0):
        #print("create rectangle at",x0, self.ym(y0), x0+xSize, self.ym(y0)-ySize,"of sizes:",xSize,ySize)
        self.canvas.create_rectangle(x0, self.ym(y0), x0+xSize, self.ym(y0)-ySize, fill=fillCol, outline=outlineCol, width=widthBorder)

    def getRectangleName(self, x, y):# y is tk style and so are the elements
        for screenElement in self.screenElements:
            if screenElement.contains(x,self.ym(y)):
                return screenElement.resource.name# todo can also type(resource).__name__
        return "empty"
         
    @staticmethod
    def getSlotPocketDimensions(): 
        justTempVariableToDetermineSlotSize = opentrons_96_tiprack_1000ul(name="testIgnore") # needed for calculation slot sizes
        return justTempVariableToDetermineSlotSize.get_size_x(),justTempVariableToDetermineSlotSize.get_size_y()
    
    def __init__(self, rootWindow, liquidHandler):
        self.stack = deque(maxlen = 10)
        self.stackcursor = 0
        self.zoom = 1
        self.liquidHandler:LiquidHandler=liquidHandler
        # some calculations
        for col in range(1,len(self.liquidHandler.deck.slot_locations)):
            if self.liquidHandler.deck.slot_locations[col].x==0:
                 break
        self.slotSizeX=self.liquidHandler.deck.slot_locations[1].x # assume slots go  right first and then up
        self.slotSizeY=self.liquidHandler.deck.slot_locations[col+1].y
        justTempVariableToDetermineSlotSize = opentrons_96_tiprack_1000ul(name="testIgnore") # needed for calculation slot sizes
        self.slotPocketSizeX, self.slotPocketSizeY=UiWindow.getSlotPocketDimensions()
        print("stockSize:",self.slotPocketSizeX, self.slotPocketSizeY)
        self.firstDraw:bool=True
        self.screenElements:list[ResourceCoordinates]=list()
        # UI
        self.root = rootWindow
        self.frameLabelHolder = Frame(self.root)
        self.frameLabelHolder.place(relx=0.5, rely=0.05, anchor=CENTER, bordermode =OUTSIDE)        
        self.xyLabel:Label = Label(self.frameLabelHolder, text = "Coordinates")
        self.xyLabel.grid(row=0, column=0)             
        self.elementNameLabel:Label = Label(self.frameLabelHolder, text = "Element Name")
        self.elementNameLabel.grid(row=1, column=0)             
        # self.xyLabel.pack(padx = 5, pady = 5)
        # self.elementNameLabel.pack(padx = 5, pady = 5)
         # Add a Scrollbar (horizontal)
        # scrollbar=Scrollbar(self.frameLabelHolder, orient='horizontal')
        # self.menu = Menu(self.frameLabelHolder)-
        # self.menu.add_command(label = "Debug", command = self.debug)
        # CANVAS
        # self.canvasFrameHolder = Frame(self.root)

        # self.canvasFrameHolder.grid(row=1, column=1, sticky="NESW")
        # self.canvasFrameHolder.grid_rowconfigure(0, weight=1)
        # Making a Canvas https://www.tutorialspoint.com/python/tk_place.htm
        self.canvas = Canvas(self.root, width= liquidHandler.deck._size_x, height= liquidHandler.deck._size_y, bd=0,bg="white", cursor="crosshair",
                              highlightthickness=0, highlightbackground="blue")
        #self.canvas.grid(row=1, column=1,sticky='')
        self.canvas.place(relx=0.5, rely=0.5, anchor=CENTER, bordermode =OUTSIDE)
        self.canvas.config()#cursor="pencil")
        # END UI
        # Event Binding
        self.canvas.bind("<Motion>", self.showCursorCoordinates)
        self.canvas.bind("<Button-1>", self.zoomButtonAction)        
        #self.frameLabelHolder.bind("<Motion>", self.clear)
        # self.canvas.bind("<ButtonRelease-1>", self.paint)
        # self.frameLabelHolder.pack(padx = 5, pady = 5, fill= BOTH)
        self.drawAll()
        self.firstDraw=False # so we don't over collect screenElements

    def showCursorCoordinates(self, event):
        self.xyLabel.config(text = "x="+str(round((event.x),2))+" y="+str(round(self.yGcode(event.y),2))+" Ty="+str(round((event.y),2)))
        self.elementNameLabel.config(text=self.getRectangleName(event.x,event.y))

    def zoomButtonAction(self, event):
        print("zoom")
        self.zoom=2
        self.drawAll()
    # def clear(self, event):
    #     self.xyLabel.config(text = "")
    #     self.elementNameLabel.config(text="")
    #     self.drawAll()

    def stackify(self):
        None

    def debug(self):
        print("LiquidHandler", self.liquidHandler)
        # print(Controller.model.dump())
        # messagebox.showinfo("Model", Controller.model.dump())


class UiBootUp:

    def __init__(self, liquidHandler):
        rootWindow = Tk()
        rootWindow.title('text')
        rootWindow.geometry(str(rootWindow.winfo_screenwidth())+"x"+str( int(rootWindow.winfo_screenheight()*.7)))
        rootWindow.state('zoomed')
        window = UiWindow(rootWindow, liquidHandler)
        #rootWindow.attributes('-fullscreen', True)
        #screen_width = win.winfo_screenwidth()
        rootWindow.bind("<Key>", lambda event: window.stackify())
        rootWindow.protocol( "WM_DELETE_WINDOW", onExit )
        rootWindow.mainloop()


def onExit():
    #messagebox.showinfo("bye", "bye")
    #  UtilFileIO.saveModelToFile()
    #os.path.dirname(os.path.abspath(__file__))+"\\..\\default.fa"
    quit()




# from tkinter import * 
# from tkinter.ttk import *
 
# # creating tkinter window
# root = Tk()
# # getting screen's height in pixels
# height = root.winfo_screenheight()
# width = root.winfo_screenwidth()

# my_var = StringVar()
 
# # defining the callback function (observer)
# def my_callback(var, index, mode):
#     print (("Traced variable ".format(my_var.get())))
 
# # registering the observer
# my_var.trace_add('write', my_callback)
 
# Label(root, textvariable = my_var).pack(padx = 5, pady = 5)
 
# Entry(root, textvariable = my_var).pack(padx = 5, pady = 5)

# print("\n width x height = %d x %d (in pixels)\n" %(width, height))
# # infinite loop
# frameLabelHolderloop()