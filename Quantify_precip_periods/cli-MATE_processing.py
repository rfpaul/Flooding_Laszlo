# coding: utf-8
# Import packages
import pandas as pd
from matplotlib import pyplot as plt

# Get data
myPrecip = pd.read_csv("~/Box_Sync/Data/Soil_flooding_data_figs/Data/cli-MATE_precip_SD_b2dates.csv")
# Format date strings as datetime objects
myPrecip["DATE"] = pd.to_datetime(myPrecip["DATE"])
# Make the date the index
myPrecip = myPrecip.set_index("DATE")
# Set the value outputs to 5 decimal places
pd.options.display.float_format = '{:.5g}'.format

# 3-day rolling sum
myPrecip["3-day"] = myPrecip["PRCP"].rolling(window = 3).sum()
print(myPrecip["3-day"].describe(
    percentiles = [.1, .15, .2, .25, .5, .75, .8, .9, .95, .99]), '\n')

# 5-day rolling sum
myPrecip["5-day"] = myPrecip["PRCP"].rolling(window = 5).sum()
print(myPrecip["5-day"].describe(
    percentiles = [.1, .15, .2, .25, .5, .75, .8, .9, .95, .99]), '\n')

# 10-day rolling sum
myPrecip["10-day"] = myPrecip["PRCP"].rolling(window = 10).sum()
print(myPrecip["10-day"].describe(
    percentiles = [.1, .15, .2, .25, .5, .75, .8, .9, .95, .99]))

# Separate out high and low precip periods
lowPrecip = myPrecip[myPrecip["10-day"] <= .3]
highPrecip = myPrecip[myPrecip["5-day"] >= 1.6]

## Plot the data
ax = myPrecip.plot(linewidth = .5)
plt.tight_layout()
plt.show()
