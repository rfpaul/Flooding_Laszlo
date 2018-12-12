library(caret)
library(sp)
library(rgdal)
library(randomForest)
library(e1071)
library(raster)
library(parallel)
library(doParallel)
library(RStoolbox)
library(raster)

# Check extents of '2017-05-10' and '2017-05-14'!!
dateVec <-  c('2017-05-13')
# dateVec <-  c('2017-05-02', '2017-05-05', '2017-05-06', '2017-05-07',
#               '2017-05-09', '2017-05-10', '2017-05-13', '2017-05-14',
#               '2017-05-15')

userPath <- "~/tmp/2017-05/"

mosaicPath <- paste0(userPath, "Mosaics/")
mosaicSuffix <- "_cbw_masked-mosaic_3m.tif"

naFlagPath <- paste0(userPath, "NA Flagged/")
naFlagSuffix <- "_R_na-flagged_mosaic_3m.tif"

trainerPath <- paste0(userPath, "2017-05_Combined_Trainers_Cai+Paul.shp")

classPath <- paste0(userPath, "Classified/R_randomforest_bin-class_")
classSuffix <- ".tif"

statsPath <- paste0(userPath, "Statistics/")
statsSuffix <- "_Training.txt"

polysIn <- readOGR(trainerPath)

for(i in seq_len(length(dateVec))) {
  thisDate <- dateVec[i]
  print(paste0("Starting on ", thisDate))
  
  filepath <- paste0(mosaicPath, thisDate, mosaicSuffix)
  r <- brick(filepath)
  
  startTime <- Sys.time()

  filepath <- paste0(naFlagPath, thisDate, naFlagSuffix)
  writeRaster(r,
              filepath,
              format = "GTiff",
              overwrite = TRUE,
              datatype = "INT2U",
              NAflag = 0)
  #endCluster()
  endTime <- Sys.time()
  print(paste0(filepath, " finished: ", endTime - startTime, " m"))
  
  plabs <- brick(filepath)
  outPath <- paste0(classPath, thisDate, classSuffix)
  
  # Restrict to the date we're looking at
  train <- polysIn[polysIn$strDate == thisDate,]
  
  startTime <- Sys.time()
  # Begin CPU parallellization
  beginCluster()

  ## Fit classifier (splitting training into 90% training data, 10% validation data)
  # Should run parallelized
  SC <- superClass(plabs, trainData = train, responseCol = "class", model = "rf",
                   tuneLength = 1, nSamples = 500000,
                   na.action = na.omit, trainPartition = 0.9, verbose = TRUE,
                   predict = FALSE)
  endTime <- Sys.time()
  print(paste0("Finished training: ", endTime - startTime, " m"))
  
  # Classification of predicted classification values, parallelized
  map <- clusterR(plabs,
                  predict,
                  args = list(model = SC[[1]], datatype = "INT1U"))
  
  writeRaster(map,
              outPath,
              format = "GTiff",
              overwrite = TRUE,
              datatype = "INT1U")
  
  # End parallelization
  endCluster()
  endTime <- Sys.time()
  print(paste0(thisDate, " finished predicting: ", endTime - startTime, " m"))
  
  # Report the training statistics
  sink(file = paste0(statsPath, thisDate, statsSuffix))
  print(SC)
  # Reset to output to console
  sink()
}