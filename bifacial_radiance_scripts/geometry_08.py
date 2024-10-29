import os
from pathlib import Path

sim_name = 'geo_08'

testfolder = Path().resolve() / 'bifacial_radiance' / 'TEMP' / sim_name

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')

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
lat = 16.66
lon = -2.94

epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/DZA_AL_Algiers.Port.603690_TMYx.epw'
metdata = demo.readWeatherFile(weatherFile=epwfile)

# Obtain actual coordinates of the locations
with open(epwfile, 'r') as epw:
    for _ in range(1):  # Latitude and longitude are on the first line
        line = epw.readline()
    location_data = line.split(',')
    lat = float(location_data[6])  # Latitude is the 6th element
    lon = float(location_data[7])  # Longitude is the 7th element

# Ground albedo, module and scene
albedo = 0.23
demo.setGround(material=albedo)  # for using .gendaylit this command must be run first! for .gencumsky as well!
demo.genCumSky()

moduletype = 'test_module'  # all parameters derived from module.json, landscape mode, numpanels=1
y = 1.036  # module length (y = N/S)
x = 1.74  # module width (x = E/W)
azimuth = 180 if lat >= 0 else 0  # panel facing south if lat >= 0, else facing north
tilt = round(abs(lat))      # should ideally be close to latitude, at least 1% of module length to allow for rainwater runoff (find proof!!!)
rad_tilt = math.radians(tilt)
# min_solar_angle = 90 - round(abs(lat)) - 23.5    # minimum solar noon altitude (solar angle at solstice when sun is straight south (lat>0) or north (lat<0)
# rad_min_solar_angle = math.radians(min_solar_angle)
# min_ygap = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2)      # minimum pitch to prevent the panels from shading each other

# sensor density
sensorsy = 10
sensorsx = 10

# iteration over other factors, one after the other:
shadings_clearance = []
shadings_pitch = []
shadings_xgap = []
shadings_n = []
bifacials_clearance = []
bifacials_pitch = []
bifacials_xgap = []
bifacials_n = []
pvshadings_clearance = []
pvshadings_pitch = []
pvshadings_xgap = []
pvshadings_n = []

for i in range(7):
    clearance_height = i
    pitch = 3
    xgap = 3
    n = 15

    #pitch = y * math.cos(rad_tilt) + ygap
    nMods = n
    nRows = n

    sceneDict = {'tilt': tilt,
                 'pitch': pitch,
                 'clearance_height': clearance_height,
                 'azimuth': azimuth,
                 'nMods': nMods,
                 'nRows': nRows
                 }

    module = demo.makeModule(name=moduletype, x=x, y=y, xgap=xgap)
    scene = demo.makeScene(module=module, sceneDict=sceneDict)

    # Generate sky for raytracing and combine everything in .oct file for analysis
    oct = demo.makeOct(octname=f"{demo.basename}_ch_{i}")

    # Analysis
    analysis = AnalysisObj(octfile=oct, name=demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=sensorsy, sensorsx=sensorsx)

    groundfrontscan = frontscan.copy()

    groundfrontscan['zstart'] = 0  # setting it 12 cm from the ground according to Penman-Monteith (FAO)
    groundfrontscan['zinc'] = 0  # constant height
    groundfrontscan['xinc'] = (x + xgap) / (sensorsx - 1)  # increase spacing, so it covers module + gap
    groundfrontscan['yinc'] = pitch / (sensorsy - 1)  # increase spacing, so it covers row + gap

    groundbackscan = groundfrontscan.copy()

    analysis.analysis(octfile=oct, name=f"{demo.basename}_panel_ch_{i}", frontscan=frontscan, backscan=backscan)
    f_bifaciality = np.mean(analysis.backRatio)
    f_shading_pv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    analysis.analysis(octfile=oct, name=f"{demo.basename}_ground_ch_{i}", frontscan=groundfrontscan,
                      backscan=groundbackscan)
    f_shading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    shadings_clearance.append(f_shading)
    bifacials_clearance.append(f_bifaciality)
    pvshadings_clearance.append(f_shading_pv)

for i in range(7):
    clearance_height = 3
    pitch = i
    xgap = 3
    n = 15

    if pitch < y * math.cos(rad_tilt):
        shadings_pitch.append(None)
        bifacials_pitch.append(None)
        pvshadings_pitch.append(None)
    else:
        #pitch = y * math.cos(rad_tilt) + ygap
        nMods = n
        nRows = n

        sceneDict = {'tilt': tilt,
                     'pitch': pitch,
                     'clearance_height': clearance_height,
                     'azimuth': azimuth,
                     'nMods': nMods,
                     'nRows': nRows
                     }

        module = demo.makeModule(name=moduletype, x=x, y=y, xgap=xgap)
        scene = demo.makeScene(module=module, sceneDict=sceneDict)

        # Generate sky for raytracing and combine everything in .oct file for analysis
        oct = demo.makeOct(octname=f"{demo.basename}_pitch_{i}")

        # Analysis
        analysis = AnalysisObj(octfile=oct, name=demo.basename)
        frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=sensorsy, sensorsx=sensorsx)

        groundfrontscan = frontscan.copy()

        groundfrontscan['zstart'] = 0  # setting it 12 cm from the ground according to Penman-Monteith (FAO)
        groundfrontscan['zinc'] = 0  # constant height
        groundfrontscan['xinc'] = (x + xgap) / (sensorsx - 1)  # increase spacing, so it covers module + gap
        groundfrontscan['yinc'] = pitch / (sensorsy - 1)  # increase spacing, so it covers row + gap

        groundbackscan = groundfrontscan.copy()

        analysis.analysis(octfile=oct, name=f"{demo.basename}_panel_pitch_{i}", frontscan=frontscan, backscan=backscan)
        f_bifaciality = np.mean(analysis.backRatio)
        f_shading_pv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        analysis.analysis(octfile=oct, name=f"{demo.basename}_ground_pitch_{i}", frontscan=groundfrontscan,
                          backscan=groundbackscan)
        f_shading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        shadings_pitch.append(f_shading)
        bifacials_pitch.append(f_bifaciality)
        pvshadings_pitch.append(f_shading_pv)

