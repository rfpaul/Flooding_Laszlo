# Parses Sentinel manifest XML into a list of beginposition date times
# and outputs them into a CSV file

## Package imports
import csv
import datetime as dt
import xml.etree.ElementTree as ET

## Begin script run
# Where's the XML manifest?
inFile = "/mnt/Box_sync/Data/SW_Champaign_query_results.xml"
# Where is the save location?
outFile = "/mnt/Box_sync/Data/sentinel-1_SW_Champaign_passes.csv"

tree = ET.parse(inFile)
root = tree.getroot()

# Empty list to store dates
dates = []

# Find all the 'beginposition' attributes in the XML file
for day in root.findall('.//*[@name="beginposition"]'):
    # Convert string to datetime object
    currDay = dt.datetime.strptime(day.text, "%Y-%m-%dT%H:%M:%S.%fZ")
    # Append to list of dates
    dates.append(currDay)

# Initiate filestream for output
with open(outFile, mode='w') as fstream:
    # Initiate CSV writer
    csv_writer = csv.writer(fstream)
    # Write header
    csv_writer.writerow(["Datetime", "Date", "Year", "Month", "Day"])
    # Write each date to a row in the CSV file
    for day in dates:
        csv_writer.writerow([day, day.date(), day.year, day.month, day.day])
