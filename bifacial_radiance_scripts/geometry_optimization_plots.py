import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

r"""
Plotting the functions to adjust the approximation
"""

os.chdir("bifacial_radiance/TEMP/geo_07")
results = pd.read_csv('results.csv', index_col=0)
os.chdir("../../..")

# Input: Latitude (Timbuktu)
lat = 16.66

# Input parameters
# all parameters derived from module.json, x=1.036 and y=1.74, portrait mode, numpanels=1
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
# minimum distance to prevent the panels from shading each other
min_ygap = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2)
# define pitch as distance from edge of one module across row up to the edge of the next module
pitch = y * math.cos(rad_tilt) + min_ygap

# # iteration results from bifacial radiance (George Town)
# xgaps = [0, 1, 2, 3, 4, 5]  # [m]
# fshadings = [0.220319439, 0.565189071, 0.688755063, 0.760388298, 0.796953448, 0.825899627]  # [-]
# fbifacials = [0.078295417, 0.12392022, 0.148550429, 0.160079754, 0.167985713, 0.172557357]  # [-]
# fbifacials = [0 for i in range(len(xgaps))]

# dataframe to lists
fshadings = results['fshadings']
fbifacials = results['fbifacials']
xgaps = [i for i in range(7)]
bio_pot = fshadings + (1 - fshadings) * 0.4
bio_pot2 = fshadings - 1.8 * fshadings**2 + 0.8 * fshadings + 0.5

# Calculate the nonlinear term from the optimization problem
non_linear_term = [(1 + fbifacials[i]) * x / ((1 + fbifacials[0]) * (x + xgaps[i])) for i in range(len(xgaps))]

# calculate ler
#ler = [non_linear_term[i] + fshadings[i] for i in range(len(xgaps))]
ler = non_linear_term + fshadings
ler_pot = non_linear_term + bio_pot
ler_pot2 = non_linear_term + bio_pot2

# Create figure and axis objects
plt.figure(figsize=(8, 6))

# Plotting the non-linear term
plt.plot(xgaps, non_linear_term, '-o', color='orange', label='relative electricity yield')
plt.plot(xgaps, fshadings, '-x', color='green', label='relative biomass yield')
plt.plot(xgaps, bio_pot, '--x', color='green', label='potential rel. crop yield')
# plt.plot(xgaps, bio_pot2, ':x', color='green', label='potential rel. crop yield')
plt.plot(xgaps, ler, '-*', color='blue', label='LER')
plt.plot(xgaps, ler_pot, '--*', color='blue', label='potential LER')
# plt.plot(xgaps, ler_pot2, ':*', color='blue', label='potential LER b)')
# plt.title('LER optimization problem')
plt.xlabel('xgap [m]')
plt.ylabel(r'$\text{E}_{el,rel}$, $\text{m}_{bio,rel}$, $\text{LER}$  [-]')
plt.grid(True)
plt.legend()
plt.subplots_adjust(bottom=0.2)
plt.figtext(0.5, 0.05,
            'LER optimization for Timbuktu, Mali: Potential', ha='center', va='bottom')


# Show plot
plt.show()

