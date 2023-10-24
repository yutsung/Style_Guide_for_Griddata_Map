import numpy as np


def load_demo_ref():
    lon = np.fromfile('ref/gfe0p01d_lon.bin', 'f4').reshape(525, 575)
    lat = np.fromfile('ref/gfe0p01d_lat.bin', 'f4').reshape(525, 575)

    sea_mask = np.zeros(301875, '?')
    with open('ref/gfe0p01d_land_sea.txt') as fid:
        fid.readline()
        for iline, line in enumerate(fid):
            if int(line.split()[4]) == 0:
                sea_mask[iline] = True
    return lat, lon, sea_mask


def load_demo_wind():
    wd = np.fromfile('ref/FST_202310050000TAU0024_301875_WD.bin', 'f4').reshape(525, 575)
    ws = np.fromfile('ref/FST_202310050000TAU0024_301875_WS.bin', 'f4').reshape(525, 575)
    theta_d = (450 - wd) % 360
    theta_d = (theta_d + 180)%360
    theta = theta_d * np.pi / 180
    u10 = ws * np.cos(theta)
    v10 = ws * np.sin(theta)
    return u10, v10
    
    
def load_demo_tmax(mask):
    tmax = np.fromfile('ref/FST_202310050000TAU0024_301875_Tmax.bin', 'f4')
    tmax[mask] = np.nan
    tmax = tmax.reshape(525, 575)
    return tmax
    
    
def load_demo_qpf(lat, mask, dlon_degree=0.01, dlat_degree=0.01):
    qpf = np.fromfile('ref/FST_202310050000TAU0024_301875_QPF1hr.bin', 'f4')
    qpf_land = qpf.copy()
    qpf_land[mask] = np.nan
    qpf = qpf.reshape(525, 575)
    
    radius_km = 6371
    radius = radius_km * 1000
    area = (
        (dlat_degree * np.pi/180 * radius) 
        * (dlon_degree * np.pi/180 * radius) 
        * np.cos(lat * np.pi/180)
    )
    total_water = np.nansum(qpf_land * area.reshape(-1))*1e-3
    return qpf, total_water

