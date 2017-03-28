# Collect GPS data from a glob search of directories
# Data is collected into a Pandas data frame
import datetime
import pandas as pd
from PIL import Image
import glob
# Extract EXIF data and GPS from images
from extract_gps import get_exif_data, get_exif_location

# Collect the GPS tags in a folder and output them as a pandas dataframe
def gps_dir_df(searchDir):
    filePaths = glob.glob(searchDir)
    
    gps_list = []
    
    for imagePath in filePaths:
        image = Image.open(imagePath)
        exif_data = get_exif_data(image)
        # GPS coordinates and MSL altitude
        gps_data = list(get_exif_location(exif_data))
        # Time of image capture in UTC
        captureTime = "{}:{} UTC".format(exif_data['DateTime'], 
                                        exif_data['SubsecTime'])
        dt_capture = datetime.datetime.strptime(
            captureTime, "%Y:%m:%d %H:%M:%S:%f %Z")
        # Build up a list of GPS data lists for casting into a data frame
        # [ [datetime, lat, lon, alt], ...]
        gps_data.insert(0, dt_capture)
        gps_list.append(gps_data)
    
    df = pd.DataFrame(
        gps_list,
        columns=["Datetime", "Latitude", "Longitude", "MSL_Altitude"])
    # Add relative altitudes vs. the minimum value recorded
    relAlt = df['MSL_Altitude'] - min(df['MSL_Altitude'])
    df = df.assign(Relative_Altitude=relAlt)
    #df.rename(columns={"rel" : "Relative Altitude"}, inplace=True)
    
    return df

################
# Example ######
################
if __name__ == "__main__":
    # Where is the directory with the GPS-tagged images?
    # searchDir = "/images/path/here/*.JPG"
    gps_df = gps_dir_df(searchDir)
    