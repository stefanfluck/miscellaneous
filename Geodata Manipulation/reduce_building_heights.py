# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 21:01:15 2021

@author: stefa
"""

import geopandas as gpd
#%%
df = gpd.read_file(r'D:\Geodaten\Leimbach\varianteB-geodaten\leimbach_bestand_gebaeude_hoehencorrected.shp')
df.HEIGHT_TOP[df.HEIGHT_TOP < 0]= 0
df.to_file(r'D:\Geodaten\Leimbach\varianteB-geodaten\leimbach_bestand_gebaeude_hoehencorrected.shp')


#%%
df = gpd.read_file(r'D:\Geodaten\Leimbach\variante1-geodaten\leimbach_variante1_gebaeude.shp')
df['heightcorr'] = 0
df.loc[df.OBJEKTART <= 7, 'heightcorr'] = df.HEIGHT_TOP - 3 - (df['_max']-df['_min'])
df.loc[(df.OBJEKTART <=7) & (df.heightcorr < 0), 'heightcorr']= 0
df.to_file(r'D:\Geodaten\Leimbach\variante1-geodaten\leimbach_variante1_gebaeude_hoehencorrected.shp')


#%%
df = gpd.read_file(r'D:\Geodaten\Leimbach\variante2-geodaten\leimbach_variante2_gebaeude.shp')
df['heightcorr'] = 0
df.loc[df.OBJEKTART <= 7, 'heightcorr'] = df.HEIGHT_TOP - 3 - (df['_max']-df['_min'])
df.loc[(df.OBJEKTART <=7) & (df.heightcorr < 0), 'heightcorr']= 0
df.to_file(r'D:\Geodaten\Leimbach\variante2-geodaten\leimbach_variante2_gebaeude_hoehencorrected.shp')


#%%
df = gpd.read_file(r'D:\Geodaten\Leimbach\variante3-geodaten\leimbach_variante3_gebaeude.shp')
df['heightcorr'] = 0
df.loc[df.OBJEKTART <= 7, 'heightcorr'] = df.HEIGHT_TOP - 3 - (df['_max']-df['_min'])
df.loc[(df.OBJEKTART <=7) & (df.heightcorr < 0), 'heightcorr']= 0
df.to_file(r'D:\Geodaten\Leimbach\variante3-geodaten\leimbach_variante3_gebaeude_hoehencorrected.shp')


