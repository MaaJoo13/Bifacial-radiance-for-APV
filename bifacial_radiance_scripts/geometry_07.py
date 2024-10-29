import os
from pathlib import Path
import math
import pandas as pd
import numpy as np

try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')


r"""
 ***** Part 1: Define general geometry parameters and initiate radiance model *****
 """


sim_name = 'geo_07'
lat = 16.666218157055397
lon = -2.943276813740285

folder = Path().resolve() / 'bifacial_radiance' / 'TEMP' / sim_name
print(f"Your simulation will be stored in {folder}")

if not os.path.exists(folder):
    os.makedirs(folder)

# Create Radiance object
rad_model = RadianceObj(name=sim_name, path=str(folder))

# Get weather data
epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/MLI_TT_Timbuktu-Tombouctou.Intl.AP.612230_TMYx.epw'
metdata = rad_model.readWeatherFile(weatherFile=epwfile)

# Ground albedo and sky
albedo = 0.23  # FAO56
rad_model.setGround(material=albedo)  # must be run before for .gencumsky or .gendaylit
rad_model.genCumSky()

# Module and scene
moduletype = 'test_module'
# all parameters derived from module.json, landscape mode, numpanels=1
y = 1.036  # module length (y = N/S)
x = 1.74  # module width (x = E/W)


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
# minimum distance to prevent the panels from shading each other
min_ygap = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2)
# define pitch as distance from edge of one module across row up to the edge of the next module
pitch = y * math.cos(rad_tilt) + min_ygap
# clearance height fixed at 3 m (no significant change afterwards; see paper Sánchez, Meza, Dittmann; own iteration)
clearance_height = 3
# numer of Rows and Modules per row fixed at 16 each, no significant change afterwards; own iteration results)
n = 16
# analysis sensitivity (number of sensors in x and y direction on panel and ground)
sensors = 10
# iteration steps and width
steps = 7
step_width = 1

# Fill SceneDict with constant geometry parameters
sceneDict = {'tilt': tilt,
             'pitch': pitch,
             'clearance_height': clearance_height,
             'azimuth': azimuth,
             'nMods': n,
             'nRows': n
             }

r"""
Part 2: Analyze radiance model for varying gaps between PV modules
"""

# Create lists for analysis results:
xgaps = []
fbifacials = []
fshadings = []

# Iterate through xgaps and calculate shading and bifaciality factors
for step in range(steps):
    xgap = step * step_width
    # Create module based on xgap; create scene based on module
    module = rad_model.makeModule(name=moduletype, x=x, y=y, xgap=xgap)
    scene = rad_model.makeScene(module=module, sceneDict=sceneDict)

    # Combine everything in .oct file for analysis
    oct = rad_model.makeOct()

    # Create analysis object
    analysis = AnalysisObj(octfile=oct, name=rad_model.basename)

    # Create scans on the panel (automatic sensor positioning)
    frontscan, backscan = analysis.moduleAnalysis(scene=scene, sensorsy=sensors, sensorsx=sensors)

    # Copy panel scans and adjust for the ground
    groundfrontscan = frontscan.copy()

    # setting height to 12 cm from the ground (FAO56), constant height
    groundfrontscan['zstart'] = 0
    groundfrontscan['zinc'] = 0
    # keep first x, increase x spacing, so it covers 1 module and gap to next module
    # groundfrontscan['xinc'] = (x + xgap) / (sensors - 1)
    # keep first y, increase y spacing, so it covers 1 pitch
    groundfrontscan['yinc'] = pitch / (sensors - 1)

    groundbackscan = groundfrontscan.copy()

    # Panel analysis
    analysis.analysis(octfile=oct, name=rad_model.basename + f"_panelscan_{step}",
                      frontscan=frontscan, backscan=backscan)
    fbifacial = np.mean(analysis.backRatio)
    # fshadingpv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    # Ground analysis
    analysis.analysis(octfile=oct, name=rad_model.basename + f"_groundscan_{step}",
                      frontscan=groundfrontscan, backscan=groundbackscan)
    fshading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    # Store results in lists
    xgaps.append(xgap)
    fbifacials.append(fbifacial)
    fshadings.append(fshading)

area_module = [x * y * math.cos(rad_tilt) for i in range(len(xgaps))]
area_apv = [(x + xgaps[i]) * pitch for i in range(len(xgaps))]

resultsDict = {
    'fbifacials': fbifacials,
    'fshadings': fshadings,
    'area_module': area_module,
    'area_apv': area_apv
}

results = pd.DataFrame(resultsDict, index=xgaps)
results_path = os.path.join(folder, 'results.csv')
results.to_csv(results_path)
