# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 09:55:57 2021

@author: stefa
"""


import geopandas as gpd
import numpy as np
#%%

df = gpd.read_file(r'D:\Geodaten\Leimbach\varianteB-geodaten\leimbach_bestand_gebaeude_hoehencorrected.shp')

df.BLDGTYP.isna().sum()

df = df[['BLDGTYP','ID','HEIGHT_TOP', 'geometry']]
df[df.isnull().any(axis=1) == True].plot()






#%%

a = gebtyp
b = gebhoehe
k = gebid
plt.imshow(a)
plt.figure(); plt.imshow(b)
plt.figure(); plt.imshow(k, vmax=1)
c = np.where( (a == -127) & (b != -9999), 1, 0 )
plt.imshow(c)
d = np.where( (a != -127) & (b == -9999), 1, 0 )
plt.imshow(d)
