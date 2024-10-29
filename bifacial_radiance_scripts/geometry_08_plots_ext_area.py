import matplotlib.pyplot as plt
import pandas as pd
import os

from geometry_08_ext_area import geometry_area

name = 'KEN_NK_Nakuru.637140_TMYx'
#name = 'DZA_AL_Algiers.Port.603690_TMYx'

os.chdir('bifacial_radiance/TEMP/geo_08_ext')

if 'KEN' in name:
    landscape = pd.read_csv('iteration_results_NAK_landscape.csv', index_col=0)
    portrait = pd.read_csv('iteration_results_NAK_portrait.csv', index_col=0)
    description = 'Nakuru, Kenya.'
    filename = 'frt_nak.pdf'
elif 'DZA' in name:
    landscape = pd.read_csv('iteration_results_ALG_landscape.csv', index_col=0)
    portrait = pd.read_csv('iteration_results_ALG_portrait.csv', index_col=0)
    description = 'Algiers, Algeria.'
    filename = 'frt_alg.pdf'

print(landscape.head())

# os.chdir('../../..')

# Area calculation:
areas_pitch_portrait, areas_xgap_portrait, areas_pitch_landscape, areas_xgap_landscape = geometry_area(name)


plt.figure(figsize=(6, 5))

plt.plot(areas_pitch_portrait, portrait['shadings_ygap'], '--', color='orange', label='variable pitch, portrait mode')
plt.plot(areas_pitch_landscape, landscape['shadings_ygap'], '-', color='orange', label='variable pitch, landscape mode')
plt.plot(areas_xgap_portrait, portrait['shadings_xgap'], '--', color='green', label='variable xgap, portrait mode')
plt.plot(areas_xgap_landscape, landscape['shadings_xgap'], '-', color='green', label='variable xgap, landscape mode')
plt.xlabel(r'$\text{A}_{APV}$ [m²]', fontsize=11)
plt.ylabel(r'$\text{f}_{rt}$ [-]', fontsize=11)
plt.grid(True)
plt.legend()
# plt.subplots_adjust(bottom=0.2)
# plt.figtext(0.5, 0.05,
#             'Radiation transmission factor: Pitch and xgap sensitivity analysis for ' + description,
#             ha='center', va='bottom')

# Save plot
plt.savefig(filename, format='pdf')

# Show plot
plt.show()

