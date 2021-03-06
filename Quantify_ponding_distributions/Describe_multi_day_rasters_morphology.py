## Describe_multi_day_rasters_morphology.py
# Describes 3D "islands" of chronologically ordered binomial classification
# rasters by numbers of islands, sizes, and frequency distribution

## Import packages
import numpy as np
import glob
import re
import gdal
import sys
import matplotlib.pyplot as plt
from matplotlib import rc_file
import datetime as dt
from scipy import ndimage
import rasterio
from rasterio.profiles import DefaultGTiffProfile

# Matplotlib parameters file
rc_file("/Users/exnihilo/Box_Sync/Data/Soil_flooding_data_figs_docs/Documents/manuscript_figure_rc_params")

## Functions
# Parse date from a file path with a YYYY-MM-DD year
def ParseDate(path):
    # Regex search string for YYYY-MM-DD
    regexString = "\d{4}-\d{2}-\d{2}"
    # Pull the date from the path name
    pathDate = re.search(regexString, path).group()
    # Convert string to a date object
    pathDate = dt.datetime.strptime(pathDate, "%Y-%m-%d").date()
    return pathDate

# Gathers the raster files associated with the pattern, reorders
# the list of raster paths into chronological order, and returns a list of
# file paths and a parallel list of their dates
def SortExtractChrono(pathPattern):
    # Fetch the list of raster filepaths matching the pattern
    inRasters = glob.glob(pathPattern)
    
    # Parse a list of dates from the list of rasters paths
    dateList = [ParseDate(x) for x in inRasters]
    # Sort the dates into chronologcial order
    dateSort = sorted(dateList)
    # Get the order of indices in chronological order
    chronOrderIndices = [dateList.index(x) for x in dateSort]
    pathSort = [inRasters[i] for i in chronOrderIndices]
    
    # Return resulting sorted filepaths and their dates
    return pathSort, dateSort

# Take the list of raster paths and return them as a 3D array,
# with the first axis being the order of the rasters in the list
# (in this case, time is the first axis)
def LoadRasterSlices(pathList, maskPath):
    # Empty array for the slices
    arrayList = []
    # Load mask of the permanent water features in the image
    try:
        # Open mask
        src = gdal.Open(maskPath)
        # Read in the mask as an array
        mask = np.array(src.GetRasterBand(1).ReadAsArray()).astype('uint8')
        src = None
        # We want to exclude permanent water features; flip the 0 and 1 values
        mask = 1 - mask
    except OSError as err: # Catch bad file input
        print("OS error: {0}".format(err))
    except: # Catch all other errors
        print("Unexpected error:", sys.exc_info()[0])
        raise
    # Load the raster data as a list of arrays
    for path in pathList:
        try:
            # Open the raster
            src = gdal.Open(path)
            # Read in the raster data as an array
            inData = np.array(
                src.GetRasterBand(1).ReadAsArray())
            # Close the raster i/o
            src = None
            # Redefine NA value of 255 to 0
            inData[inData == 255] = 0
            # Mask out permanent water features
            inData = np.bitwise_and(inData, mask)
            # Append array to list
            arrayList.append(inData)
        except OSError as err: # Catch bad file input
            print("OS error: {0}".format(err))
        except: # Catch all other errors
            print("Unexpected error:", sys.exc_info()[0])
            raise
    
    # Return array stacked as a 3D array
    # Time is the FIRST dimension of this array!
    return np.array(arrayList)

# Pass back (later -> earlier) information through non-overlapping layers.
# If the layer extents overlap, use the earlier values.
# This assumes inputs of 3D arrays based on a series of 2D raster-derived
# arrays arranged in time slices from first to last chronologically, and the
# time axis being the first dimension of the array.
# dataArray is the classification data itself; extentsArray is the collection
# of masks describing valid data extents.
# Returns an array of the classification slices with the time-extended data
def ExtendTimeSlices(dataArray, extentsArray):
    # Work on a copy of the array
    dataCopy = dataArray.copy()
    # Number of time slices in the arrays
    numSlices = dataCopy.shape[0]
    # Backwards-counting list of indices for the arrays
    # NOTE: we end at the 2nd item (index 1) because the data processing
    # for loop shifts data UP the array to index-1
    sliceIndices = list(range(numSlices-1, 0, -1))
    
    for i in sliceIndices:
        # Get current data and extent
        currData = dataCopy[i]
        # Get the next earliest data and extent
        nextData = dataCopy[i - 1]
        nextExtent = extentsArray[i - 1]
        
        # What is excluded from the earlier extent?
        extentExclusion = 1-nextExtent  # Equivalent to logical not of next 
                                        # earliest extent
        # Copy the excluded (non-overlapping) data in the current extent
        extentExclusion = np.bitwise_and(extentExclusion, currData)
        # Copy the excluded data into the next earliest extent
        nextData = np.bitwise_or(extentExclusion, nextData)
        # Replace the next earliest data with the new extended data
        dataCopy[i - 1] = nextData
    
    return dataCopy

