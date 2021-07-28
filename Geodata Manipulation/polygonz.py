# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 16:51:09 2021

@author: stefa
"""
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

def give_z(x):
    if x.type == 'Polygon':
        x = [x]
    zlist = []
    for polygon in x:
        zlist.extend([c[-1] for c in polygon.exterior.coords[:-1]])
        for inner_ring in polygon.interiors:
            zlist.extend([c[-1] for c in inner_ring.coords[:-1]])
    #return zlist
    # return (min(zlist),sum(zlist)/len(zlist),max(zlist)) #In your case to get mean. Or just return zlist[0] if they are all the same
    return (sum(zlist)/len(zlist)) #In your case to get mean. Or just return zlist[0] if they are all the same


from shapely.geometry import Polygon, MultiPolygon, shape, Point
import geopandas as gp
def convert_3D_2D(geometry):
    '''
    Takes a GeoSeries of 3D Multi/Polygons (has_z) and returns a list of 2D Multi/Polygons
    '''
    new_geo = []
    for p in geometry:
        if p.has_z:
            if p.geom_type == 'Polygon':
                lines = [xy[:2] for xy in list(p.exterior.coords)]
                new_p = Polygon(lines)
                new_geo.append(new_p)
            elif p.geom_type == 'MultiPolygon':
                new_multi_p = []
                for ap in p:
                    lines = [xy[:2] for xy in list(ap.exterior.coords)]
                    new_p = Polygon(lines)
                    new_multi_p.append(new_p)
                new_geo.append(MultiPolygon(new_multi_p))
    return new_geo

#%%


alt = gpd.read_file(r'C:\Users\stefa\OneDrive - ZHAW\02_Leimbach Schulhaus\Geodaten\20210222_Daten_SA_Leimbach_Testplanung\20210222_TestplanungSALeimbach_SHP\Variante1.shp')
neu = gpd.read_file(r'C:\Users\stefa\OneDrive - ZHAW\02_Leimbach Schulhaus\Geodaten\ExportFuerWindanalsyeLOD1_inklHoehen\20210303_TestplanungSALeimbach_LOD1_SHP\Variante1.shp')



alt['z'] = alt.geometry.apply(give_z)
alt.geometry = convert_3D_2D(alt.geometry)




#%%
alt['z'] = alt.geometry.apply(give_z)

alt.geometry.type == "Polygon"


#%%
neu.columns

poly = neu[neu.index == 0]

poly.geometry.geometry.geometry.geometry


[list(poly.geometry.exterior[row_id].coords) for row_id in range(poly.shape[0])]


poly.exterior.geometry


poly.convex_hull







#%%

