import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from bifacial_radiance import *
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

r"""
Sensor positioning...maybe later, not really important for now
"""

sim_name = "geo_12"

# Create directory within project for radiation analysis
folder = Path().resolve() / 'bifacial_radiance' / 'TEMP' / sim_name
print(f"Your simulation will be stored in {folder}")

if not os.path.exists(folder):
    os.makedirs(folder)

# Create Radiance object
rad_model = RadianceObj(name=sim_name, path=str(folder))

# Get weather data
epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/KEN_NK_Nakuru.637140_TMYx.epw'
metdata = rad_model.readWeatherFile(weatherFile=epwfile)

with open(epwfile, 'r') as epw:
    for _ in range(1):  # Latitude and longitude are on the first line
        line = epw.readline()
    location_data = line.split(',')
    lat = float(location_data[6])  # Latitude is the 6th element
    lon = float(location_data[7])  # Longitude is the 7th element

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
# numer of Rows and Modules per row fixed at 16 each, no significant change afterwards; own iteration results)
n = 16
# analysis sensitivity (number of sensors in x and y direction on panel and ground)
sensors = 10

sceneDict = {'tilt': tilt,
             'pitch': pitch,
             'clearance_height': clearance_height,
             'azimuth': azimuth,
             'nMods': n,
             'nRows': n
             }

xgap = 2

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

# # Panel analysis
# analysis.analysis(octfile=oct, name=rad_model.basename + f"_panelscan_{step}",
#                   frontscan=frontscan, backscan=backscan)
# fbifacial = np.mean(analysis.backRatio)
# # fshadingpv = np.mean(analysis.Wm2Front) / metdata.ghi.sum()

# Ground analysis
analysis.analysis(octfile=oct, name=rad_model.basename + f"_groundscan_xgap_{xgap}_pitch_{pitch}",
                  frontscan=groundfrontscan, backscan=groundbackscan)



### PLOT

def plot_scatter(df, ax, cmap='viridis'):
    scatter = ax.scatter(df['x'], df['y'], c=df['Wm2Front'], cmap=cmap)
    return scatter


# Create 2x2 subplots
fig, axs = plt.subplots(2, 2, figsize=(12, 12))

# Flatten the axs array for easy iteration
axs = axs.flatten()

# # Determine the global min and max for scaling axes
# all_x = pd.concat([df['x'] for df in dfs])
# all_y = pd.concat([df['y'] for df in dfs])
# x_min, x_max = all_x.min(), all_x.max()
# y_min, y_max = all_y.min(), all_y.max()

# Plot each DataFrame
for ax, df in zip(axs, dfs):
    scatter = plot_scatter(df, ax)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel('x')
    ax.set_ylabel('y')


# Add a single colorbar for all subplots
fig.colorbar(scatter, ax=axs, orientation='vertical', label='Value of y')

# Show the plot
#plt.tight_layout()
plt.show()
