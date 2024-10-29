import os
from pathlib import Path

sim_name = 'geo_01'

testfolder = Path().resolve() / 'bifacial_radiance' / 'TEMP' / sim_name

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')

print ("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np
import pandas as pd



# Create Radiance object
demo = RadianceObj(sim_name,str(testfolder))

# Ground albedo
albedo = 0.2
demo.setGround(albedo) # for using .gendaylit this command must be run first!


hub_height = 1
xgaps = 1
ygaps = 1
numpanels = 1
nMods = 5
nRows = 5
moduletype = 'test_module'
x = 1.64 # why specify module size, is it not given with 'test_module'?
y = 1

tilt = 10
azimuth = 180

pitch = y * np.cos(np.radians(tilt)) + ygaps

# Location, time and weather data
lat = 13
lon = 31
year = 2021

epwfile = demo.getEPW(lat, lon)
metdata = demo.readWeatherFile(epwfile, coerce_year=year)
timestamp = metdata.datetime.index(pd.to_datetime('2021-05-01 12:00:00+08:00'))
#end = metdata.datetime.index(pd.to_datetime('2021-06-01 6:0:0 +1'))

demo.gendaylit(timestamp)

module = demo.makeModule(moduletype, x=x, y=y, numpanels=numpanels, xgap=xgaps, ygap=ygaps)

sceneDict = {'tilt':tilt,'pitch': 15,'hub_height':hub_height,'azimuth':azimuth, 'nMods': nMods, 'nRows': nRows}
scene = demo.makeScene(module=moduletype, sceneDict=sceneDict)

oct = demo.makeOct()

# Analysis
sensorsy = 10

rad = {}

analysis = AnalysisObj(oct, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=sensorsy)

analysis.analysis(oct, sim_name+"_panelscan", frontscan, backscan)
rad['panelfront'] = np.mean(analysis.Wm2Front)
rad['panelback'] = np.mean(analysis.Wm2Back)

groundscan = frontscan

groundscan['zstart'] = 0  # setting it 12 cm from the ground according to Penman-Monteith (FAO)
groundscan['zinc'] = 0 # constant height
groundscan['xstart'] = 0
groundscan['xinc'] = 0
groundscan['yinc'] = 2*pitch/(sensorsy-1)   # increasing spacing so it covers all distance between rows

analysis.analysis(oct, sim_name+"_groundscan", groundscan, backscan)

rad['groundfront'] = np.mean(analysis.Wm2Front)
rad['groundback'] = np.mean(analysis.Wm2Front)