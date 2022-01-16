# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 15:07:06 2022

@author: sfluck
"""

import numpy as np  
import matplotlib.pyplot as plt  
import mpl_toolkits.mplot3d 
import pandas as pd 
 
df = pd.read_csv("Desktop\\SWISSALTI3D_10_XYZ_CHLV95_LN02_2600_1196.xyz", header=0, sep=' ') 

df2 = pd.read_csv("Desktop\\SWISSALTI3D_10_XYZ_CHLV95_LN02_2600_1197.xyz", header=0, sep=' ') 
df = pd.concat([df,df2])
df2 = pd.read_csv("Desktop\\SWISSALTI3D_10_XYZ_CHLV95_LN02_2601_1196.xyz", header=0, sep=' ') 
df = pd.concat([df,df2])
df2 = pd.read_csv("Desktop\\SWISSALTI3D_10_XYZ_CHLV95_LN02_2601_1197.xyz", header=0, sep=' ') 
df = pd.concat([df,df2])


X = df.iloc[:, 0] 
Y = df.iloc[:, 1] 
Z = df.iloc[:, 2] 
 
fig = plt.figure() 
ax = fig.add_subplot(111, projection='3d') 
ax.plot_trisurf(X, Y, Z, color='white', edgecolors='grey', linewidth=0.2, alpha=0.5) 
# ax.scatter(X, Y, Z, c='red') 
plt.show()