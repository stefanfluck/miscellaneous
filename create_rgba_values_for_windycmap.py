import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

class MplColorHelper:

  def __init__(self, cmap_name, start_val, stop_val):
    self.cmap_name = cmap_name
    self.cmap = plt.get_cmap(cmap_name)
    self.norm = mpl.colors.Normalize(vmin=start_val, vmax=stop_val)
    self.scalarMap = cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

  def get_rgb(self, val):
    return self.scalarMap.to_rgba(val)

#%%
import numpy as np

print('[', end='')
for i in np.arange(0,108,4):
    colval = tuple(int(255*x) for x in MplColorHelper('jet',-20,104).get_rgb(i))
    # print(colval)
    print('['+str(i)+',['+str(colval)[1:-1]+']]', end='')
    if i < 104:
        print(',')        
print(']')