for i in range(7):
    clearance_height = 3
    pitch = 3
    xgap = i
    n = 15

    #pitch = y * math.cos(rad_tilt) + ygap
    nMods = n
    nRows = n

    sceneDict = {'tilt': tilt,
                 'pitch': pitch,
                 'clearance_height': clearance_height,
                 'azimuth': azimuth,
                 'nMods': nMods,
                 'nRows': nRows
                 }

    module = demo.makeModule(name=moduletype, x=x, y=y, xgap=xgap)
    scene = demo.makeScene(module=module, sceneDict=sceneDict)

    # Generate sky for raytracing and combine everything in .oct file for analysis
    oct = demo.makeOct(octname=f"{demo.basename}_xgap_{i}")

    # Analysis
    analysis = AnalysisObj(octfile=oct, name=demo.basename)
    frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=sensorsy, sensorsx=sensorsx)

    groundfrontscan = frontscan.copy()

    groundfrontscan['zstart'] = 0  # setting it 12 cm from the ground according to Penman-Monteith (FAO)
    groundfrontscan['zinc'] = 0  # constant height
    groundfrontscan['xinc'] = (x + xgap) / (sensorsx - 1)  # increase spacing, so it covers module + gap
    groundfrontscan['yinc'] = pitch / (sensorsy - 1)  # increase spacing, so it covers row + gap

    groundbackscan = groundfrontscan.copy()

    analysis.analysis(octfile=oct, name=f"{demo.basename}_panel_xgap_{i}", frontscan=frontscan, backscan=backscan)
    f_bifaciality = np.mean(analysis.backRatio)
    f_shading_pv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    analysis.analysis(octfile=oct, name=f"{demo.basename}_ground_xgap_{i}", frontscan=groundfrontscan,
                      backscan=groundbackscan)
    f_shading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    shadings_xgap.append(f_shading)
    bifacials_xgap.append(f_bifaciality)
    pvshadings_xgap.append(f_shading_pv)

for i in range(7):
    clearance_height = 3
    pitch = 3
    xgap = 3
    n = i

    #pitch = y * math.cos(rad_tilt) + ygap
    if n == 0:
        shadings_n.append(None)
        bifacials_n.append(None)
        pvshadings_n.append(None)
    else:
        nMods = n
        nRows = n

        sceneDict = {'tilt': tilt,
                     'pitch': pitch,
                     'clearance_height': clearance_height,
                     'azimuth': azimuth,
                     'nMods': nMods,
                     'nRows': nRows
                     }

        module = demo.makeModule(name=moduletype, x=x, y=y, xgap=xgap)
        scene = demo.makeScene(module=module, sceneDict=sceneDict)

        # Generate sky for raytracing and combine everything in .oct file for analysis
        oct = demo.makeOct(octname=f"{demo.basename}_n_{i}")

        # Analysis
        analysis = AnalysisObj(octfile=oct, name=demo.basename)
        frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=sensorsy, sensorsx=sensorsx)

        groundfrontscan = frontscan.copy()

        groundfrontscan['zstart'] = 0  # setting it 12 cm from the ground according to Penman-Monteith (FAO)
        groundfrontscan['zinc'] = 0  # constant height
        groundfrontscan['xinc'] = (x + xgap) / (sensorsx - 1)  # increase spacing, so it covers module + gap
        groundfrontscan['yinc'] = pitch / (sensorsy - 1)  # increase spacing, so it covers row + gap

        groundbackscan = groundfrontscan.copy()

        analysis.analysis(octfile=oct, name=f"{demo.basename}_panel_n_{i}", frontscan=frontscan, backscan=backscan)
        f_bifaciality = np.mean(analysis.backRatio)
        f_shading_pv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        analysis.analysis(octfile=oct, name=f"{demo.basename}_ground_n_{i}", frontscan=groundfrontscan,
                          backscan=groundbackscan)
        f_shading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        shadings_n.append(f_shading)
        bifacials_n.append(f_bifaciality)
        pvshadings_n.append(f_shading_pv)

# Save results
iteration_results = pd.DataFrame({
    'shadings_clearance': shadings_clearance,
    'shadings_ygap': shadings_pitch,
    'shadings_xgap': shadings_xgap,
    'shadings_n': shadings_n,
    'bifacials_clearance': bifacials_clearance,
    'bifacials_ygap': bifacials_pitch,
    'bifacials_xgap': bifacials_xgap,
    'bifacials_n': bifacials_n,
    'pvshadings_clearance': pvshadings_clearance,
    'pvshadings_ygap': pvshadings_pitch,
    'pvshadings_xgap': pvshadings_xgap,
    'pvshadings_n': pvshadings_n,
})

filename = os.path.join(testfolder, 'iteration_results_TIM_new.csv')
iteration_results.to_csv(filename, index=True)
