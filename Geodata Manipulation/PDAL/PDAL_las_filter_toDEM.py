#%%
"""
execute json pipeline to filter las by classification and save output tiff
with certain statistics

modify resolution yourself in json text (radius is res*1.414). 


#TODO: 

add function to process multiple las files 
(for file in directory: create a dem)
create function to do vrt and join with gdal in python! 
buildvrt basically in python


"""

do = 'ground' #refer to below dict which is avbl
casename = 'winterthur' #will be prepended to output files
resolution = 1 #meter

classification = {'ground':'Classification[2:2],Classification[9:9]',
                  'buildings':'Classification[6:6]',
                  'vegetation':'Classification[3:3]',
                  'bridges':'Classification[17:17]',
                  'build_brdg':'Classification[6:6],Classification[17:17]'}



import os
import glob
import json
import pdal
from osgeo import gdal
import rasterio
from rasterio.fill import fillnodata
import numpy as np

#%% create list of tiles to process
tiles = []
for file in glob.glob("*.las"):
    tiles.append(file)

#for debugging
tiles = tiles[0:2]

#%% iterate over tiles
# for i in range(len(tiles)):
#     print(f'do file {tiles[i]}')
#     filename_out = tiles[i].split('.')[0]+'_'+ str(do) +'.tif'
#     config = json.dumps([ tiles[i], 
#                          {'type':'filters.range', 'limits':classification[do]},
#                          {'resolution':resolution, 'radius':resolution*1.414, 
#                           'gdaldriver':'GTiff', 
#                           'output_type':['mean'], 
#                           'filename':filename_out}
#                          ])
    
#     pipeline = pdal.Pipeline(config)
#     pipeline.execute()
#     print(f'finished and wrote {filename_out}')



#%% iterate over tiles for las2dem modularized

def select_points_and_raster(file, do, resolution):
    filename_out = file.split('.')[0]+'_'+ str(do) +'.tif'
    config = json.dumps([ file, 
                         {'type':'filters.range', 'limits':classification[do]},
                         {'resolution':resolution, 'radius':resolution*1.414, 
                          'gdaldriver':'GTiff', 
                          'output_type':['mean'], 
                          'filename':filename_out}
                         ])
    
    pipeline = pdal.Pipeline(config)
    pipeline.execute()
    return filename_out

#execute it serially
for i in range(len(tiles)):
    print(f'do file {tiles[i]}')
    filename_out = select_points_and_raster(tiles[i], do, resolution)
    print(f'finished and wrote {filename_out}')


#%% iterate over tiles for las2dem parallelized


# from multiprocess import Pool
# ncores = 4
# # tiles_split = np.array_split(tiles, ncores)

# pool = Pool(processes=ncores)

# pool.starmap(select_points_and_raster, [
#              [file for file in tiles], do, resolution])

# pool.close()
# pool.join()


#%% gdal build vrt
merged_dem_name = casename+'_'+str(do)+'.tif'
keep_tiles_after_merge = True


print('Start merging multiple tiles:\n')
if len(tiles) > 1:
    print('Multiple tiles found. Merging now.')

    tiles_to_merge = [tile.split('.')[0]+'_'+str(do)+'.tif' for tile in tiles]
    
    vrt = gdal.BuildVRT('merge.vrt', tiles_to_merge)
    vrt = None
    
    out = gdal.Translate(casename+'_'+str(do)+'.tif', 'merge.vrt')
    out = None
    
    os.remove("merge.vrt")
    print('Merging finished and wrote {}'.format(casename+'_'+str(do)+'.tif'))
    
    if keep_tiles_after_merge == False:
        _= [os.remove(file) for file in tiles_to_merge]
    
elif len(tiles) == 1:
    print('INFO: Only one file, nothing to merge. Skipping merging step, '
          'but renaming {} to {}'.format(filename_out,
                                         merged_dem_name))
    os.rename(filename_out, merged_dem_name)
else: 
    raise FileNotFoundError('Tile list is empty.')


#%% fill holes for ground
if do == 'ground':
    print('Ground file was done, filling holes now.')
    merged_filled_name = '_filled.'.join(merged_dem_name.split('.'))
    
    
    with rasterio.open(merged_dem_name) as ras:
        profile = ras.profile
        mask = ras.read(1)
        mas = np.where(mask[:,:] == -9999, 0, mask[:,:])
        filled = fillnodata(ras.read(1), mask=mas)
    
    profile['count'] = 1
    
    with rasterio.open(merged_filled_name, 'w', **profile) as dest:
        dest.write_band(1, filled)

    os.remove(merged_dem_name)
    print(f'Finished filling holes, wrote {merged_filled_name}')





















