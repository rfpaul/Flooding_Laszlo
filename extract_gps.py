# extract_gps.py
# Gets lat, lon, and alt from Parrot Sequoia exif tags
# Based on https://gist.github.com/erans/983821

import exifread
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data

def _get_if_exist(data, key):
    if key in data:
        return data[key]
    else:
        return None


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][0]) / float(value[2][1])

    return d + (m / 60.0) + (s / 3600.0)
    
def get_exif_location(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    lat = None
    lon = None
    mslAlt = None

    gps_latitude = _get_if_exist(exif_data['GPSInfo'], 'GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data['GPSInfo'], 'GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data['GPSInfo'], 'GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data['GPSInfo'], 'GPSLongitudeRef')
    gpsAlt = _get_if_exist(exif_data['GPSInfo'], 'GPSAltitude')
    gpsAlt_ref = _get_if_exist(exif_data['GPSInfo'], 'GPSAltitudeRef')
    
    # Were the data successfully extracted?
    if gps_latitude and \
        gps_latitude_ref and \
        gps_longitude and \
        gps_longitude_ref and \
        gpsAlt:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref != 'E':
            lon = 0 - lon
        
        mslAlt = gpsAlt[0]/gpsAlt[1]
        if gpsAlt_ref != 0:
            mslAlt = -(mslAlt)

    return lat, lon, mslAlt
    
################
# Example ######
################
if __name__ == "__main__":
    # Where is the image?
    # imagePath = "/image/path/here"
    image = Image.open(imagePath)
    exif_data = get_exif_data(image)
    print(get_exif_location(exif_data))