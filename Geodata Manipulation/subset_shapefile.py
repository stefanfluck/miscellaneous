# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 15:54:56 2021

@author: stefa
"""
import geopandas as gpd

#%% 
df = gpd.read_file(r'D:\Geodaten\Leimbach\leimbach_modified_variante2.shp')


subset_pav = [8,9,10,11,12,13,14,15,17,18,19,20,2001,2002,2003]
subset_veg = [21,22,23,24,25,26,27,28,29,31,32,33,35,38,1001,1002,1003,1004,1005,1006,1007]



pav = df[df.OBJEKTART.isin(subset_pav)]
veg = df[df.OBJEKTART.isin(subset_veg)]
bld = df[df.BLDGTYP > 0]

# pav.to_file(r'D:\Geodaten\Leimbach\variante2-geodaten\leimbach_variante2_paved.shp')
# veg.to_file(r'D:\Geodaten\Leimbach\variante2-geodaten\leimbach_variante2_vegetation.shp')
# bld.to_file(r'D:\Geodaten\Leimbach\variante2-geodaten\leimbach_variante2_gebaeude.shp')



df = gpd.read_file(r'D:\Geodaten\Leimbach\leimbach_modified_variante3.shp')


subset_pav = [8,9,10,11,12,13,14,15,17,18,19,20,2001,2002,2003]
subset_veg = [21,22,23,24,25,26,27,28,29,31,32,33,35,38,1001,1002,1003,1004,1005,1006,1007]



pav = df[df.OBJEKTART.isin(subset_pav)]
veg = df[df.OBJEKTART.isin(subset_veg)]
bld = df[df.BLDGTYP > 0]

# pav.to_file(r'D:\Geodaten\Leimbach\variante3-geodaten\leimbach_variante3_paved.shp')
# veg.to_file(r'D:\Geodaten\Leimbach\variante3-geodaten\leimbach_variante3_vegetation.shp')
# bld.to_file(r'D:\Geodaten\Leimbach\variante3-geodaten\leimbach_variante3_gebaeude.shp')

