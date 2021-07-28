# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 12:56:14 2021

@author: fluf
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import scipy.signal as signal


#%%
ds = xr.open_dataset(r'E:\PALM\Balzers\balzers_foehn_large_6_output\spectratest.nc')

ds = ds.mean(dim=['x','y'])
ws = ds['wspeed']

plt.plot(ws.isel(time=0))


plt.plot(ws.sel(zu_3d=54, method='nearest'))
ws = ws.sel(zu_3d=54, method='nearest').values

#ws is np array of wspeed data for 1 h, every second.
plt.plot(ws)


#%%

freqs, PSD = signal.welch(ws, fs=1, window=signal.windows.hamming(len(ws)), scaling='density', return_onesided=True, detrend=False)


plt.loglog(freqs, PSD)
# plt.ylim([1e-10, 1e0])
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')

y_power_law = freqs**(-5/3)*0.01
plt.loglog(y_power_law, freqs)


