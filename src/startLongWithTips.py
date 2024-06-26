import sys
import os
import numpy

from pylabrobot.liquid_handling import LiquidHandler
#from pylabrobot.visualizer.visualizer import Visualizer
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources.opentrons.deck import OTDeck
from pylabrobot.resources import set_tip_tracking, set_volume_tracking
from pylabrobot.resources.opentrons import opentrons_96_tiprack_20ul, opentrons_96_tiprack_1000ul
from pylabrobot.resources.opentrons import corning_96_wellplate_360ul_flat
from pylabrobot.resources.coordinate import Coordinate
from pylabrobot.resources.plate import Plate
from pylabrobot.resources.resource import Resource
from pylabrobot.resources.liquid import Liquid
from pylabrobot.resources.well import Well
from pylabrobot.resources.tip_rack import TipSpot, TipRack
#from pylabrobot.resources.petri_dish import PetriDish, PetriDishHolder
#
from uiBootup import UiBootup, UiWindow
#
#from opentrons import robot, labware, instruments
from pylabrobot.liquid_handling.backends import ChatterBoxBackend
from cncLabBackend import CncLabBackend
import inspect
import adUtil, cncLabBackend
import asyncio
import os
from pprint import pprint
from adUtil import createOtPetriDishPetriHolder
from adUtil import drawBigPlusSign
from adUtil import findLimits
from adUtil import configureZ


opentronsIp=None
if opentronsIp != None:
    print("using an Opentrons server")
    #backend = OpentronsBackend(host=opentronsIp, port=31950)
else:
    backend=CncLabBackend()

#backend=ChatterBoxBackend()
deck:OTDeck=OTDeck(); deck._size_x=437.86;deck._size_y=437.36
liquidHandler = LiquidHandler(backend, deck)
opentronsIp=None


# all docs at https://github.com/AdrianMolecule/inoculatingRobot and source at 
async def main():
    print("current execution directory",os.getcwd())   # Create a new file path new_file_path = os.path.join(current_directory, 'new_file.txt')
    await liquidHandler.setup()
    await asyncio.sleep(1)
    # vis = Visualizer(resource=liquidHandler)    # await vis.setup()
    set_tip_tracking(True)
    configureZ(22)# will set clearance Z for this session.If not it will go the z_max for machine
    #set_volume_tracking(True)
    petriSlot=1
    sourceSlot=4 # labeled style starts at 1 not the 0 indexed
    tipsSlot=5 # my fourth one
    tips = opentrons_96_tiprack_1000ul(name="tip_rack_20") #opentrons_96_tiprack_20ul
    deck.assign_child_at_slot(tips, tipsSlot)
    await liquidHandler.pick_up_tips(tips["A1"]) #tips.fill()
    sourceWells:Resource = corning_96_wellplate_360ul_flat(name='source_plate') #https://labware.opentrons.com/corning_96_wellplate_360ul_flat?category=wellPlate
    deck.assign_child_at_slot(sourceWells, slot=sourceSlot)
    sourceWells.set_well_liquids((Liquid.WATER, 200))
    await liquidHandler.aspirate(sourceWells["H6"][0], vols=[100.0])
    print("loading petriHolder")
    petriHolder = createOtPetriDishPetriHolder("petri")
    dish = petriHolder.dish
    liquidHandler.deck.assign_child_at_slot(petriHolder, petriSlot)
    print("calling disperse with offsets")
    calibrationMediaHeight=8.4 #change here and replace with the z of the top of your agar plate calculated as distance from the bed
    #await drawBigPlusSign(liquidHandler,dish,calibrationMediaHeight) # change here if you want to test with big plus sign
    points=numpy.load("C:/a/diy/pythonProjects/labRobot/src/image/dotarray.npy") #change here for gettig your points from a saved file
    print ("limits for Petri disperse: ",findLimits(points))
    for point in points:
        print("disperse offset:",point)
        await liquidHandler.aspirate(sourceWells["H6"][0], vols=[1.0])        
        await liquidHandler.dispense(dish, vols=[1.0], offsets=[Coordinate(x=point[0], y=point[1], z=calibrationMediaHeight)])
    # #liquidHandler.summary()
    adUtil.saveGCode()
    # I can get pylabrobot.machine.Machine and then get all children
    await liquidHandler.stop()

asyncio.run(main())
UiBootup(liquidHandler) #all done in the constructor


    # https://docs.pylabrobot.org/installation.html change pip install -e ".[dev]"
    # https://docs.pylabrobot.org/basic.html
    # https://docs.pylabrobot.org/using-the-visualizer.html
    # https://colab.research.google.com/drive/1ljiMtb2jrh7-a-ZpjeO7i92d1sQY8KIP?usp=sharing#scrollTo=0gmcxpe-5Qu9
    # https://github.com/Opentrons/opentrons/blob/8fd8a190467708e5b98fc9a0f85163c757fe8272/api/docs/v1/labware.rst
    # for JIM use the workout https://opentrons.com/resource/using-your-multi-channel-e-pipette/
    # https://docs.opentrons.com/v1/hardware_control.html from Jupiter#monkey https://stackoverflow.com/questions/17985216/simpler-way-to-draw-a-circle-with-tkinter


#https://colab.research.google.com/drive/1PoEZYIjggdnXQNGiKdnMmrJGTUg9xrPY#scrollTo=1cp3Mp8C4tQt HTGAA Rick's big code

#C:\a\diy\pythonProjects\pylabrobot\pylabrobot\server\readme.md has interesting info for running and communication with the web server

    #my cnc max y160 x=285
# SCRIPT_DIR = os.path.dirname(os.path.abspath("C:/a/diy/pythonProjects/pylabrobot/pylabrobot/gui"))
# print("SCRIPT_DIR:",SCRIPT_DIR,sys.path)
# sys.path.append(os.path.dirname(SCRIPT_DIR))


# custom_plate_name = "custom_18_wellplate_200ul"

# if plate_name not in labware.list():
#     labware.create(
#         custom_plate_name,  # name of you labware
#         grid=(3, 6),        # number of (columns, rows)
#         spacing=(12, 12),   # distances (mm) between each (column, row)
#         diameter=5,         # diameter (mm) of each well
#         depth=10,           # depth (mm) of each well
#         volume=200)         # volume (µL) of each well

# if plate_name not in labware.list():
#     labware.create(
#         PetriDish,  # name of you labware
#         grid=(1, 1),        # number of (columns, rows)
#         spacing=(100, 100),   # distances (mm) between each (column, row)
#         diameter=84.8,         # diameter (mm) of each well
#         depth=10,           # depth (mm) of each well
#         volume=1000)         # volume (µL) of each well

# custom_plate = labware.load(custom_plate_name, slot="3")