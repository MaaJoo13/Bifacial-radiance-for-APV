import pandas as pd
import matplotlib.pyplot as plt

results_10 = "C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/TEMP/geo_10/results_10.csv"

results_df = pd.read_csv(results_10)

print(results_df.head())

plt.figure(figsize=(11, 5.5))
