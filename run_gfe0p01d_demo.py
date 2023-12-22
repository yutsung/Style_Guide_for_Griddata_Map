import datetime

import numpy as np

from module.draw_griddata import DrawGriddataMap
from module.load_demo import load_demo_ref_v2
from module.load_demo import load_demo_var_v2
from module.load_demo import load_demo_alt_v2

def main():
    init_date = datetime.datetime(2022, 9, 15, 12)
    
    lat, lon, = load_demo_ref_v2()
    rh, tp, t2m, u10, v10, srp = load_demo_var_v2()
    alt = load_demo_alt_v2()
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(t2m)
    Draw_obj.set_info('ECMWF', 'T2m', init_date, 24)
    Draw_obj.draw_zoom_out('t2m_v2_domain_demo.png', 'temperature') #0
    
    Draw_obj = DrawGriddataMap(china_coast=False)
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(rh)
    Draw_obj.set_info('ECMWF', 'RH', init_date, 24)
    Draw_obj.mask_sea_gfe1km_v2()
    Draw_obj.draw_zoom_in('rh_demo.png', 'relative_humidity') #1
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(tp)
    Draw_obj.set_info('ECMWF', 'TP', init_date, 0, 24)
    Draw_obj.gfe1km_v2_get_total_water()
    Draw_obj.draw('tp_demo.png', 'precipitation') #2
    
    Draw_obj = DrawGriddataMap(china_coast=False)
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(t2m)
    Draw_obj.set_info('ECMWF', 'T2m', init_date, 24)
    Draw_obj.mask_sea_gfe1km_v2()
    Draw_obj.draw_zoom_in('t2m_demo.png', 'temperature') #3
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(np.sqrt(u10**2+v10**2))
    Draw_obj.set_info('ECMWF', 'WS', init_date, 24)
    Draw_obj.draw('ws_demo.png', 'windspeed') #4
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(srp)
    Draw_obj.set_info('ECMWF', 'SRP', init_date, 24)
    Draw_obj.draw('srp_demo.png', 'pressure') #5
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(srp)
    Draw_obj.set_info('ECMWF', 'SRP', init_date, 24)
    Draw_obj.draw_zoom_out('srp_v2_domain_demo.png', 'Downward short-wave radiation flux') #6
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(alt)
    Draw_obj.set_info('GFE', 'ALT', init_date)
    Draw_obj.draw_zoom_out('alt_v2_domain_demo.png', 'elevation') #7
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(alt)
    Draw_obj.set_info('GFE', 'ALT', init_date)
    Draw_obj.mask_sea_gfe1km_v2()
    Draw_obj.draw_zoom_in('alt_v2_demo.png', 'elevation') #8

    
if __name__ == '__main__':
    main()