import pandas as pd
from input_data import data
import panel
import plant
from crops import crop_dict


geometry = pd.read_csv('C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/TEMP/geo_07/results_07.csv')
fshadings = geometry['fshadings']
fbifacials = geometry['fbifacials']
area_module = geometry['area_module'][0]
area_apv = geometry['area_apv']
area_apv_rel = [area_module / area_apv[i] for i in range(len(area_apv))]


# module_name = "SolarWorld SW 270 duo bifacial PV" Source: Schindele et al. 2020
p_rated = 270  # [Wp]
rad_ref = 1000  # [W/m²]
t_ref = 25  # [°C]
noct = 48  # [°C]

data['pv_eff'] = data.apply(
    lambda row: panel.power(p_rated, row['ghi'], rad_ref, row['t_air'], t_ref, noct), axis=1)

# plant data
crop_type = 'cassava'
t_opt = crop_dict[crop_type]['t_opt']
t_base = crop_dict[crop_type]['t_base']
t_heat = crop_dict[crop_type]['t_max']
t_extreme = crop_dict[crop_type]['t_ext']
t_sum = crop_dict[crop_type]['t_sum']
i50a = crop_dict[crop_type]['i50a']
i50b = crop_dict[crop_type]['i50b']
f_solar_max = crop_dict[crop_type]['f_solar_max']
RUE = crop_dict[crop_type]['rue']

# sowing date
sowing_date = pd.to_datetime('2022-03-01 12:00:00')


data['f_temp'] = data['t_air'].apply(
    lambda t_air: plant.temp(t_air, t_opt, t_base))

data['f_heat'] = data['t_air'].apply(
    lambda t_air: plant.heat(t_air, t_heat, t_extreme))

data['cum_temp'] = data.apply(
    lambda row: plant.development(row.name, sowing_date, row['t_air'], t_base), axis=1).cumsum()

data['f_solar'] = data['cum_temp'].apply(
    lambda cum_temp: plant.solar(cum_temp, t_sum, i50a, i50b, f_solar_max))

data['biomass'] = fshadings[xgap] * data['ghi'] * 3.6e-3 * RUE * data['f_solar'] * data['f_temp'] * data['f_heat']

biomass = data['biomass'].sum()

