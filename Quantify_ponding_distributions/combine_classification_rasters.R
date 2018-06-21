# Import packages
library(raster)

# Combine rasters by adding them together; save the result
addRasters <- function(currDir) {
  # Find TIFFs for the current directory which have Corn or Soybean in the name
  rastFiles <- list.files(currDir,
                          pattern = "(Corn|Soybean).*.tif$",
                          full.names = TRUE)
  # Load raster files
  r1 <- raster(rastFiles[1])
  r2 <- raster(rastFiles[2])
  # Add the two rasters together
  result <- r1 + r2
  # Prepare the result filename by substituting text from another file path
  resultPath <- gsub("Corn|Soybean", "combined-no_compression", rastFiles[1])
  # Write the result
  writeRaster(result, resultPath, format = "GTiff", datatype = "INT1U", 
              options = c("COMPRESS=NONE"), overwrite = TRUE)
  message(paste("Wrote to", resultPath))
}

# Where are the directories for each date located?
rootFilepath <- "~/Box_Sync/Data/Soil_flooding_data_figs_docs/Data/CMI_ponded_soils_classifications"

# Get the target directories. Drop the first item in the vector.
targetDirs <- list.dirs(rootFilepath, full.names = TRUE)[-1]

# Save the result as an uncompressed, 8-bit integer GeoTIFF
# TODO: Fix the Python side of this workflow so compressed files work
# properly
# Alternative TODO: adapt the workflow to be entirely in R

# invisible() suppresses the console output from sapply
invisible(sapply(targetDirs, addRasters))
