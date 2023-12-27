import datetime

import numpy as np

from module.draw_griddata import DrawGriddataMap
from module.load_demo import load_demo_gfe0p01d_v2

def main():
    init_date = datetime.datetime(2022, 9, 15, 12)
    lon, lat, alt = load_demo_gfe0p01d_v2()
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(alt)
    Draw_obj.set_info('GFE', 'ALT', init_date)
    Draw_obj.draw('alt_demo.png', 'elevation')
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(alt)
    Draw_obj.set_info('GFE', 'ALT', init_date)
    Draw_obj.draw_zoom_out('alt_zoom_out_demo.png', 'elevation')
    
    Draw_obj = DrawGriddataMap()
    Draw_obj.put_latlon(lat, lon)
    Draw_obj.put_data(alt)
    Draw_obj.set_info('GFE', 'ALT', init_date)
    Draw_obj.mask_sea_gfe1km_v2()
    Draw_obj.draw_zoom_in('alt_zoom_in_demo.png', 'elevation')

    
if __name__ == '__main__':
    main()