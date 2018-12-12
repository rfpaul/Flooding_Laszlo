## Parse classifier statistics
# Parse statistics from classifier text output files into a CSV

## Import packages
import glob
import re
import datetime as dt
import pandas as pd

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
    inFiles = glob.glob(pathPattern)
    
    # Parse a list of dates from the list of rasters paths
    dateList = [ParseDate(x) for x in inFiles]
    # Sort the dates into chronologcial order
    dateSort = sorted(dateList)
    # Get the order of indices in chronological order
    chronOrderIndices = [dateList.index(x) for x in dateSort]
    pathSort = [inFiles[i] for i in chronOrderIndices]
    
    # Return resulting sorted filepaths and their dates
    return pathSort, dateSort

def ParseFile(filepaths, dates):
    # Column names
    colNames = ["Date"]
    # List of data rows, initialized to empty
    dataRows = []
    
    # For each text file stats report...
    for path, currentDate in zip(filepaths, dates):
        # Open as read-only
        with open(path, 'r') as txt:
            # Add the date to the row
            currentRow = [currentDate]
            for line in txt.readlines():
                # Is there a colon in the line? If so, this is a line with data.
                if ':' in line:
                    # Remove whitespace and split the line at the colon
                    parsed = line.strip().split(' : ')
                    # Is this the first file? Get the column name
                    if path == filepaths[0]:
                        colNames.append(parsed[0])
                    # Append the data
                    currentRow.append(parsed[1])
            dataRows.append(currentRow)
    
    # Collect the data into a pandas dataframe
    df = pd.DataFrame(dataRows, columns = colNames)
    return df

## Global variables
# Searchable pattern for the filepaths of the statistics output data
dataPathPattern = "/Users/exnihilo/tmp/2017-05/Statistics/*_Training.txt"
dataPaths, dateList = SortExtractChrono(dataPathPattern)
# Pathname for output file
outputPath = "/Users/exnihilo/tmp/2017-05/Statistics/Collected_training_stats.csv"

## Main script run
# Collect the data into a pandas dataframe
dfOut = ParseFile(dataPaths, dateList)
# Save as a CSV
dfOut.to_csv(outputPath, index = False)
