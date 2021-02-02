# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 07:56:04 2020

@author: fluf
"""

import pandas as pd
import scipy.signal as sig
import matplotlib.pyplot as plt

#%%
data = pd.read_csv(r'C:/Users/fluf/Desktop/leer_0_50_100_50_0_acc.csv',
                   skiprows = [1])

fs = 20

f, Pxx_den = sig.periodogram(data.Y_value[450:650], fs, scaling='density')

plt.semilogy(f, Pxx_den)
plt.ylim([1e-7, 1e2])
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