# Take the number of slices a labeled feature lasts, and then by looking up the
# dates associated with the ending slice, return an array of day lengths
def SlicesToDays(sliceLens, dates):
    dayLens = np.array(
        [(dates[j - 1] - dates[i]).days for i, j in sliceLens]).astype('int')
    return dayLens
 
## Global variables
# Searchable pattern for the filepaths of the data
dataPathPattern = "/Users/exnihilo/Box_Sync/tmp/2017-05/Classified/R_randomforest_bin-class_*.tif"
dataPaths, dateList = SortExtractChrono(dataPathPattern)

# Searchable pattern for the filepaths of the extent data
# IMPORTANT! These MUST have exactly the same scale and extent as the
# data rasters!
extentPathPattern = "/Users/exnihilo/Box_Sync/tmp/2017-05/Masks/*_cbw_viz-mask_3m_int8.tif"
extentPaths, extentDates = SortExtractChrono(extentPathPattern)

# Where is the CDL mask for permanent water features?
maskPath = "/Users/exnihilo/Box_Sync/GIS/Flooding_Remote_Sensing/Masks/2017_water_3m_mask.tif"

# Large structuring array for noise removal via binary opening
# structElement = np.array(
#   [[[0, 0, 1, 0, 0],
#     [0, 1, 1, 1, 0],
#     [1, 1, 1, 1, 1],
#     [0, 1, 1, 1, 0],
#     [0, 0, 1, 0, 0]]])

# Small structuring array
structElement = np.array(
  [[[0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]]])

# Color for plotting histograms
plotColor = 'steelblue'

## Main script run -- load data
# Get the raster data and extents loaded into arrays
print("Gathering raster data...", end = ' ')
inputData = LoadRasterSlices(dataPaths, maskPath)
rasterData = inputData.copy()
print("Done")

print("Gathering extent data...", end = ' ')
extents = LoadRasterSlices(extentPaths, maskPath)
print("Done")

# Check that the shapes of the arrays are the same
sameProperties = extents.shape == rasterData.shape
if (not sameProperties):
    # If shapes don't match, raise an error
    raise RuntimeError("Dimensions of data and extents do not match")

# Check that all the dates are the same and in the same order
sameProperties = all([i == j for (i, j) in zip(dateList, extentDates)])
if (not sameProperties):
    # If dates don't match, raise an error
    raise RuntimeError("Dates for data and extents do not match")

# Binary opening; remove regions smaller than the defined structuring element
print("Removing areas smaller than structuring element...", end = ' ')

rasterData = ndimage.binary_opening(
    rasterData,
    structure = structElement).astype('uint8')
print("Done")

# Pass back, chronologically, "missing" information through the data layers
print("Extending non-overlapping data from later to earlier...", end = ' ')
rasterData = ExtendTimeSlices(rasterData, extents)
print("Done")

## Main script run -- morphology
# Get the morphology of the image; return the contiguous features labeled and
# the total number of features
print("Labeling morphological structure...", end = ' ')
labeled, num_features = ndimage.label(rasterData)
# Grab the first raster layer and the first label layer
# firstSlice = rasterData[0]
primaryLabeled = labeled[0]
# Alternatively, grab the layer for 2017-05-06 (first day after precip)
firstSlice = rasterData[2]

print("Done")

# "Bounding box" of found objects
print("Finding and describing labeled objects...", end = ' ')
found = ndimage.find_objects(labeled)
# "Lengths" of each label
allLabelLens = np.array([(x[0].start, x[0].stop) for x in found])
# "Lengths" of each label that starts at the first slice
labelLens = np.array([x for x in allLabelLens if x[0] == 0])
print("Done")

# Convert number of slices to duration in days
dayLens = SlicesToDays(labelLens, dateList)
# Last day with precipitation over 1 cm (.39")
lastRainyDay = dt.date(2017, 5, 5)
# Days between first measurement date and the last rainy day
numRainyDays = (lastRainyDay - dateList[0]).days
# Change durations to days after rain
allDayLens = dayLens - numRainyDays
# We only care about ponds that last at least 1 day
dryDayLens = allDayLens[allDayLens > 0]

