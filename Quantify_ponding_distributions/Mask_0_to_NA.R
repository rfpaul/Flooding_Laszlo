library(raster)
# library(parallel)

# extReference <- raster("~/Box_Sync/GIS/Flooding_Remote_Sensing/Masks/2017_champaign_3m_mask.tif")
# masking <- extReference

dateVec = c('2017-05-05')

for(i in seq_len(length(dateVec))) {
  thisDate = dateVec[i]
  
  filepath <- Sys.glob(paste0("~/tmp/", thisDate, "*-mosaic_3m.tif"))
  r <- brick(filepath)
  
  startTime <- Sys.time()
  #beginCluster()
  # redef <- clusterR(r,
  #                   reclassify,
  #                   args = list(rcl = cbind(0, NA)),
  #                   filename = paste0("~/tmp/", thisDate, "_R-na_mask.tif"),
  #                   overwrite = TRUE,
  #                   datatype = "INT2U")
  writeRaster(r,
              paste0("~/tmp/", thisDate, "_R-na_mask.tif"),
              format = "GTiff",
              overwrite = TRUE,
              datatype = "INT2U",
              NAflag = 0)
  #endCluster()
  endTime <- Sys.time()
  print(paste0(filepath, ": ", endTime - startTime))
}