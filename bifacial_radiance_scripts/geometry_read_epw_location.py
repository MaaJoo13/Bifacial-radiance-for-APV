

def read_epw_location(epw_path):
    """
    Reads the latitude and longitude from an EPW file.

    Args:
    epw_path (str): The file path to the EPW file.

    Returns:
    tuple: latitude and longitude as floats.
    """
    with open(epw_path, 'r') as file:
        for _ in range(1):  # Latitude and longitude are on the first line
            line = file.readline()
        location_data = line.split(',')
        latitude = float(location_data[6])  # Latitude is the 6th element
        longitude = float(location_data[7])  # Longitude is the 7th element

    return latitude, longitude

epwfile = 'C:/Users/Max.Libberoth/PycharmProjects/APVclimate/bifacial_radiance/custom_EPWs/MLI_TT_Timbuktu-Tombouctou.Intl.AP.612230_TMYx.epw'

lat, lon = read_epw_location(epwfile)
print(lat, lon)
