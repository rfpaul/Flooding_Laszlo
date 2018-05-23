# Import packages
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

# Get precip data
myPrecip = pd.read_csv("/mnt/Box_sync/Data/cli-MATE_precip_SD_b2dates.csv")
# Get Sentinel-1 pass data
satPasses = pd.read_csv("/mnt/Box_sync/Data/sentinel-1_combined_Champaign_passes.csv")

# Format date strings as datetime objects
myPrecip["DATE"] = pd.to_datetime(myPrecip["DATE"])
satPasses["Date"] = pd.to_datetime(satPasses["Date"])
# Make the date the index
myPrecip = myPrecip.set_index("DATE")
satPasses = satPasses.set_index("Date")

# 5-day rolling sum
myPrecip["5-day rolling sum"] = myPrecip["PRCP"].rolling(window = 5).sum()

# 10-day rolling sum
myPrecip["10-day rolling sum"] = myPrecip["PRCP"].rolling(window = 10).sum()

# 30-day rolling sum
myPrecip["30-day rolling sum"] = myPrecip["PRCP"].rolling(window = 30).sum()

## Plot the high precip data
ax = myPrecip["5-day rolling sum"].plot(figsize=(9, 6),
    c = "black",
    linewidth = .75)
plt.xlabel("date")
plt.ylabel("precipitation (in)")
plt.tick_params(top='off', right = 'on', direction = 'in')
# 90th percentile cutoff for high values
ax.axhline(1.6, c = "blue", linestyle = ":")
# Dates of full coverage passes
[ax.axvline(x, c = "orange", linestyle = "--", linewidth = 1) 
    for x in satPasses[satPasses["Quadrants"] == 4].index]
# Dates of partial coverage passes
[ax.axvline(x, c = "darkred", linestyle = "--", linewidth = 1) 
    for x in satPasses[satPasses["Quadrants"] == 2].index]
# Legend lines
custom_lines = [Line2D([0], [0], color="black", lw=.75),
                Line2D([0], [0], color="blue", ls = ":"),
                Line2D([0], [0], color="orange", ls="--", lw=1),
                Line2D([0], [0], color="darkred", ls="--", lw=1)]
# Draw legend
ax.legend(custom_lines, 
    ["5-day rolling sum",
    "90th percentile",
    "Sentinel-1 total coverage",
    "Sentinel-1 partial coverage"])
plt.tight_layout()
plt.show()

## Plot the low precip data
ax = myPrecip["30-day rolling sum"].plot(figsize=(9, 6),
    c = "black",
    linewidth = .75)
plt.xlabel("date")
plt.ylabel("precipitation (in)")
plt.tick_params(top='off', right = 'on', direction = 'in')
# 20th percentile cutoff for low values
ax.axhline(1.25, c = "blue", linestyle = ":")
# Dates of full coverage passes
[ax.axvline(x, c = "orange", linestyle = "--", linewidth = 1) 
    for x in satPasses[satPasses["Quadrants"] == 4].index]
# Dates of partial coverage passes
[ax.axvline(x, c = "darkred", linestyle = "--", linewidth = 1) 
    for x in satPasses[satPasses["Quadrants"] == 2].index]
# Draw legend
ax.legend(custom_lines, 
    ["30-day rolling sum",
    "10th percentile",
    "Sentinel-1 total coverage",
    "Sentinel-1 partial coverage"])
plt.tight_layout()
plt.show()
