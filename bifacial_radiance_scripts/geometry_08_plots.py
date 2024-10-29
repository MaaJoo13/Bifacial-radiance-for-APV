import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects
import os

# read in csv
os.chdir('bifacial_radiance/TEMP/geo_08')
results = pd.read_csv('iteration_results_TIM_landscape.csv', index_col=0)
print(results.head())


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



# Create figure and axis objects
plt.figure(figsize=(11, 5.5))

plt.plot(results.index.values, results['bifacials_clearance'], label='clearance height')
plt.plot(results.index.values, results['bifacials_ygap'], label='pitch')
plt.plot(results.index.values, results['bifacials_xgap'], label='xgap')
plt.plot(results.index.values, results['bifacials_n'], label='nMods, nRows')
#plt.title('Radiation bifaciality factor: Parameter sensitivity analysis for Timbuktu, Mali.')
plt.xlabel('clearance height, pitch, xgap: length [m]; nMods, nRows: number [-]', fontsize=11)
plt.ylabel(r'$\text{f}_{rb}$ [-]', fontsize=11)
plt.grid(True)
plt.legend()
# plt.subplots_adjust(bottom=0.2)
# plt.figtext(0.5, 0.05,
#             'Radiation bifaciality factor: Parameter sensitivity analysis for Timbuktu, Mali.', ha='center', va='bottom')

# Show plot
#plt.show()
plt.savefig('params_frb_landscape_nofigtext.pdf', format='pdf')


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
