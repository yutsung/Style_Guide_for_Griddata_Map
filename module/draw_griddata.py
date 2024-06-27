import datetime
import json
from decimal import Decimal, ROUND_HALF_UP

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from shapely import MultiPolygon, Point


def round_v3(num, decimal=0):
    """ https://pcchencode.medium.com/
        [Python] round() 四捨五入…的小坑
    """
    str_deci = 1
    for _ in range(decimal):
        str_deci = str_deci / 10
    str_deci = str(str_deci)
    result = Decimal(str(num)).quantize(Decimal(str_deci), rounding=ROUND_HALF_UP)
    result = float(result)
    return result

def from_colorlist_to_cmap_norm(boundary, hex_list):
    colorlist = []
    for hex in hex_list:
        colorlist.append(matplotlib.colors.to_rgb(hex))
    n_bin = len(colorlist)
    cmap_name = 'precipitation'
    mycmap = LinearSegmentedColormap.from_list(
        cmap_name,
        colorlist,
        N=n_bin
    )
    mynorm = matplotlib.colors.BoundaryNorm(boundary, n_bin)
    return mycmap, mynorm


def wind_speed_cmap_kt():
    color_under = '#ffffff'
    color_over = '#1e0a0a'
    boundary = [
        0.5, 1.0, 4.0, 7.0, 11.0, 
        17.0, 22.0, 28.0, 34.0, 41.0, 
        48.0, 56.0, 64.0, 72.0, 81.0, 
        90.0, 100.0, 109., 119.0
    ]
    hex_list = [
        '#e6e6e6', '#d3d3d3', '#979797', '#646464', '#96d2fa', 
        '#1464d5', '#34d53a', '#ffe87c', '#ffa001', '#ff1500', 
        '#820000', '#663e32', '#b48c82', '#ffc8c8', '#e68282', 
        '#d45050', '#641616' ,'#321414', 
    ]
    mycmap, mynorm = from_colorlist_to_cmap_norm(boundary, hex_list)
    return mycmap, mynorm, boundary, color_under, color_over


