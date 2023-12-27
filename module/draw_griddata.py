import datetime
import json

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
    
    def __init__(self, ref_dir='ref', china_coast=True, coast_width=0.8):
        self.ref_dir = ref_dir
        self.china_coast = china_coast
        self._load_shapefile(coast_width)
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
        return mycmap, mynorm, cmap_dict
        
    def _load_shapefile(self, linewidth):
        self.shape_feature_tw = cfeature.ShapelyFeature(
            shpreader.Reader(f'{self.ref_dir}/TW_10908_TWD97/COUNTY_MOI_1090820').geometries(),
            ccrs.PlateCarree(), 
            facecolor='none',
            linewidth=linewidth
        )
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
        
    def put_data(self, values, **kwargs):
        self.values = values
        if 'total_water' in kwargs:
            self.total_water = kwargs['total_water']
        if 'uwind' in kwargs:
            self.uwind = kwargs['uwind']
        if 'vwind' in kwargs:
            self.vwind = kwargs['vwind']
            
    def gfe1km_v2_get_total_water(self):
        dlon_degree=0.01
        dlat_degree=0.01
        self._load_mask_gfe1km_v2()
        qpf = self.values.copy().reshape(-1)
        qpf[self.v2_mask] = np.nan   
        radius_km = 6371
        radius = radius_km * 1000
        area = (
            (dlat_degree * np.pi/180 * radius) 
            * (dlon_degree * np.pi/180 * radius) 
            * np.cos(self.lat * np.pi/180)
        )
        self.total_water = np.nansum(qpf * area.reshape(-1))*1e-3
            
    def mask_sea_gfe1km(self):
        self.mask_sea_gfe1km_v1()
            
    def mask_sea_gfe1km_v1(self):
        sea_mask = np.zeros(301875, '?')
        with open(f'{self.ref_dir}/GFE0p01d_v1.txt') as fid:
            fid.readline()
            for iline, line in enumerate(fid):
                if int(line.split()[4]) == 0:
                    sea_mask[iline] = True
        self.values = self.values.reshape(-1)
        self.values[sea_mask] = np.nan
        self.values = self.values.reshape(525, 575)
        
    def _load_mask_gfe1km_v2(self):
        sea_mask = np.zeros(407281, '?')
        with open(f'{self.ref_dir}/GFEGridInfo_1km_Ext.txt') as fid:
            for iline, line in enumerate(fid):
                if line.split()[5] == 'False':
                    sea_mask[iline] = True
        self.v2_mask = sea_mask
        
    def mask_sea_gfe1km_v2(self):
        self._load_mask_gfe1km_v2()
        self.values = self.values.reshape(-1)
        self.values[self.v2_mask] = np.nan
        self.values = self.values.reshape(581, 701)
        
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
        fig = plt.figure(figsize=(6, 7))
        ax = fig.add_axes((0.082, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([118, 122.5, 21.3, 26.5], ccrs.PlateCarree())
        return fig, ax

    def _init_zoom_in_figure_axes(self):
        fig = plt.figure(figsize=(6, 7.5))
        ax = fig.add_axes((0.082, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([119.1, 122.1, 21.7, 25.5], ccrs.PlateCarree())
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
    
    def _add_barbs(self, ax):
        mycmap, mynorm, boundary, color_under, color_over = wind_speed_cmap_kt()
        step = 40
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
    
    def draw(self, out_path, cmap_name, draw_barbs=False):
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
        cbar_ax = fig.add_axes([0.942, 0.09, 0.02, 0.52])
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
                119.7, 20.9, 
                f'total water : {int(self.total_water//1e6)} x $10^6 m^3$',
                fontsize=16
            )
        plt.savefig(out_path)
        plt.close()

    def draw_zoom_in(self, out_path, cmap_name):
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

        cbar_ax = fig.add_axes([0.942, 0.09, 0.02, 0.52])
        cbar = fig.colorbar(
            pcolor_cs, 
            cax=cbar_ax, 
            extend='both', 
            ticks=cmap_dict['boundary']
        )
        cbar = self._set_colorbar_title_ticklabels(cbar, cmap_dict)

        plt.savefig(out_path)
        plt.close()
        
    def draw_zoom_out(self, out_path, cmap_name, draw_barbs=False):
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
        cbar_ax = fig.add_axes([0.94, 0.08, 0.02, 0.62])
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
        plt.savefig(out_path)
        plt.close()