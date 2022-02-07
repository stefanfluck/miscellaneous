#%%
"""
execute json pipeline to filter las by classification and save output tiff
with certain statistics

modify resolution yourself in json text (radius is res*1.414). 


"""


json = """
[
    "2693_1262.las",
    {
        "type":"filters.range",
        "limits":"Classification[3:3], Classification[3:3]"
    },
    {
        "type":"writers.las",
        "filename":"filtered_py.las"
    },
    {
        "resolution": 0.5,
        "radius": 0.707,
        "gdaldriver": "GTiff",
        "output_type": ["mean", "min", "max"],
        "filename":"outputfile_py.tif"
    }
]
"""



import pdal
pipeline = pdal.Pipeline(json)
pipeline.execute()
# count = pipeline.execute()
# arrays = pipeline.arrays
# metadata = pipeline.metadata
# log = pipeline.log


