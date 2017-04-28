# Use the SimpleKML library to turn the GPS cooordinates into a KML file

import simplekml
from collect_dir_data import gps_dir_df

# Instantiation of kml object
kml = simplekml.Kml()
# Where is the directory with the GPS-tagged images?
# searchDir = "/images/path/here/*.JPG"
gps_df = gps_dir_df(searchDir)
# Name of the linestring
# lsName = "Name/title here"
ls = kml.newlinestring(name=lsName)
# Long, lat, and alt in df to kml
subset = gps_df[['Longitude', 'Latitude', 'MSL_Altitude']]
tuples = [tuple(x) for x in subset.values]
ls.coords = tuples
ls.altitudemode = simplekml.AltitudeMode.absolute

# Line styles and names
ls.extrude = 1
ls.style.linestyle.width = 2
ls.style.linestyle.color = simplekml.Color.blue

# Save to current directory
# kmlName = "filename.kml"
kml.save(kmlName)
