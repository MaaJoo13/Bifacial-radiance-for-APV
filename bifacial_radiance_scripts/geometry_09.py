import os
from pathlib import Path

sim_name = 'geo_09'

testfolder = Path().resolve() / 'bifacial_radiance' / 'TEMP' / sim_name
print("Your simulation will be stored in %s" % testfolder)

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

import numpy as np
import pandas as pd
import math

# Create Radiance object
demo = RadianceObj(name=sim_name, path=str(testfolder))

# Location, time and weather data
lat = 16.666218157055397
lon = -2.943276813740285
year = 2022

epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/MLI_TT_Timbuktu-Tombouctou.Intl.AP.612230_TMYx/MLI_TT_Timbuktu-Tombouctou.Intl.AP.612230_TMYx.epw'
metdata = demo.readWeatherFile(weatherFile=epwfile, coerce_year=year)
# ghi_total = metdata.ghi.sum()

# Ground albedo and sky
albedo = 0.23  # FAO56
demo.setGround(material=albedo)  # for using .gendaylit this command must be run first! for .gencumsky as well!
demo.genCumSky()

# Module and scene
moduletype = 'test_module'  # all parameters derived from module.json, x=1.036 and y=1.74 -> portrait mode, numpanels=1
y = 1.74  # module length (y = N/S)
x = 1.036  # module width (x = E/W)

# panel facing south if lat >= 0, else facing north
azimuth = 180 if lat >= 0 else 0
# IBC minimum slope (by means of PV: tilt) for proper rainwater runoff
min_slope = 0.25 / 12
min_tilt = math.ceil(math.degrees(math.atan(min_slope)))
# tilt should ideally be close to latitude, but allow for rainwater runoff
tilt = max(round(abs(lat)), min_tilt)
rad_tilt = math.radians(tilt)
# minimum solar noon altitude (solar angle at solstice when sun is straight south (lat>0) or north (lat<0)
min_solar_angle = 90 - round(abs(lat)) - 23.5
rad_min_solar_angle = math.radians(min_solar_angle)
# minimum pitch to prevent the panels from shading each other
min_ygap = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2)
# clearance height fixed at 3 m (no significant change afterwards; see paper Sánchez, Meza, Dittmann; own iteration)
clearance_height = 3
# numer of Rows and Modules per row fixed at 5 each, no significant change afterwards; own iteration results)
n = 15
# iteration steps
steps = 5
# analysis sensitivity (number of sensors in x and y direction on panel and ground)
sensors = 10

# Create lists for the final output
xgaps = []
ygaps = []
fbifacials = []
fshadings = []

for i in range(steps):
    # Create lists for the values for each iteration step in y direction
    fbifacialsy = []
    fshadingsy = []
    # iterate through xgaps and append to list
    xgap = i
    xgaps.append(xgap)

    for j in range(steps):
        # iterate through ygaps and append to list (only once)
        ygap = min_ygap + j

        # Define pitch as distance from edge of one module across row to edge of next module
        pitch = y * math.cos(rad_tilt) + ygap

        # Fill SceneDict with geometry parameters
        sceneDict = {'tilt': tilt,
                     'pitch': pitch,
                     'clearance_height': clearance_height,
                     'azimuth': azimuth,
                     'nMods': n,
                     'nRows': n
                     }

        # Create module and scene
        module = demo.makeModule(name=moduletype, x=x, y=y, xgap=xgap)  # see readthedocs for parameter customization
        scene = demo.makeScene(module=module, sceneDict=sceneDict)

        # Combine everything in .oct file for analysis
        oct = demo.makeOct()

        # Pass analysis sensitivity (sensor density)
        sensorsy = sensors
        sensorsx = sensors

        # Create analysis object
        analysis = AnalysisObj(octfile=oct, name=demo.basename)

        # Create scans on the panel (automatic sensor positioning)
        frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=sensorsy, sensorsx=sensorsx)

        # Copy panel scans and adjust for the ground
        groundfrontscan = frontscan.copy()

        # setting height to 12 cm from the ground (FAO56), constant height
        groundfrontscan['zstart'] = 0.12
        groundfrontscan['zinc'] = 0
        # keep first x, increase x spacing, so it covers 1 module and gap to next module
        groundfrontscan['xinc'] = (x + xgap) / (sensorsx - 1)
        # keep first y, increase y spacing, so it covers 1 pitch
        groundfrontscan['yinc'] = pitch / (sensorsy - 1)

        groundbackscan = groundfrontscan.copy()

        # Panel analysis
        analysis.analysis(octfile=oct, name=demo.basename + "_panelscan",
                          frontscan=frontscan, backscan=backscan)
        fbifacial = np.mean(analysis.backRatio)
        # fshadingpv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        # Ground analysis
        analysis.analysis(octfile=oct, name=demo.basename + "_groundscan",
                          frontscan=groundfrontscan, backscan=groundbackscan)
        fshading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        # Append iteration results to list (ygaps only once!)
        fbifacialsy.append(fbifacial)
        fshadingsy.append(fshading)
        if i != 0:
            pass
        else:
            ygaps.append(ygap)

    # Append the lists with values in y direction as elements for each step in x direction
    fbifacials.append(fbifacialsy)
    fshadings.append(fshadingsy)

# Final output: lists for xgaps and ygaps of length n,
# n^2 matrix with fbifacials and fshadings for each tuple (x, y) respectively
print(xgaps)
print(ygaps)
print(fbifacials)
print(fshadings)
# Find a way to properly store the results!
