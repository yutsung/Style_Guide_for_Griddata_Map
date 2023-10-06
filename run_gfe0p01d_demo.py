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

from module.load_demo import load_demo_ref
from module.load_demo import load_demo_qpf, load_demo_tmax, load_demo_wind
from module.colormap import precipitation_cmap, temperature_cmap, wind_speed_cmap


class DrawGriddataMap:
    
    def put_latlon(self, lat, lon):
        self.lat = lat
        self.lon = lon
    
    def _load_shape_file(self, linewidth=0.3):
        self.shape_feature_tw = cfeature.ShapelyFeature(
            shpreader.Reader('ref/gadm36_TWN_shp/gadm36_TWN_2').geometries(),
            ccrs.PlateCarree(), 
            facecolor='none',
            linewidth=linewidth
        )
        self.shape_feature_ch = cfeature.ShapelyFeature(
            shpreader.Reader('ref/CHN_adm/CHN_adm1').geometries(),
            ccrs.PlateCarree(), 
            facecolor='none',
            linewidth=linewidth
        )
    
    
class DrawGriddataMap_QPF(DrawGriddataMap):
    
    def put_data(self, qpf, u10, v10, total_water):
        self.qpf = qpf
        self.u10 = u10
        self.v10 = v10
        self.total_water = total_water
    
    def draw(self, title, out_path):
        self._load_shape_file()
        
        mycmap, mynorm, boundary = precipitation_cmap()

        fig = plt.figure(figsize=(6, 7.5))
        ax = fig.add_axes((0.082, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([118, 122.5, 21.3, 26.5], ccrs.PlateCarree())

        ax.add_feature(self.shape_feature_tw)
        ax.add_feature(self.shape_feature_ch)

        gd0 = ax.gridlines(draw_labels=True, alpha=0.5, linestyle=':')
        gd0.top_labels = False
        gd0.right_labels = False
        gd0.xlocator = mticker.FixedLocator([118, 119, 120, 121, 122])
        gd0.ylocator = mticker.FixedLocator([22, 23, 24, 25, 26])
        gd0.xformatter = LONGITUDE_FORMATTER
        gd0.yformatter = LATITUDE_FORMATTER
        gd0.xlabel_style = {'size': 12}
        gd0.ylabel_style = {'size': 12}

        ax.set_title(title, fontsize=16)

        pcolor = ax.pcolormesh(self.lon, self.lat, self.qpf, cmap=mycmap, norm=mynorm)

        cbar_ax = fig.add_axes([0.942, 0.11, 0.02, 0.50])
        cbar = fig.colorbar(pcolor, cax=cbar_ax, extend='both', ticks=boundary)
        cbar.ax.set_yticklabels([
            '', '0.1', '1', '2', '6', '10', '15', '20', '30', '40', 
            '50', '70', '90', '110', '130', '150', '200', '300', ''
        ])
        cbar.ax.tick_params(size=0, labelsize=6)

        mycmap, mynorm, boundary = wind_speed_cmap()
        step = 40
        ws = np.sqrt(self.u10**2 + self.v10**2)
        ax.barbs(
            self.lon[::step, ::step], self.lat[::step, ::step], 
            self.u10[::step, ::step]/0.51444, self.v10[::step, ::step]/0.51444, 
            ws[::step, ::step]/0.51444, cmap=mycmap, norm=mynorm,
            length=6
        )

        ax.text(119.7, 20.9, f'total water : {int(self.total_water//1e6)} x $10^6 m^3$', fontsize=16)

        plt.savefig(out_path)
        plt.close()


class DrawGriddataMap_TminTmax(DrawGriddataMap):
    
    def put_data(self, t2m):
        self.t2m = t2m
    
    def draw(self, title, out_path):
        self._load_shape_file()
        
        mycmap, mynorm, boundary = temperature_cmap()

        fig = plt.figure(figsize=(6, 7.5))
        ax = fig.add_axes((0.082, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([119.1, 122.1, 21.7, 25.5], ccrs.PlateCarree())

        ax.add_feature(self.shape_feature_tw)
        ax.add_feature(self.shape_feature_ch)

        gd0 = ax.gridlines(draw_labels=True, alpha=0.5, linestyle=':')
        gd0.top_labels = False
        gd0.right_labels = False
        gd0.xlocator = mticker.FixedLocator([120, 121, 122])
        gd0.ylocator = mticker.FixedLocator([22, 23, 24, 25])
        gd0.xformatter = LONGITUDE_FORMATTER
        gd0.yformatter = LATITUDE_FORMATTER
        gd0.xlabel_style = {'size': 12}
        gd0.ylabel_style = {'size': 12}

        ax.set_title(title, fontsize=16)

        ax_k = fig.add_axes((0.12, 0.14, 0.2, 1), projection=ccrs.PlateCarree())
        ax_k.set_extent([118.05, 118.55, 24.3, 24.6])
        ax_k.add_feature(self.shape_feature_tw)

        ax_m = fig.add_axes((0.12, 0.295, 0.2, 1), projection=ccrs.PlateCarree())
        ax_m.set_extent([119.8, 120.3, 25.9, 26.4])
        ax_m.add_feature(self.shape_feature_tw)

        pcolor = ax.pcolormesh(self.lon, self.lat, self.t2m, cmap=mycmap, norm=mynorm)
        ax_k.pcolormesh(self.lon, self.lat, self.t2m, cmap=mycmap, norm=mynorm)
        ax_m.pcolormesh(self.lon, self.lat, self.t2m, cmap=mycmap, norm=mynorm)

        cbar_ax = fig.add_axes([0.942, 0.078, 0.02, 0.52])
        cbar = fig.colorbar(pcolor, cax=cbar_ax, extend='both', ticks=boundary)
        cbar.ax.set_yticklabels([
            '', -10, '', -8, '', -6, '', -4, '', -2, '', 
             0, '',  2, '',  4, '',  6, '',  8, '', 
            10, '', 12, '', 14, '', 16, '', 18, '', 
            20, '', 22, '', 24, '', 26, '', 28, '', 
            30, '', 32, '', 34, '', 36, '', 38, ''
        ])
        cbar.ax.tick_params(size=0, labelsize=6)

        plt.savefig(out_path)
        plt.close()

    
    
class DrawGriddataMap_WindSpeed(DrawGriddataMap):
    
    def put_data(self, ws):
        self.ws = ws
        
    def draw(self, title, out_path):
        self._load_shape_file()
        
        mycmap, mynorm, boundary = wind_speed_cmap()

        fig = plt.figure(figsize=(6, 7.5))
        ax = fig.add_axes((0.082, 0.064, 0.859, 0.873), projection=ccrs.PlateCarree())
        ax.set_extent([118, 122.5, 21.3, 26.5], ccrs.PlateCarree())

        ax.add_feature(self.shape_feature_tw)
        ax.add_feature(self.shape_feature_ch)

        gd0 = ax.gridlines(draw_labels=True, alpha=0.5, linestyle=':')
        gd0.top_labels = False
        gd0.right_labels = False
        gd0.xlocator = mticker.FixedLocator([118, 119, 120, 121, 122])
        gd0.ylocator = mticker.FixedLocator([22, 23, 24, 25, 26])
        gd0.xformatter = LONGITUDE_FORMATTER
        gd0.yformatter = LATITUDE_FORMATTER
        gd0.xlabel_style = {'size': 12}
        gd0.ylabel_style = {'size': 12}

        ax.set_title(title, fontsize=16)

        pcolor = ax.pcolormesh(self.lon, self.lat, self.ws/0.5144444, cmap=mycmap, norm=mynorm)

        cbar_ax = fig.add_axes([0.942, 0.11, 0.02, 0.50])
        cbar = fig.colorbar(pcolor, cax=cbar_ax, extend='both', ticks=boundary)
        cbar.ax.set_yticklabels([
            '0', '', '1', '2', '3', '4', '5', '6', '7', '8', 
            '9', '10', '11', '12', '13', '14', '15', '16', '17', '>17',
            ''
        ])
        cbar.ax.tick_params(size=0, labelsize=6)

        plt.savefig(out_path)


def main():
    lat, lon, sea_mask = load_demo_ref()
    qpf, total_water = load_demo_qpf(lat, sea_mask)
    tmax = load_demo_tmax(sea_mask)
    u10, v10 = load_demo_wind()
    
    Draw_qpf = DrawGriddataMap_QPF()
    Draw_t   = DrawGriddataMap_TminTmax()
    Draw_ws  = DrawGriddataMap_WindSpeed()

    Draw_qpf.put_latlon(lat, lon)
    Draw_qpf.put_data(qpf, u10, v10, total_water)
    Draw_qpf.draw('ECMWF : 20231005_0000+(23-24h)', 'qpf_demo.png')
    
    Draw_t.put_latlon(lat, lon)
    Draw_t.put_data(tmax)
    Draw_t.draw('ECDCA max-T : 20231005_0000+(24-36)', 'tmax_demo.png')
    
    Draw_ws.put_latlon(lat, lon)
    Draw_ws.put_data(np.sqrt(u10**2 + v10**2))
    Draw_ws.draw('ECFMM Wind : 20231005_0000 + 24h', 'wind_demo.png')
    
    
if __name__ == '__main__':
    main()