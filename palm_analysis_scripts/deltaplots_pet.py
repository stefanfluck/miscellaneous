#%% start
'''
deltaplots für pet

'''

import xarray as xr
import geopandas as gpd

import numpy as np
import matplotlib.pyplot as plt
plt.style.use('stiviMT')


agl = 5
minz=0


path_bestand = r'/cluster/lhome/fluf-schwarzhorn/palm/v21.10/JOBS/'\
                r'luchswiesen_foc_bestand_smaller/'
path_modded = r'/cluster/lhome/fluf-schwarzhorn/palm/v21.10-mod0/JOBS/'\
                'luchswiesen_foc_mod/'


#%% import data of bestand pet

ds_bestand = xr.open_dataset(path_bestand+r'OUTPUT/'\
                             'luchswiesen_foc_bestand_smaller_av_xy.000.nc')
# make absolute timestamp and add two hours for LT
ds_bestand['time'] = (ds_bestand['time']
                         + np.datetime64(ds_bestand.origin_time[:-4])
                         + np.timedelta64(2, 'h'))

#transform coordinates to epsg2056
ds_bestand = ds_bestand.assign_coords(x = ds_bestand.x + ds_bestand.origin_x,
                                      y = ds_bestand.y + ds_bestand.origin_y)



bio_vars = [var for var in list(ds_bestand.keys()) if 'bio' in var]
bio_bestand = ds_bestand[bio_vars].squeeze()

starttime = '2019-06-26 14:00'
endtime = '2019-06-27 04:00'

bio_bestand_subset = bio_bestand.sel(time=slice(starttime, endtime))
bio_bestand_subset = bio_bestand_subset.isel(time=[0,-1])

pet_bestand = bio_bestand_subset['bio_pet*_xy']




#%% import data of modded pet

ds_mod = xr.open_dataset(path_modded+r'OUTPUT/'\
                             'luchswiesen_foc_mod_av_xy.001.nc')
ds_mod['time'] = (ds_mod['time']
                         + np.datetime64(ds_mod.origin_time[:-4])
                         + np.timedelta64(2, 'h'))

ds_mod = ds_mod.assign_coords(x = ds_mod.x + ds_mod.origin_x,
                              y = ds_mod.y + ds_mod.origin_y)

bio_vars = [var for var in list(ds_mod.keys()) if 'bio' in var]
bio_mod = ds_mod[bio_vars].squeeze()

starttime = '2019-06-26 14:00'
endtime = '2019-06-27 04:00'

bio_mod_subset = bio_mod.sel(time=slice(starttime, endtime))
bio_mod_subset = bio_mod_subset.isel(time=[0,-1])

pet_mod = bio_mod_subset['bio_pet*_xy']


#%% Import Geodata
gdpath = '/cluster/home/fluf/files/Geodata/luchswiesen/'
bldgs = gpd.read_file(gdpath + 'luchswiesen_zhext_bestand_gebaeude.shp',
                      bbox=(ds_bestand.origin_x
                                + (ds_bestand.x.max()
                                   - ds_bestand.x.min())*1.2,
                            ds_bestand.origin_y
                                + (ds_bestand.y.max()
                                  - ds_bestand.y.min())*1.2,
                           ds_bestand.origin_x,
                           ds_bestand.origin_y))
trees = gpd.read_file(gdpath + 'luchswiesen_einzelbaeume_bestand'\
                      '_enhanced_w_polygonized_ndom.shp',
                      bbox=(ds_bestand.origin_x
                                + (ds_bestand.x.max()
                                   - ds_bestand.x.min())*1.2,
                            ds_bestand.origin_y
                                + (ds_bestand.y.max()
                                   - ds_bestand.y.min())*1.2,
                            ds_bestand.origin_x,
                            ds_bestand.origin_y))
wald = gpd.read_file(gdpath + 'waldonly.shp',
                     bbox=(ds_bestand.origin_x
                               + (ds_bestand.x.max()
                                  - ds_bestand.x.min())*1.2,
                           ds_bestand.origin_y
                               + (ds_bestand.y.max()
                                  - ds_bestand.y.min())*1.2,
                           ds_bestand.origin_x,
                           ds_bestand.origin_y))


#%% create pet delta data

#create dataset
pet_delta = pet_bestand.copy()
pet_delta = pet_delta.rename('dPET')
pet_delta.attrs['long_name'] = 'dPET'

# pet_delta.isel(time=0).values = (pet_bestand.isel(time=0).values
                                # - pet_mod.isel(time=0).values)
dpet = (pet_mod.values
           - pet_bestand.values)

pet_delta.values = dpet

# pet_delta.isel(time=0).plot()



#%% make pet delta plot
data = pet_delta.isel(time=1)

#for labelling purposes: extract date and time from data
datestring = np.datetime_as_string(data.time.values)[0:10]
timestring = (':'.join(np.datetime_as_string(data.time.values)[11:]
                      .split(':')[0:2]))


scale = np.array(np.arange(-4,4.5,0.5)) #create scale
scale = np.delete(scale, np.where(scale == 0)) #delete 0 value from scale



fig = plt.figure(figsize=(21/2.54,14.8/2.54))
# ax = fig.add_axes([0.01, 0.175, 0.98, 0.75])
ax = fig.gca()
ax.set_aspect('equal')

main_plot = data.interpolate_na(dim='x').plot.contourf(ax = ax,
                    levels=scale,
                    cmap='bwr',
                    add_colorbar=True,
                    extend='both',
                    cbar_kwargs={'shrink':0.6,
                                 'label':'Delta PET [°]',
                                 'ticks':scale, 'format':'%.1f'})

titlestring = ("PET-Veränderung bei geänderten Gebäudeparametern und "
               "Umgebungsgestaltung\n"
               "(Grünanteil höher, helle Fassade, helles Dach, Dachbegrünung, "
               "Entsiegelung, Wasserfläche)"
               "\nam "
             + datestring[8:10]+'.' + datestring[5:7] + '.' + datestring[0:4]
             +' um '+ timestring + ' Uhr')

ax.set_title(titlestring,
             loc='center')

#plot geodata over it
bldgs.plot(ax=ax, color='dimgray',
           edgecolor='black', alpha = 1,
           zorder=99)

trees.plot(ax=ax,
           edgecolor='Green',
           facecolor="none",
           linewidth=1,
           alpha = 1,
           zorder=98)
trees.plot(ax=ax,
           edgecolor='none',
           facecolor="Green",
           linewidth=1,
           alpha = 0.1,
           zorder=98)

# set axis back to sim extents
ax.set_ylim([ds_bestand.origin_y,
             ds_bestand.origin_y
                 + (ds_bestand.y.max()
                    - ds_bestand.y.min()
                    )])

ax.set_xlim([ds_bestand.origin_x,
             ds_bestand.origin_x
             +(ds_bestand.x.max()
               - ds_bestand.x.min()
               )])

ax.set_xticks([])
ax.set_yticks([])
ax.set_ylabel('')
ax.set_xlabel('')

plt.tight_layout()


outpath = ('/cluster/home/fluf/files/luchswiesen_plots/pet_deltaplots/'
           f'petdelta_{datestring}_{timestring.replace(":","")}.png')
plt.savefig(outpath)
plt.close()
