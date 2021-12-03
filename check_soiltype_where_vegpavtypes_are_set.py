# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 10:50:57 2021

@author: fluf
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt




#%%
ds = xr.open_dataset('luchswiesen_foc_mod_static')


soil = ds.soil_type
pav = ds.pavement_type
veg = ds.vegetation_type


pavarr = pav.values
vegarr = veg.values
soilarr = soil.values


pavar = np.where(pavarr>0, 1, 0)
vegar = np.where(vegarr>0, 1, 0)
lsmar = pavar+vegar
soilar =  np.where(soilarr>0,1,0)

plt.imshow(soilar, origin='lower')


np.unique(soilar+lsmar)
plt.imshow(soilar+lsmar, origin='lower')



'''
issue is that bldgtype above 7 were not respected in cleanup phase in make-static file.
'''





np.unique(ds.building_type.values)[~np.isnan(np.unique(ds.building_type.values))]































