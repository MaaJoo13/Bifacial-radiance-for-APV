import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects
import os

# read in csv
os.chdir('bifacial_radiance/TEMP/geo_08_ext')
# results_xgap_landscape = pd.read_csv('irr_geo_08_ext_ground_xgap_4_landscape.csv',
#                                      usecols={'x', 'y', 'Wm2Front'})
# results_xgap_portrait = pd.read_csv('irr_geo_08_ext_ground_xgap_4_portrait.csv',
#                                     usecols={'x', 'y', 'Wm2Front'})
# results_pitch_landscape = pd.read_csv('irr_geo_08_ext_ground_pitch_4_landscape.csv',
#                                       usecols={'x', 'y', 'Wm2Front'})
# results_pitch_portrait = pd.read_csv('irr_geo_08_ext_ground_pitch_4_portrait.csv',
#                                      usecols=['x', 'y', 'Wm2Front'])
# results_check_panel = pd.read_csv('irr_geo_08_ext_panel_pitch_4.csv',
#                                   usecols={'x', 'y', 'Wm2Front'})
results_pitch_landscape_test = pd.read_csv('irr_geo_08_ext_ground_pitch_2_test.csv',
                                     usecols=['x', 'y', 'Wm2Front'])
#print(results_xgap_landscape.head())
dfs = [results_pitch_landscape_test
    # results_xgap_landscape,
    #    results_xgap_portrait,
    #    results_pitch_landscape,
    #    results_pitch_portrait
       ]
os.chdir('../../..')

for df in dfs:
    min = df['Wm2Front'].min()
    max = df['Wm2Front'].max()
    mean = df['Wm2Front'].mean()
    print(min, max, mean)

# directory = 'bifacial_radiance/TEMP/geo_08/results'
# files = [f for f in os.listdir(directory) if f.endswith('.csv')]
#
# dataframes = {}
#
# for file in files:
#     file_path = os.path.join(directory, file)
#     file_name = file.replace('.csv', '')
#     if "ground" in file_name:
#         df = pd.read_csv(file_path, usecols=['Wm2Front'])
#         mean_ground = df['Wm2Back'].mean()
#         if "ch"
#     elif "panel" in file_name:
#         df = pd.read_csv(file_path, usecols=['Back/FrontRatio'])
#         mean_backratio = df['Back/FrontRatio'].mean()


# # Create figure and axis objects
# plt.figure(figsize=(10, 8))
#
# plt.plot(results.index.values, results['bifacials_clearance'], label='clearance height')
# plt.plot(results.index.values, results['bifacials_ygap'], label='pitch')
# plt.plot(results.index.values, results['bifacials_xgap'], label='xgap')
# plt.plot(results.index.values, results['bifacials_n'], label='nMods, nRows')
# #plt.title('Radiation bifaciality factor: Parameter sensitivity analysis for Timbuktu, Mali.')
# plt.xlabel('length [m], number [-]')
# plt.ylabel(r'$\text{f}_{rb}$ [-]')
# plt.grid(True)
# plt.legend()
# plt.subplots_adjust(bottom=0.2)
# plt.figtext(0.5, 0.05,
#             'Radiation bifaciality factor: Parameter sensitivity analysis for Timbuktu, Mali.', ha='center', va='bottom')
#
# # Show plot
# plt.show()


# # Plotting the non-linear term
# plt.plot(results['nMods_nRows'], results['shadings_n'], label='radiation transmission factor')
# plt.plot(results['nMods_nRows'], results['bifacials_n'], label='radiation bifaciality factor')
#
# plt.title('Influence of row and module number')
# plt.xlabel('rows; modules per row [-]')
# plt.ylabel(r'$\text{f}_{rt}$; $\text{f}_{rb}$ [-]')
# plt.grid(True)
# plt.legend()
#
# # Show plot
# plt.show()


