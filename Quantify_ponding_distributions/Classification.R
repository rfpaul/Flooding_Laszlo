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
# dateVec <-  c('2017-08-19', '2017-09-09')
# dateVec <-  c('2017-05-02', '2017-05-05', '2017-05-06', '2017-05-07',
#                '2017-05-09', '2017-05-10', '2017-05-13', '2017-05-14',
#                '2017-05-15')
dateVec <- c('2017-05-02', '2017-05-09', '2017-05-13')

userPath <- "~/Box_Sync/tmp/2017-05/"

mosaicPath <- paste0(userPath, "Mosaics/")
mosaicSuffix <- "_cbw_masked-mosaic_3m.tif"

naFlagPath <- paste0(userPath, "NA Flagged/")
naFlagSuffix <- "_R_na-flagged_mosaic_3m.tif"

trainerPath <- "~/Box_Sync/GIS/Flooding_Remote_Sensing/PLabs/Combined_Trainer_Polys/2017-05_Combined_Trainers_Cai+Paul.shp"

classPath <- paste0(userPath, "Classified/R_randomforest_bin-class_")
classSuffix <- ".tif"

statsPath <- paste0(userPath, "Statistics/")
statsSuffix <- "_Training.txt"

polysIn <- readOGR(trainerPath)

for(i in seq_len(length(dateVec))) {
  thisDate <- dateVec[i]
  print(paste0("Starting on ", thisDate))
  
  # # Open the mosaic that has zeroes where NAs should be
  # filepath <- paste0(mosaicPath, thisDate, mosaicSuffix)
  # r <- brick(filepath)
  # 
  # startTime <- Sys.time()

  filepath <- paste0(naFlagPath, thisDate, naFlagSuffix)
  
  # Write the new raster with NAs flagged as 0 values
  # writeRaster(r,
  #             filepath,
  #             format = "GTiff",
  #             overwrite = TRUE,
  #             datatype = "INT2U",
  #             NAflag = 0)
  # endTime <- Sys.time()
  # print(paste0(filepath, " finished: ", endTime - startTime, " m"))
  
  # Load the NA-flagged files
  plabs <- brick(filepath)
  outPath <- paste0(classPath, thisDate, classSuffix)
  
  # Restrict to the date we're looking at
  train <- polysIn[polysIn$strDate == thisDate,]
  # Redefine class factors; caret (via superClass) will use the first factor
  # as the "positive" class
  train$class <- factor(train$class, levels = c(1, 0))
  
  startTime <- Sys.time()
  # Begin CPU parallellization
  beginCluster()
  
  # Fit classifier (Random Forests; 50 trees; 10-fold cross-validation,
  # splitting training into 90% training/CV data, 10% validation data; validate
  # folds on Kappa value; cross-validate by polygon)
  # Should run parallelized
  SC <- superClass(plabs, trainData = train, responseCol = "class",
                   model = "rf", nSamples = 275000, kfold = 10, minDist = 1, 
                   na.action = na.omit, trainPartition = 0.9, verbose = TRUE,
                   predict = FALSE, metric = "Kappa", ntree = 50,
                   polygonBasedCV = TRUE)
  endTime <- Sys.time()
  print(paste0("Finished training: ", endTime - startTime, " m"))
  
  print(paste0("Starting prediction on ", thisDate))
  startTime <- Sys.time()
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
  
  # Save the model and validation statistics to file
  sink(file = paste0(statsPath, thisDate, statsSuffix))
  print(thisDate)
  print(SC$model)
  print(SC$modelFit)
  print(SC$validation$performance)
  
  # Reset to output to console only
  sink()
}