class DrawGriddataMap:
    
    def __init__(self, ref_dir='ref', china_coast=True, coast_width=0.8, caisancho=False):
        self.ref_dir = ref_dir
        self.china_coast = china_coast
        self.caisancho = caisancho
        self._load_shapefile(coast_width, caisancho=caisancho)
        self._pre_load_colorset_file()
        
    def _pre_load_colorset_file(self):
        with open(f'{self.ref_dir}/colorset.json') as fid:
            self.colorset_dict = json.load(fid)
            
    def _load_colormap(self, colormap_name):
        cmap_dict = self.colorset_dict[colormap_name]
        mycmap, mynorm = from_colorlist_to_cmap_norm(
            cmap_dict['boundary'], 
            cmap_dict['hex_list']
        )
        if '$degree$' in cmap_dict['unit']:
            cmap_dict['unit'] = cmap_dict['unit'].replace('$degree$', '$^\circ$')
        if 'rac{W}{m^2}$' in cmap_dict['unit']:
            cmap_dict['unit'] = r'$\frac{W}{m^2}$'
        return mycmap, mynorm, cmap_dict
    
    def remove_caisancho_in_shapefile(self):
        new_geoms = ()
        for poly_obj in self.shape_feature_tw._geoms:
            if type(poly_obj) == MultiPolygon:
                new_multipolygon = ()
                for one_poly in poly_obj.geoms:
                    if not (
                        one_poly.contains(Point(120.03, 23.48)) 
                        | one_poly.contains(Point(120.11, 23.55)) 
                        | one_poly.contains(Point(120.1, 23.54))
                    ):
                        new_multipolygon += (one_poly,)
                new_geoms += (MultiPolygon(new_multipolygon),)
            else:
                if not (
                    one_poly.contains(Point(120.03, 23.48)) 
                    | one_poly.contains(Point(120.11, 23.55)) 
                    | one_poly.contains(Point(120.1, 23.54))
                ):
                    new_geoms += (poly_obj,)
        self.shape_feature_tw._geoms = new_geoms
        
    def _load_shapefile(self, linewidth, caisancho):
        self.shape_feature_tw = cfeature.ShapelyFeature(
            shpreader.Reader(f'{self.ref_dir}/TW_10908_TWD97/COUNTY_MOI_1090820').geometries(),
            ccrs.PlateCarree(), 
            facecolor='none',
            linewidth=linewidth
        )
        if not caisancho:
            self.remove_caisancho_in_shapefile()                
        if self.china_coast:
            self.shape_feature_ch = cfeature.ShapelyFeature(
                shpreader.Reader(f'{self.ref_dir}/CHN_adm/CHN_adm1').geometries(),
                ccrs.PlateCarree(), 
                facecolor='none',
                linewidth=linewidth
            )
    
    def put_latlon(self, lat, lon):
        self.lat = lat
        self.lon = lon
        
    def put_uwind_vwind(self, uwind, vwind):
        self.uwind = uwind
        self.vwind = vwind
        
    def put_data(self, values, **kwargs):
        self.values = values
        if 'total_water' in kwargs:
            self.total_water = kwargs['total_water']
        if ('uwind' in kwargs) and ('vwind' in kwargs):
            self.put_uwind_vwind(kwargs['uwind'], kwargs['vwind'])
            
    def calculate_gfe1km_total_water(self):
        qpf = self.mask_sea_gfe1km_func(self.values, tw_land_only=True)
        dlon_degree=0.01
        dlat_degree=0.01
        radius_km = 6371
        radius = radius_km * 1000
        area = (
            (dlat_degree * np.pi/180 * radius) 
            * (dlon_degree * np.pi/180 * radius) 
            * np.cos(self.lat * np.pi/180)
        )
        self.total_water = np.nansum(qpf.reshape(-1) * area.reshape(-1))*1e-3
            
    def mask_sea_gfe1km(self, main_region_only=False, tw_land_only=False, caisancho=False):
        self.values = self.mask_sea_gfe1km_func(
            self.values, 
            main_region_only=main_region_only,
            tw_land_only=tw_land_only,
            caisancho=caisancho
        )

    def mask_sea_gfe1km_func(self, values_in, main_region_only=False, tw_land_only=False, caisancho=False):
        self._load_mask_gfe1km()        
        if values_in.size == 301875: # v1
            shape_0 = 525
            shape_1 = 575
            sea_mask = self.v1_mask
            offshore_islands = self.v1_offshore_islands
        elif values_in.size == 407281: # v2
            shape_0 = 581
            shape_1 = 701
            sea_mask = self.v2_mask
            offshore_islands = self.v2_offshore_islands
        values_out = values_in.copy().reshape(-1)
        values_out[sea_mask] = np.nan
        if not caisancho:
            values_out[offshore_islands==3] = np.nan
        if main_region_only:
            values_out[offshore_islands==3] = np.nan
            values_out[offshore_islands==4] = np.nan
        if tw_land_only:
            values_out[offshore_islands!=1] = np.nan
        values_out = values_out.reshape(shape_0, shape_1)                    
        return values_out
        
    def _load_mask_gfe1km(self):
        self.v1_mask = np.zeros(301875, '?')
        self.v2_mask = np.zeros(407281, '?')
        self.v1_offshore_islands = np.zeros(301875, 'i4')
        self.v2_offshore_islands = np.zeros(407281, 'i4')
        with open(f'{self.ref_dir}/GFEGridInfo_1km_Ext.txt') as fid:
            for iline, line in enumerate(fid):
                if line.split()[5] == 'False':
                    self.v2_mask[iline] = True
        self.v1_mask[:] = self.v2_mask.reshape(581, 701)[28:553, 78:653].reshape(-1)
        with open(f'{self.ref_dir}/GFEGridInfo_1km_Ext_OI.txt') as fid:
            for iline, line in enumerate(fid):
                self.v2_offshore_islands[iline] = int(line.split()[5])
        self.v1_offshore_islands[:] = self.v2_offshore_islands.reshape(581, 701)[28:553, 78:653].reshape(-1)
        
    def set_info(self, product, parameter, init_date, lead_time_start=-999, lead_time_end=None):
        self.product = product
        self.parameter = parameter
        self.lead_time_start = lead_time_start
        self.lead_time_end = lead_time_end            
        if lead_time_start == -999:
            lead_time_str = ''
        else:
            if (lead_time_end == None) or (lead_time_start == lead_time_end):
                lead_time_str = f'+{lead_time_start}h'
            else:
                lead_time_str = f'+({lead_time_start}-{lead_time_end}h)'
            
        self.title = (
            f'{self.product} {self.parameter} : '
            f'{init_date.strftime("%Y%m%d_%H%M")}{lead_time_str}'
        )
        
    def _init_figure_axes(self):
        fig = plt.figure(figsize=(6.2, 7))
        ax = fig.add_axes((0.078, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([118, 122.5, 21.3, 26.5], ccrs.PlateCarree())
        return fig, ax

    def _init_zoom_in_figure_axes(self):
        fig = plt.figure(figsize=(6, 7.5))
        ax = fig.add_axes((0.082, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([119.2, 122.1, 21.7, 25.5], ccrs.PlateCarree())
        return fig, ax
    
    def _init_zoom_out_figure_axes(self):
        fig = plt.figure(figsize=(9.4, 7.6))
        ax = fig.add_axes((0.082, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([117, 124, 21.2, 27], ccrs.PlateCarree())
        return fig, ax
    
    def _add_coast(self, ax):
        ax.add_feature(self.shape_feature_tw)
        if self.china_coast:
            ax.add_feature(self.shape_feature_ch)
        return ax
    
    def _add_map_gridlines(self, ax, fontsize=12):
        gd0 = ax.gridlines(draw_labels=True, alpha=0.5, linestyle=':')
        gd0.top_labels = False
        gd0.right_labels = False
        gd0.xlocator = mticker.FixedLocator([118, 119, 120, 121, 122, 123])
        gd0.ylocator = mticker.FixedLocator([22, 23, 24, 25, 26])
        gd0.xformatter = LONGITUDE_FORMATTER
        gd0.yformatter = LATITUDE_FORMATTER
        gd0.xlabel_style = {'size': fontsize}
        gd0.ylabel_style = {'size': fontsize}
        return ax
    
    def _set_colorbar_title_ticklabels(self, cbar, cmap_dict, ticksize=6):
        cbar.ax.set_yticklabels(cmap_dict['ticklabels'])
        cbar.ax.tick_params(size=0, labelsize=ticksize)
        cbar.ax.set_title(
            cmap_dict['unit'],
            fontsize=12,
            x=cmap_dict['unit_xloc'],
            y=cmap_dict['unit_yloc']
        )
        return cbar
    
    def _add_barbs(self, ax, step=40):
        mycmap, mynorm, boundary, color_under, color_over = wind_speed_cmap_kt()
        ws = np.sqrt(self.uwind**2 + self.vwind**2)
        cs_barbs = ax.barbs(
            self.lon[::step, ::step], self.lat[::step, ::step], 
            self.uwind[::step, ::step]/0.51444, self.vwind[::step, ::step]/0.51444, 
            ws[::step, ::step]/0.51444, cmap=mycmap, norm=mynorm,
            length=6
        )
        cs_barbs.cmap.set_under(color_under)
        cs_barbs.cmap.set_over(color_over)
        return ax
    
    def _mark_max_on_tw(self, ax, values, mark_size, mark_str_x_gap, mark_fontsize, action_threshold=1e-2):
        values = self.mask_sea_gfe1km_func(values, tw_land_only=True)
        ax = self._mark_max_on_map(ax, values, mark_size, mark_str_x_gap, mark_fontsize, action_threshold=1e-2)
        return ax
    
    def _mark_max_on_main(self, ax, values, mark_size, mark_str_x_gap, mark_fontsize, action_threshold=1e-2):
        values = self.mask_sea_gfe1km_func(values, main_region_only=True)
        ax = self._mark_max_on_map(ax, values, mark_size, mark_str_x_gap, mark_fontsize, action_threshold=1e-2)
        return ax
    
    def _mark_max_on_map(self, ax, values, mark_size, mark_str_x_gap, mark_fontsize, action_threshold=1e-2):
        max_value = np.nanmax(values)
        y_points_idx, x_points_idx = np.where(values==max_value)
        mark_str = str(int(round_v3(max_value)))
        if (len(x_points_idx) > 0) & (max_value > action_threshold):
            for x_idx, y_idx in zip(x_points_idx, y_points_idx):
                if (
                    (ax.get_xlim()[0] <= self.lon[y_idx, x_idx] <= ax.get_xlim()[1]) and 
                    (ax.get_ylim()[0] <= self.lat[y_idx, x_idx] <= ax.get_ylim()[1])
                ):
                    ax.plot(
                        self.lon[y_idx, x_idx], 
                        self.lat[y_idx, x_idx], 
                        'k^', markersize=mark_size, markeredgewidth=2, markerfacecolor='None')            
                    if (x_idx+mark_str_x_gap) < self.lon.shape[1]:
                        ax.text(
                            self.lon[y_idx, x_idx+mark_str_x_gap], 
                            self.lat[y_idx, x_idx+mark_str_x_gap], 
                            mark_str, fontsize=mark_fontsize, color="k")
        return ax            
    
    def draw(self, out_path, cmap_name, draw_barbs=False, draw_max=False, draw_max_tw=False, draw_max_main=False):
        mycmap, mynorm, cmap_dict = self._load_colormap(cmap_name)
        fig, ax = self._init_figure_axes()
        ax = self._add_coast(ax)
        ax = self._add_map_gridlines(ax)
        ax.set_title(self.title, fontsize=16)
        pcolor_cs = ax.pcolormesh(
            self.lon, self.lat, self.values, 
            cmap=mycmap, norm=mynorm
        )
        pcolor_cs.cmap.set_under(cmap_dict['color_under'])
        pcolor_cs.cmap.set_over(cmap_dict['color_over'])
        cbar_ax = fig.add_axes([0.935, 0.09, 0.018, 0.52])
        cbar = fig.colorbar(
            pcolor_cs, 
            cax=cbar_ax, 
            extend='both', 
            ticks=cmap_dict['boundary']
        )
        cbar = self._set_colorbar_title_ticklabels(cbar, cmap_dict)

        if draw_barbs:
            ax = self._add_barbs(ax)
        if 'total_water' in self.__dict__:
            ax.text(
                119.7, 20.92, 
                f'total water : {int(self.total_water//1e6)} x $10^6 m^3$',
                fontsize=16
            )
        if draw_max:
            ax = self._mark_max_on_map(ax, self.values, 15, 12, 19)
        if draw_max_main:
            ax = self._mark_max_on_main(ax, self.values, 15, 12, 19)
        if draw_max_tw:
            ax = self._mark_max_on_tw(ax, self.values, 15, 12, 19)
        plt.savefig(out_path)
        plt.close()

    def draw_zoom_in(self, out_path, cmap_name, draw_max=False, draw_max_tw=False, draw_max_main=False):
        mycmap, mynorm, cmap_dict = self._load_colormap(cmap_name)
        fig, ax = self._init_zoom_in_figure_axes()
        ax = self._add_coast(ax)
        ax = self._add_map_gridlines(ax)
        
        ax_k = fig.add_axes((0.12, 0.14, 0.2, 1), projection=ccrs.PlateCarree())
        ax_k.set_extent([118.05, 118.55, 24.3, 24.6])
        ax_k.add_feature(self.shape_feature_tw)

        ax_m = fig.add_axes((0.12, 0.295, 0.2, 1), projection=ccrs.PlateCarree())
        ax_m.set_extent([119.8, 120.3, 25.9, 26.4])
        ax_m.add_feature(self.shape_feature_tw)

        ax.set_title(self.title, fontsize=16)

        pcolor_cs = ax.pcolormesh(
            self.lon, self.lat, self.values, 
            cmap=mycmap, norm=mynorm
        )
        pcolor_k_cs = ax_k.pcolormesh(
            self.lon, self.lat, self.values, 
            cmap=mycmap, norm=mynorm
        )
        pcolor_m_cs = ax_m.pcolormesh(
            self.lon, self.lat, self.values, 
            cmap=mycmap, norm=mynorm
        )
        pcolor_cs.cmap.set_under(cmap_dict['color_under'])
        pcolor_cs.cmap.set_over(cmap_dict['color_over'])
        pcolor_k_cs.cmap.set_under(cmap_dict['color_under'])
        pcolor_k_cs.cmap.set_over(cmap_dict['color_over'])
        pcolor_m_cs.cmap.set_under(cmap_dict['color_under'])
        pcolor_m_cs.cmap.set_over(cmap_dict['color_over'])

        cbar_ax = fig.add_axes([0.929, 0.09, 0.02, 0.52])
        cbar = fig.colorbar(
            pcolor_cs, 
            cax=cbar_ax, 
            extend='both', 
            ticks=cmap_dict['boundary']
        )
        cbar = self._set_colorbar_title_ticklabels(cbar, cmap_dict)
        if draw_max:
            ax = self._mark_max_on_map(ax, self.values, 15, 12, 19)
            ax_k = self._mark_max_on_map(ax_k, self.values, 15, 12, 19)
            ax_m = self._mark_max_on_map(ax_m, self.values, 15, 12, 19)
        if draw_max_main:
            ax = self._mark_max_on_main(ax, self.values, 15, 12, 19)
            ax_k = self._mark_max_on_main(ax_k, self.values, 15, 12, 19)
            ax_m = self._mark_max_on_main(ax_m, self.values, 15, 12, 19)
        if draw_max_tw:
            ax = self._mark_max_on_tw(ax, self.values, 15, 12, 19)
            ax_k = self._mark_max_on_tw(ax_k, self.values, 15, 12, 19)
            ax_m = self._mark_max_on_tw(ax_m, self.values, 15, 12, 19)
        plt.savefig(out_path)
        plt.close()
        
    def draw_zoom_out(self, out_path, cmap_name, draw_barbs=False, draw_max=False, draw_max_tw=False, draw_max_main=False):
        mycmap, mynorm, cmap_dict = self._load_colormap(cmap_name)
        fig, ax = self._init_zoom_out_figure_axes()
        ax = self._add_coast(ax)
        ax = self._add_map_gridlines(ax, fontsize=14)
        ax.set_title(self.title, fontsize=18)
        pcolor_cs = ax.pcolormesh(
            self.lon, self.lat, self.values, 
            cmap=mycmap, norm=mynorm
        )
        pcolor_cs.cmap.set_under(cmap_dict['color_under'])
        pcolor_cs.cmap.set_over(cmap_dict['color_over'])
        cbar_ax = fig.add_axes([0.94, 0.08, 0.016, 0.62])
        cbar = fig.colorbar(
            pcolor_cs, 
            cax=cbar_ax, 
            extend='both', 
            ticks=cmap_dict['boundary']
        )
        cbar = self._set_colorbar_title_ticklabels(
            cbar, 
            cmap_dict, 
            ticksize=8
        )
        if draw_max:
            ax = self._mark_max_on_map(ax, self.values, 15, 12, 19)
        if draw_max_main:
            ax = self._mark_max_on_main(ax, self.values, 15, 12, 19)
        if draw_max_tw:
            ax = self._mark_max_on_tw(ax, self.values, 15, 12, 19)
        plt.savefig(out_path)
        plt.close()
        
    def draw_wind_barbs(self, out_path):
        fig, ax = self._init_figure_axes()
        ax = self._add_barbs(ax)
        ax.axis('off')
        plt.savefig(out_path, transparent=True)
        plt.close()
        