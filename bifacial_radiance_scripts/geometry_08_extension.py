import os
from pathlib import Path

sim_name = 'geo_08_ext'

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

# Create Radiance object
demo = RadianceObj(name=sim_name, path=str(testfolder))

# Weather data input
epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/KEN_NK_Nakuru.637140_TMYx.epw'
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


'''
### LANDSCAPE MODE ###

moduletype = 'test_module'  # all parameters derived from module.json, landscape mode, numpanels=1
y = 1.036  # module length (y = N/S)
x = 1.74  # module width (x = E/W)

# Azimuth, tilt and minimal row distance based on latitude
azimuth = 180 if lat >= 0 else 0  # panel facing south if lat >= 0, else facing north
# IBC minimum slope (by means of PV: tilt) for proper rainwater runoff
min_slope = 0.25 / 12
min_tilt = np.ceil(np.degrees(np.arctan(min_slope)))
# tilt should ideally be close to latitude, but allow for rainwater runoff
tilt = max(round(abs(lat)), min_tilt)
rad_tilt = np.radians(tilt)
# minimum solar noon altitude (solar angle at solstice when sun is straight south (lat>0) or north (lat<0)
min_solar_angle = 90 - round(abs(lat)) - 23.5
rad_min_solar_angle = np.radians(min_solar_angle)
# minimum pitch to prevent the panels from shading each other
min_pitch = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2) + y * np.cos(rad_tilt)

# Clearance height and nMods, nRows set
clearance_height = 3
n = 15

# sensor density
sensorsy = 10
sensorsx = 10

# iterate pitch and xgaps, obtain frt, frb, fpv:

shadings_pitch = []
shadings_xgap = []
bifacials_pitch = []
bifacials_xgap = []
pvshadings_pitch = []
pvshadings_xgap = []


for i in range(10):
    pitch = i
    xgap = 0

    if pitch < min_pitch:
        shadings_pitch.append(None)
        bifacials_pitch.append(None)
        pvshadings_pitch.append(None)
    else:
        sceneDict = {'tilt': tilt,
                     'pitch': pitch,
                     'clearance_height': clearance_height,
                     'azimuth': azimuth,
                     'nMods': n,
                     'nRows': n
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

        analysis.analysis(octfile=oct, name=f"{demo.basename}_panel_pitch_{i}_test", frontscan=frontscan, backscan=backscan)
        f_bifaciality = np.mean(analysis.backRatio)
        f_shading_pv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        analysis.analysis(octfile=oct, name=f"{demo.basename}_ground_pitch_{i}_test", frontscan=groundfrontscan,
                          backscan=groundbackscan)
        f_shading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

        shadings_pitch.append(f_shading)
        bifacials_pitch.append(f_bifaciality)
        pvshadings_pitch.append(f_shading_pv)

for i in range(10):
    pitch = min_pitch
    xgap = i

    sceneDict = {'tilt': tilt,
                 'pitch': pitch,
                 'clearance_height': clearance_height,
                 'azimuth': azimuth,
                 'nMods': n,
                 'nRows': n
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


# Save results
iteration_results = pd.DataFrame({
    'shadings_ygap': shadings_pitch,
    'shadings_xgap': shadings_xgap,
    'bifacials_ygap': bifacials_pitch,
    'bifacials_xgap': bifacials_xgap,
    'pvshadings_ygap': pvshadings_pitch,
    'pvshadings_xgap': pvshadings_xgap,
    'lat': lat,
    'lon': lon,
})

filename = os.path.join(testfolder, 'iteration_results_NAK_landscape.csv')
iteration_results.to_csv(filename, index=True)
'''

### PORTRAIT MODE ###

moduletype = 'test_module'  # all parameters derived from module.json, portrait mode, numpanels=1
y = 1.74  # module length (y = N/S)
x = 1.036  # module width (x = E/W)

# Azimuth, tilt and minimal row distance based on latitude
azimuth = 180 if lat >= 0 else 0  # panel facing south if lat >= 0, else facing north
# IBC minimum slope (by means of PV: tilt) for proper rainwater runoff
min_slope = 0.25 / 12
min_tilt = np.ceil(np.degrees(np.arctan(min_slope)))
# tilt should ideally be close to latitude, but allow for rainwater runoff
tilt = max(round(abs(lat)), min_tilt)
rad_tilt = np.radians(tilt)
# minimum solar noon altitude (solar angle at solstice when sun is straight south (lat>0) or north (lat<0)
min_solar_angle = 90 - round(abs(lat)) - 23.5
rad_min_solar_angle = np.radians(min_solar_angle)
# minimum pitch to prevent the panels from shading each other
min_pitch = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2) + y * np.cos(rad_tilt)

# Clearance height and nMods, nRows set
clearance_height = 3
n = 15

# sensor density
sensorsy = 10
sensorsx = 10

# iterate pitch and xgaps, obtain frt, frb, fpv:

shadings_pitch = []
shadings_xgap = []
bifacials_pitch = []
bifacials_xgap = []
pvshadings_pitch = []
pvshadings_xgap = []


for i in range(10):
    pitch = i
    xgap = 0

    if pitch < min_pitch:
        shadings_pitch.append(None)
        bifacials_pitch.append(None)
        pvshadings_pitch.append(None)
    else:
        sceneDict = {'tilt': tilt,
                     'pitch': pitch,
                     'clearance_height': clearance_height,
                     'azimuth': azimuth,
                     'nMods': n,
                     'nRows': n
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

for i in range(10):
    pitch = min_pitch
    xgap = i

    sceneDict = {'tilt': tilt,
                 'pitch': pitch,
                 'clearance_height': clearance_height,
                 'azimuth': azimuth,
                 'nMods': n,
                 'nRows': n
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


# Save results
iteration_results = pd.DataFrame({
    'shadings_ygap': shadings_pitch,
    'shadings_xgap': shadings_xgap,
    'bifacials_ygap': bifacials_pitch,
    'bifacials_xgap': bifacials_xgap,
    'pvshadings_ygap': pvshadings_pitch,
    'pvshadings_xgap': pvshadings_xgap,
    'lat': lat,
    'lon': lon,
})

filename = os.path.join(testfolder, 'iteration_results_NAK_portrait.csv')
iteration_results.to_csv(filename, index=True)

