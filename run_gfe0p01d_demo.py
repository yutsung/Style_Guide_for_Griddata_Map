import datetime

import numpy as np

from module.draw_griddata import DrawGriddataMap
from module.load_demo import load_demo_ref
from module.load_demo import load_demo_qpf, load_demo_tmax, load_demo_wind


def main():
    init_date = datetime.datetime(2023, 10, 5, 0)
    
    lat, lon, sea_mask = load_demo_ref()
    qpf, total_water = load_demo_qpf(lat, sea_mask)
    tmax, _ = load_demo_tmax(sea_mask)
    u10, v10 = load_demo_wind()
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(qpf, total_water=total_water)
    Draw_obj.set_info('ECMWF', 'QPF', init_date, 23, 24)
    Draw_obj.draw('qpf_demo.png', 'precipitation') #1
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(qpf, uwind=u10, vwind=v10)
    Draw_obj.set_info('ECMWF', 'QPF', init_date, 23, 24)
    Draw_obj.draw('qpf_barbs_demo.png', 'precipitation', draw_barbs=True) #2
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(qpf, total_water=total_water, uwind=u10, vwind=v10)
    Draw_obj.set_info('ECMWF', 'QPF', init_date, 23, 24)
    Draw_obj.draw('qpf_barbs_totalwater_demo.png', 'precipitation', draw_barbs=True) #3
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax)
    Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
    Draw_obj.draw('tmax_demo.png', 'temperature') #4
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax)
    Draw_obj.mask_sea_gfe1km()
    Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
    Draw_obj.draw('tmax_mask_demo.png', 'temperature') #5

    Draw_obj = DrawGriddataMap(coast_width=0.6)
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax)
    Draw_obj.mask_sea_gfe1km()
    Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
    Draw_obj.draw_zoom_in('tmax_zoom_in_demo.png', 'temperature') #6
    
    Draw_obj = DrawGriddataMap(china_coast=False)
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax)
    Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
    Draw_obj.draw('tmax_demo_nochina.png', 'temperature') #7
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tmax)
    Draw_obj.mask_sea_gfe1km()
    Draw_obj.set_info('ECDCA', 'max-T', init_date)
    Draw_obj.draw('tmax_fakegt_demo.png', 'temperature') #8
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(np.sqrt(u10**2 + v10**2))
    Draw_obj.set_info('ECFMM', 'Wind', init_date, 24)
    Draw_obj.draw('wind_demo.png', 'windspeed') #9
    
    
if __name__ == '__main__':
    main()