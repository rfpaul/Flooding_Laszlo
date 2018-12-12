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
#inRaster = "/Users/exnihilo/tmp/2017-05-05_RandomForest30_3m_int8.tif"
inRaster = "/Users/exnihilo/tmp/R_randomforest_bin-class_2017-05-05.tif"

# What is the date of observation?
rastDate = "2017-05-05"

## Functions

## Load raster data as 2D array
# Open the raster
src = gdal.Open(inRaster)

# Read in the raster data as an array
rasterData = np.array(src.GetRasterBand(1).ReadAsArray())

# Close the raster i/o
src = None

# Do this if it's the R output where 255 = NA
rasterData[rasterData == 255] = 0

## Process image array
# Binary opening; remove regions smaller than the defined structuring element
# Large structuring array
# structElement = np.array(
#   [[[0, 0, 1, 0, 0],
#     [0, 1, 1, 1, 0],
#     [1, 1, 1, 1, 1],
#     [0, 1, 1, 1, 0],
#     [0, 0, 1, 0, 0]]])

# Small structuring array
structElement = np.array(
  [[0, 1, 0],
   [1, 1, 1],
   [0, 1, 0]])

rasterData = ndimage.binary_opening(
    rasterData,
    structure = structElement).astype('uint8')

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
