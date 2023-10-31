import datetime

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from module.draw_griddata import DrawGriddataMap
from module.load_demo import load_demo_ref
from module.load_demo import load_demo_qpf, load_demo_tmax, load_demo_wind


def main():
    init_date = datetime.datetime(2023, 10, 5, 0)
    
    lat, lon, sea_mask = load_demo_ref()
    qpf, total_water = load_demo_qpf(lat, sea_mask)
    tmax, tmax_mask = load_demo_tmax(sea_mask)
    u10, v10 = load_demo_wind()
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(qpf, total_water=total_water)
    Draw_obj.set_info('ECMWF', 'QPF', init_date, 23, 24)
    Draw_obj.draw('qpf_demo.png', 'precipitation')
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(qpf, uwind=u10, vwind=v10)
    Draw_obj.set_info('ECMWF', 'QPF', init_date, 23, 24)
    Draw_obj.draw('qpf_barbs_demo.png', 'precipitation', draw_barbs=True)
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(qpf, total_water=total_water, uwind=u10, vwind=v10)
    Draw_obj.set_info('ECMWF', 'QPF', init_date, 23, 24)
    Draw_obj.draw('qpf_barbs_totalwater_demo.png', 'precipitation', draw_barbs=True)
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax)
    Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
    Draw_obj.draw('tmax_demo.png', 'temperature')
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax_mask)
    Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
    Draw_obj.draw('tmax_mask_demo.png', 'temperature')
    
    Draw_obj = DrawGriddataMap(china_coast=False)
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax_mask)
    Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
    Draw_obj.draw('tmax_mask_demo_nochina.png', 'temperature')
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax_mask)
    Draw_obj.set_info('ECDCA', 'max-T', init_date, -1)
    Draw_obj.draw('tmax_fakegt_demo.png', 'temperature')
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(np.sqrt(u10**2 + v10**2))
    Draw_obj.set_info('ECFMM', 'Wind', init_date, 24, 24)
    Draw_obj.draw('wind_demo.png', 'windspeed')
    
    
if __name__ == '__main__':
    main()