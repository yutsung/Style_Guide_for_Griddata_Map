import numpy as np


def load_demo_ref_v2():
    lon = np.fromfile('ref/gfe0p01d_v2_lon.bin', 'f4').reshape(581, 701)
    lat = np.fromfile('ref/gfe0p01d_v2_lat.bin', 'f4').reshape(581, 701)
    return lat, lon

def load_demo_var_v2():
    rh = np.fromfile('ref/rh2m_demo.bin', 'f4').reshape(581, 701)
    tp = np.fromfile('ref/tp_demo.bin', 'f4').reshape(581, 701)
    t2m = np.fromfile('ref/t2m_demo.bin', 'f4').reshape(581, 701)
    u10 = np.fromfile('ref/u10_demo.bin', 'f4').reshape(581, 701)
    v10 = np.fromfile('ref/v10_demo.bin', 'f4').reshape(581, 701)
    srp = np.fromfile('ref/srp_demo.bin', 'f4').reshape(581, 701)
    return rh, tp, t2m-273.15, u10, v10, srp

def load_demo_alt_v2():
    alt = np.zeros(407281, 'f4')
    with open('ref/GFEGridInfo_1km_Ext.txt') as fid:
        for iline, line in enumerate(fid):
            alt[iline] = float(line.split()[4])
    #with open('ref/GFE0p01d_v2.txt') as fid:
    #    fid.readline()
    #    for iline, line in enumerate(fid):
    #        alt[iline] = float(line.split()[3])
    return alt.reshape(581, 701)
