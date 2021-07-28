'''
function to turn numpy array into geotiff.
'''

from osgeo import gdal

def array2geotiff(path, vals, width, height, llx,lly,xres,yres):
    '''
    Turns a numpy array (e.g. data from a xarray dataset by ds.values) into a geotiff. Various 
    geotiff layer data need to be provided.
    
    Numpy array needs to be shown as flipped by axis 0 when viewed with plt.imshow(vals), then it works as expected.
    
    
    Example usage:
   
        > dat = xr.open_dataset(f'Desktop/Auswertung/zw_baseline3_av_xy_N03.selt.nc')
        > pet = dat['bio_pet*_xy'].isel(time=0).squeeze()
        > ox = dat.origin_x
        > oy = dat.origin_y
        > llx = ox
        > lly = oy
        > xres = 4
        > yres = 4
        
        > vals = pet.values
        
        > width = 512
        > height = 256
        > bands = 1
        > path = "C:\\Users\\stefa\\Desktop\\test.tif"
        
        > array2geotiff(path, vals, width, height, llx,lly, xres,yres)



    Parameters
    ----------
    path : str
        path, where to save the geotiff file. Include filename as well.
    vals : np.array (2D)
        Numpy array with data to be saved into the geotiff.
    width : int
        number of cells in x direction.
    height : int
        number of cells in y direction.
    llx : float
        lower left corner x coordinate.
    lly : float
        lower left corner y coordinate.
    xres : float
        resolution per cell in x direction.
    yres : float
        resolution per cell in x direction.

    Returns
    -------
    None.

    '''
    
    drv = gdal.GetDriverByName("GTiff")
    ds = drv.Create(path, width, height, 1, gdal.GDT_Float32)
    ds.SetGeoTransform((llx,xres,0,lly,0,yres))
    ds.GetRasterBand(1).WriteArray(vals)













