import numpy as np


def geometry_area(name):

    epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/' + name + '.epw'

    with open(epwfile, 'r') as epw:
        for _ in range(1):  # Latitude and longitude are on the first line
            line = epw.readline()
        location_data = line.split(',')
        lat = float(location_data[6])  # Latitude is the 6th element
        lon = float(location_data[7])  # Longitude is the 7th element


    # LANDSCAPE

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
    min_pitch_l = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2) + y * np.cos(rad_tilt)

    areas_pitch_landscape = []
    areas_xgap_landscape = []

    for i in range(10):
        pitch = i
        xgap = i

        if pitch < min_pitch_l:
            area_pitch = None
        else:
            area_pitch = x * pitch

        area_xgap = (x + xgap) * min_pitch_l

        areas_pitch_landscape.append(area_pitch)
        areas_xgap_landscape.append(area_xgap)

    # PORTRAIT

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
    min_pitch_p = round(y * np.sin(rad_tilt) / np.tan(rad_min_solar_angle), 2) + y * np.cos(rad_tilt)

    areas_pitch_portrait = []
    areas_xgap_portrait = []

    for i in range(10):
        pitch = i
        xgap = i

        if pitch < min_pitch_p:
            area_pitch = None
        else:
            area_pitch = x * pitch

        area_xgap = (x + xgap) * min_pitch_p

        areas_pitch_portrait.append(area_pitch)
        areas_xgap_portrait.append(area_xgap)

    return areas_pitch_portrait, areas_xgap_portrait, areas_pitch_landscape, areas_xgap_landscape
