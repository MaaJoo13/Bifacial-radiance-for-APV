import os
from pathlib import Path
import numpy as np
import pandas as pd
import json

try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')


r"""
This is a copy of version 11 which hosts a sensitivity analysis for .epw files for locations of different latitudes. 

It performs the same calculation for Belfaa, Morocco, using the 2 nearest TMY file available
 
Choose the file manually and insert in

epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/<file>.epw'
"""

sim_name = "geo_belfaa"

# Create directory within project for radiation analysis
folder = Path().resolve() / 'bifacial_radiance' / 'TEMP' / sim_name
print(f"Your simulation will be stored in {folder}")

if not os.path.exists(folder):
    os.makedirs(folder)

# Create dictionary for overall geometry parameters and results, will be dumped as .json
geo_params = {}

# Create Radiance object
rad_model = RadianceObj(name=sim_name, path=str(folder))

# choose 1 of 2 epw files and insert in 'epwfile':

# MAR_SS_Agadir-Massira.Intl.AP.602520_TMYx.epw
# MAR_SS_Tiznit.602700_TMYx.epw

epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/MAR_SS_Tiznit.602700_TMYx.epw'
metdata = rad_model.readWeatherFile(weatherFile=epwfile)

# Obtain actual coordinates of the nearest location
with open(epwfile, 'r') as epw:
    for _ in range(1):  # Latitude and longitude are on the first line
        line = epw.readline()
    location_data = line.split(',')
    lat = float(location_data[6])  # Latitude is the 6th element
    lon = float(location_data[7])  # Longitude is the 7th element
print(lat, lon)

# Ground albedo and sky
albedo = 0.23  # FAO56
rad_model.setGround(material=albedo)  # must be run before for .gencumsky or .gendaylit
rad_model.genCumSky()

# Module and scene
moduletype = 'test_module'
# all parameters derived from module.json, portrait mode, numpanels=1
y = 1.74  # module length (y = N/S)
x = 1.036  # module width (x = E/W)

# panel facing south if lat >= 0, else facing north
azimuth = 180 if lat >= 0 else 0
# IBC minimum slope (by means of PV: tilt) for proper rainwater runoff
min_slope = 0.25 / 12
min_tilt = np.ceil(np.degrees(np.arctan(min_slope)))
# tilt should ideally be close to latitude, but allow for rainwater runoff
tilt = max(round(abs(lat)), min_tilt)
rad_tilt = np.radians(tilt)
# minimum solar noon altitude (solar angle at solstice when sun is straight south (lat>0) or north (lat<0)
min_solar_angle = 90 - round(abs(lat)) - 23.5
rad_min_solar_angle = np.radians(min_solar_angle)
# minimum distance to prevent the panels from shading each other
min_ygap = y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle)
# define pitch as distance from edge of one module across row up to the edge of the next module
pitch = round(y * np.cos(rad_tilt) + min_ygap, 2)
# clearance height fixed at 3 m (no significant change afterwards; see paper Sánchez, Meza, Dittmann; own iteration)
clearance_height = 3
# numer of Rows and Modules per row fixed at 5 each, no significant change afterwards; own iteration results)
n = 15
# analysis sensitivity (number of sensors in x and y direction on panel and ground)
sensors = 10
# iteration steps and width
steps = 10
step_width = 1

# Fill SceneDict with constant geometry parameters
sceneDict = {'tilt': tilt,
             'pitch': pitch,
             'clearance_height': clearance_height,
             'azimuth': azimuth,
             'nMods': n,
             'nRows': n
             }

# Create dictionary for results and parameters for each latitude
lat_params = {'xgaps': [], 'fbifacials': [], 'fshadings': [], 'azimuth': azimuth, 'tilt': tilt, 'pitch': pitch}

r"""
Analyze radiance model for varying gaps between PV modules
"""

# Create lists for analysis results:
data = []

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

    # constant height
    groundfrontscan['zstart'] = 0
    groundfrontscan['zinc'] = 0
    # increase x spacing, so it covers 1 module and gap to next module
    groundfrontscan['xinc'] = (x + xgap) / (sensors - 1)
    # increase y spacing, so it covers 1 pitch
    groundfrontscan['yinc'] = pitch / (sensors - 1)

    groundbackscan = groundfrontscan.copy()

    # Panel analysis
    analysis.analysis(octfile=oct, name=rad_model.basename + f"_panelscan_{lat}_{step}",
                      frontscan=frontscan, backscan=backscan)
    fbifacial = np.mean(analysis.backRatio)
    # fshadingpv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    # Ground analysis
    analysis.analysis(octfile=oct, name=rad_model.basename + f"_groundscan_{lat}_{step}",
                      frontscan=groundfrontscan, backscan=groundbackscan)
    fshading = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

    data.append({
        'xgaps': xgap,
        'fbifacials': fbifacial,
        'fshadings': fshading
    })

df = pd.DataFrame(data)

file_name = 'results.csv'
file_path = os.path.join(folder, file_name)
df.to_csv(file_path, index=False)