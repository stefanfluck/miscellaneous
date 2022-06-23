#%%
import xarray as xr
import matplotlib.pyplot as plt

#%% 
ds = xr.open_dataset(r'C:\Users\fluf\switchdrive\Shared Material\Balzers_Dataexchange\Sonic Data\balzers_sonic_20hz_rotated.nc', engine="netcdf4")

#%% 
ds['ws'] = (ds.u**2+ds.v**2)**0.5

#%%
# ds.ws.plot()

ws_subs = ds.ws.sel(time=slice('2020-12-27', '2020-12-28 12:00'))
u_subs = ds.u.sel(time=slice('2020-12-27', '2020-12-28 12:00'))
v_subs = ds.v.sel(time=slice('2020-12-27', '2020-12-28 12:00'))

#%%
fig,ax = plt.subplots(figsize=(12,6))
ws_subs.resample({'time':'10min'}).mean().plot(ylim=[0,30], label='(u**2+v**2)**0.5')
u_subs.resample({'time':'10min'}).mean().plot(ax=ax,ylim=[0,30], label='u')
v_subs.resample({'time':'10min'}).mean().plot(ax=ax,ylim=[0,30], label='v')
ax.legend()

#%%
fig,ax = plt.subplots(figsize=(12,6))
ws_subs.plot(ylim=[0,45], label='(u**2+v**2)**0.5', marker='.', lw=0, markersize=0.2, color='black')
ws_subs.resample({'time':'10min'}).mean().plot(label='(u**2+v**2)**0.5_10min', color='red')
# u_subs.plot(ax=ax,ylim=[0,45], label='u', marker='.', lw=0, markersize=0.2, color='yellow', alpha=0.2)
# v_subs.plot(ax=ax,ylim=[0,45], label='v', marker='.', lw=0, markersize=0.2, color='orange',alpha=0.2)
ax.legend()

#%%
fig,ax = plt.subplots(figsize=(12,6))
# ws_subs.plot(ylim=[0,45], label='(u**2+v**2)**0.5', marker='.', lw=0, markersize=0.2, color='black')
u_subs.plot(ax=ax,ylim=[0,45], label='u', marker='.', lw=0, markersize=0.2, color='black', alpha=1)
u_subs.resample({'time':'10min'}).mean().plot(ax=ax,ylim=[0,45], label='u_10min', color='red')
# v_subs.plot(ax=ax,ylim=[0,45], label='v', marker='.', lw=0, markersize=0.2, color='orange',alpha=0.2)
ax.legend()

#%%
fig,ax = plt.subplots(figsize=(12,6))
# ws_subs.plot(ylim=[0,45], label='(u**2+v**2)**0.5', marker='.', lw=0, markersize=0.2, color='black')
# u_subs.plot(ax=ax,ylim=[0,45], label='u', marker='.', lw=0, markersize=0.2, color='yellow', alpha=0.2)
v_subs.plot(ax=ax,ylim=[0,45], label='v', marker='.', lw=0, markersize=0.2, color='black',alpha=1)
v_subs.resample({'time':'10min'}).mean().plot(ax=ax,ylim=[0,45], label='v_10min', color='red')
ax.legend()

#%%
ds.time