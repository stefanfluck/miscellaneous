#!/usr/bin/env python
# coding: utf-8

# # Merge Tiles to large raster with python

# Process to transform multiple separate tiles to one large raster file for swissalti3d.
# - Input: .csv file containing download links to .tif tiles.
# - Output: merged raster file with target resolution

# ### Define paths
tilelist = r'C:/Users/fluf/Desktop/files/ch.swisstopo.swissimage-dop10-zBTmxlHK.csv'
wd = r'C:/Users/fluf/Desktop/files'


# ### set names
merged_dem_name = 'zuerich_swissalti3d_2m_cut.tif'
keep_tiles_after_merge = False

import os
import glob
from osgeo import gdal
import numpy as np


# ### Download all the files to folder in desktop
# Make download folder

try:
    os.makedirs(wd)
    print("created {} successfully".format(wd))
except FileExistsError:
    print('Folder {} already exists'.format(wd))


# read tilelist and make list of it
with open(tilelist) as f:
    tilelist = f.readlines()



tilelist = [line.rstrip() for line in tilelist]

import wget
os.chdir(wd)
it = 0


for file in tilelist:
    print('\ndownloading file nr {} / {}'.format(it, len(tilelist)))
    wget.download(file)
    it += 1
    


# Make List of Tiles
# ### Merge the Files

# make tile list
tiles = []
for file in glob.glob("*.tif"):
    tiles.append(file)


# Loop over tiles
print('Start merging multiple tiles:\n')
if len(tiles) > 1:
    print('Multiple tiles found. Merging now.')
    
    vrt = gdal.BuildVRT('merge.vrt', tiles)
    vrt = None
    
    out = gdal.Translate(merged_dem_name, 'merge.vrt')
    out = None
    
    os.remove("merge.vrt")
    
    print('Merging finished and wrote {}'.format(merged_dem_name))
    
    if keep_tiles_after_merge == False:
        _= [os.remove(file) for file in tiles]
    
elif len(tiles) == 1:
    print('INFO: Only one file, nothing to merge.')
    
else: 
    raise FileNotFoundError('Tile list is empty.')

