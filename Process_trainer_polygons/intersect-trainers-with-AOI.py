## Package imports
import glob
import fiona
from shapely.geometry import shape, MultiPolygon, mapping

## Global variables

# What is the root directory with all the shape files?
fpRoot = "/Users/exnihilo/Box_Sync/GIS/Flooding_Remote_Sensing/Coverage_Polygons/"
# What is the glob pattern for CDL+footprint intersection shape files?
fpPattern = fpRoot + "*/*_cdl-intersect.shp"
# Get the paths of the shapefiles
fpPaths = glob.glob(fpPattern)
# What should the output file be called?
outPath = fpRoot + "{0}/{0}_cdl-intersect.shp"

# Where is the shapefile of the CDL classifications?
lcPath = "/Users/exnihilo/Box_Sync/GIS/Flooding_Remote_Sensing/Masks/cbw_vector_2017.shp"
# Load the multipolygon of the CDL vector
with fiona.open(lcPath, 'r') as lc:
    lcShape = MultiPolygon([shape(poly['geometry']) for poly in lc])
    meta = lc.meta

## Script main run
for fpPath in fpPaths:
    # Load the multipolygon of the footprint
    with fiona.open(fpPath, 'r') as fp:
        print("Opening " + fpPath)
        outDriver = fp.driver
        outcrs = fp.crs
        outSchema = fp.schema
        outProperties = fp[0]['properties']
        currDate = outProperties['date']
        multiPList.append(MultiPolygon([shape(poly['geometry']) for poly in fp]))
    print("Opened footprint file for {}, intersecting...".format(currDate))
    
    # Intersect polygon
    interShape = lcShape.intersection(fpShape)
    print("Intersection for {} complete. Saving...".format(currDate))
    
    # Write intersected polygon to file
    with fiona.open(outPath,
                    'w',
                    driver = outDriver,
                    crs = outcrs,
                    schema = outSchema) as c:
        for poly in boundsUnion:
            c.write({
                'properties': outProperties,
                'geometry': mapping(poly)
            })
        print("Save complete")