# Count up the number of cells (as a flattened array) that share a label
feature_areas = np.bincount(primaryLabeled.ravel())[1:]
# Copy all the features in case we need to use them again
all_features = feature_areas.copy()
# We only care about ponds that last at least 1 day
feature_areas = feature_areas[allDayLens > 0]

# We have a few leftover small features that started in previous days;
# remove them
dryDayLens = dryDayLens[feature_areas >=5]
feature_areas = feature_areas[feature_areas >=5]

# Each cell is 3m resolution, so multiply by 3^2 to get sqm
features_sqm = feature_areas * 3**2

# Also get the hectares
features_ha = features_sqm / 1e4

# What percent area in the AOI gets ponded?
allExtents = np.bitwise_or.reduce(extents, axis = 0)
percentPonded = np.bitwise_or.reduce(rasterData, axis = 0).sum() / allExtents.sum()

## Plot duration results in a histogram
# Single plot
fig, ax = plt.subplots()
# 1 row, 2 col plot
#plt.subplot(1, 2, 1)
plt.hist(dryDayLens, color = plotColor)
plt.yscale('log')
plt.xlabel("Duration (days)")
plt.ylabel("Count")
#plt.title("Duration distribution of n={} ponds lasting at least\none day after significant rainfall (> 1 cm daily accumulation)".format(len(dryDayLens)))
plt.tick_params(right=True, which="both", direction="in")
plt.tight_layout()
plt.show()

## Plot first slice results in a histogram
# Single plot
fig, ax = plt.subplots()
# 1 row, 2 col plot
#plt.subplot(1, 2, 2)
# Histogram bin breaks
plt.hist(features_ha,
    color = plotColor,
    bins = [0, .0078125, .015625, .03125, .0625, .125, .25, .5,
            1, 4, 8, 16, 32])
# Use log scales on X and Y axes; data set has high density around short
# durations and low pond sizes 
plt.yscale('log')
plt.xscale('log')
plt.xlabel("Area (ha)")
plt.ylabel("Count")
#plt.title("Size distribution of n={} ponds\nfrom May 2017 classification data".format(num_features, dateList[0]))
plt.tick_params(right=True, which="both", direction="in")
plt.tight_layout()
plt.show()

## Plot a hex bin of feature duration * size
fig, ax = plt.subplots()
hb = ax.hexbin(dryDayLens,
    features_ha,
    gridsize = 12,
    yscale = 'log',
    cmap = 'Blues',
    bins = 'log')
plt.xlabel("Duration (days)")
plt.ylabel("Area (ha)")
cb = fig.colorbar(hb, ax=ax)
cb.set_label('Count')
plt.tick_params(right=True, which="both", direction="in")
plt.tight_layout()
plt.show()

## Raster + crs output of first slice
# Where are we saving the file?
destPath = "/Users/exnihilo/Box_Sync/Work/Conferences/AGU2018/first_slice_class.tif"

# Prepare the mask values
mask = allExtents.copy()
rasterOut = firstSlice.copy()
# 255 is the "nodata" value
rasterOut[mask == 0] = 255

# Open any classified raster as source--we just need to copy the profile
with rasterio.open(dataPaths[0]) as src:
    # Copy driver, dimensions, data type, crs, etc.
    matchParams = src.profile
    # Open the write stream
    with rasterio.open(destPath, 'w', **matchParams) as dest:
        # Write the raster to disk
        dest.write(rasterOut, 1)
    
## Raster + crs output of all slices
# Where are we saving the file?
destBase = "/Users/exnihilo/Box_Sync/tmp/2017-05/Gap-filled/"

# Open any classified raster as source--we just need to copy the profile
with rasterio.open(dataPaths[0]) as src:
    # Copy driver, dimensions, data type, crs, etc.
    matchParams = src.profile
    
    for index, rSlice, date in zip(range(len(rasterData)), rasterData, dateList):
        destPath = destBase + "GF_" + date.isoformat() + ".tif"
        # Open the write stream
        with rasterio.open(destPath, 'w', **matchParams) as dest:
            rasterOut = rSlice.copy()
            maskOut = np.bitwise_or.reduce(extents[index:], axis = 0)
            # 255 is the "nodata" value
            rasterOut[maskOut == 0] = 255
            # Write the raster to disk
            dest.write(rasterOut, 1)
    