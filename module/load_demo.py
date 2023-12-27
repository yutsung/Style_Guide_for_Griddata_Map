import numpy as np

def load_demo_gfe0p01d_v2():
    lon = np.zeros(407281, 'f4')
    lat = np.zeros(407281, 'f4')
    alt = np.zeros(407281, 'f4')
    with open('ref/GFEGridInfo_1km_Ext.txt') as fid:
        for iline, line in enumerate(fid):
            lon[iline] = float(line.split()[2])
            lat[iline] = float(line.split()[3])
            alt[iline] = float(line.split()[4])
    return lon.reshape(581, 701), lat.reshape(581, 701), alt.reshape(581, 701)
