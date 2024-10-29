try:
    import bifacial_radiance
except ImportError:
    raise RuntimeError('bifacial_radiance is required. download distribution')

bifacial_radiance.gui()