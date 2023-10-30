import matplotlib
from matplotlib.colors import LinearSegmentedColormap


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


def precipitation_cmap():
    color_under = '#ffffff'
    color_over = '#ffccff'
    boundary = [
        0.1, 1, 2, 6, 10, 15, 20, 30, 40, 
        50, 70, 90, 110, 130, 150, 200, 300
    ]
    hex_list = [
        '#c1c1c1', '#99ffff', '#00ccff', '#0099ff', '#0066ff', '#339900', '#33ff00', '#ffff00', '#ffcc00', '#ff9900',
        '#ff0000', '#cc0000', '#990000', '#990099', '#cc00cc', '#ff00ff'
    ]
    mycmap, mynorm = from_colorlist_to_cmap_norm(boundary, hex_list)
    return mycmap, mynorm, boundary, color_under, color_over


def temperature_cmap():
    color_under = '#000080'
    color_over = '#9c68ad'
    boundary = [
        -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
        10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
        20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 
        30, 31, 32, 33, 34, 35, 36, 37, 38
    ]
    hex_list = [
        '#0000cd', '#0000ff', '#0040ff', '#006aff', '#0095ff', '#00bfff', '#00eaff', '#00ffea', '#80fff4',
        '#117388', '#207e92', '#2e899c', '#3d93a6', '#4c9eb0', '#5ba9ba', '#69b4c4', '#78bfce' ,'#87cad8', '#96d4e2',
        '#a4dfec', '#b3eaf6', '#0c924b', '#1d9a51', '#2fa257', '#40a95e', '#51b164', '#62b96a', '#74c170', '#85c876',
        '#96d07c', '#a7d883', '#b9e089', '#cae78f', '#dbef95', '#f4f4c3', '#f7e78a', '#f4d576', '#f1c362', '#eeb14e',
        '#ea9e3a', '#e78c26', '#e07b03', '#ed5138', '#ed1759', '#ad053a', '#780101', '#c3a4cd', '#af86bd'
    ]
    mycmap, mynorm = from_colorlist_to_cmap_norm(boundary, hex_list)
    return mycmap, mynorm, boundary, color_under, color_over


def wind_speed_cmap():
    color_under = '#ffffff'
    color_over = '#1e0a0a'
    boundary = [
        0.5, 1.0, 4.0, 7.0, 11.0, 17.0, 22.0, 28.0, 34.0, 
        41.0, 48.0, 56.0, 64.0, 72.0, 81.0, 90.0, 100.0, 109., 119.0
    ]
    hex_list = [
        '#e6e6e6', '#d3d3d3', '#979797', '#646464', '#96d2fa', '#1464d5', '#34d53a', '#ffe87c', '#ffa001',
        '#ff1500', '#820000', '#663e32', '#b48c82', '#ffc8c8', '#e68282', '#d45050', '#641616' ,'#321414', 
    ]
    mycmap, mynorm = from_colorlist_to_cmap_norm(boundary, hex_list)
    return mycmap, mynorm, boundary, color_under, color_over