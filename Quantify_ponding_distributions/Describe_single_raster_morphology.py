## Describe_single_raster_morphology.py
# Describes "islands" of a binomial classification raster by numbers of islands,
# sizes, and frequency distribution

## Import packages
import numpy as np
import gdal
import matplotlib.pyplot as plt
from scipy import ndimage

## Global variables
# Where is the data?
inRaster = "/Users/exnihilo/Box_Sync/Data/Soil_flooding_data_figs_docs/Data/CMI_ponded_soils_classifications/2017-05-05/Waterlog_0505.tif"

# What is the date of observation?
rastDate = "2017-05-05"

## Functions

## Main script run
# Open the raster
src = gdal.Open(inRaster)

# Read in the raster data as an array
rasterData = np.array(src.GetRasterBand(1).ReadAsArray())

# Close the raster i/o
src = None

# Get the morphology of the image; return the contiguous features labeled and
# the total number of features
labeled, num_features = ndimage.label(rasterData)

# Count up the number of cells (as a flattened array) that share a label
feature_areas = np.bincount(labeled.ravel())[1:]

# Each cell is 10m resolution, so multiply by 10^2 to get sqm
features_sqm = feature_areas * 10**2

## Plot results in a histogram
plt.hist(features_sqm)
plt.yscale('log')
plt.xlabel("Area (m$^2$)")
plt.ylabel("Count")
plt.title("Size distribution of n={} ponds\nfrom {} classification data".format(num_features, rastDate))
plt.tick_params(right=True, which="both", direction="in")
plt.tight_layout()
plt.show()
