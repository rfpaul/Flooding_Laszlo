# Import packages
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import rc_file

# Matplotlib parameters file
rc_file("/Users/exnihilo/Box_Sync/Data/Soil_flooding_data_figs_docs/Documents/manuscript_figure_rc_params")

## Load data

# Get precip data
myPrecip = pd.read_csv("/Users/exnihilo/Box_Sync/Data/Soil_flooding_data_figs_docs/Data/cli-MATE/cli-MATE_precip_SD_b2dates.csv")
# Get Sentinel-1 pass data
satPasses = pd.read_csv("/Users/exnihilo/Box_Sync/Data/Soil_flooding_data_figs_docs/Data/Sentinel-1/sentinel-1_combined_Champaign_passes.csv")

# Format date strings as datetime objects
myPrecip["DATE"] = pd.to_datetime(myPrecip["DATE"])
satPasses["Date"] = pd.to_datetime(satPasses["Date"])
# Make the date the index
myPrecip = myPrecip.set_index("DATE")
satPasses = satPasses.set_index("Date")

# Convert to mm
myPrecip["PRCP"] = myPrecip["PRCP"] * 25.4

# Select the year 2017
myPrecip = myPrecip['2017']

# 5-day rolling sum
myPrecip["5-day rolling sum"] = myPrecip["PRCP"].rolling(window = 5).sum()

# 10-day rolling sum
myPrecip["10-day rolling sum"] = myPrecip["PRCP"].rolling(window = 10).sum()

# 30-day rolling sum
myPrecip["30-day rolling sum"] = myPrecip["PRCP"].rolling(window = 30).sum()

plotColor = 'black'
cutoffColor = 'blue'

# Legend lines
custom_lines = [Line2D([0], [0], color=plotColor),
                Line2D([0], [0], color=cutoffColor, ls = ":"),
                Line2D([0], [0], color="orange", ls="--", lw=1),
                Line2D([0], [0], color="darkred", ls="--", lw=1)]

## Plot the high precip data
fig, ax = plt.subplots()
ax = myPrecip["5-day rolling sum"].plot(color = plotColor)
plt.xlabel("Date")
plt.ylabel("Precipitation (mm)")
plt.tick_params(top = False, right = True, direction = 'in')
# 90th percentile cutoff for high values
upperPercentile = myPrecip["5-day rolling sum"].quantile(0.9)
ax.axhline(upperPercentile,
    c = cutoffColor,
    linestyle = ":",
    label = "90$^{th}$ percentile")
# # Dates of full coverage passes
# [ax.axvline(x, c = "orange", linestyle = "--", linewidth = 1) 
#     for x in satPasses[satPasses["Quadrants"] == 4].index]
# # Dates of partial coverage passes
# [ax.axvline(x, c = "darkred", linestyle = "--", linewidth = 1) 
#     for x in satPasses[satPasses["Quadrants"] == 2].index]

# Draw legend
#handles, labels = ax.get_legend_handles_labels()
#ax.legend(handles, labels)
ax.legend()

# Draw arrow
ax.arrow(dt.date(2017, 3, 31),
    101.84,
    30,
    0,
    width = 1.5,
    length_includes_head = True,
    color = 'black')

plt.tight_layout()
plt.show()

## Plot the low precip data
fig, ax = plt.subplots()
ax = myPrecip["10-day rolling sum"].plot(c = plotColor)
plt.xlabel("Date")
plt.ylabel("Precipitation (mm)")
# Turn on left and right Y-axis tick marks, turn them inside the plot
plt.tick_params(right=True, which="both", direction="in")
# 20th percentile cutoff for low values
lowerPercentile = myPrecip["10-day rolling sum"].quantile(0.2)
ax.axhline(lowerPercentile,
    c = cutoffColor,
    label = "20$^{th}$ percentile",
    linestyle = ":")
# # Dates of full coverage passes
# [ax.axvline(x, c = "orange", linestyle = "--", linewidth = 1) 
#     for x in satPasses[satPasses["Quadrants"] == 4].index]
# # Dates of partial coverage passes
# [ax.axvline(x, c = "darkred", linestyle = "--", linewidth = 1) 
#     for x in satPasses[satPasses["Quadrants"] == 2].index]
# Draw legend
ax.legend()
#ax.legend(custom_lines, 
    #["10-day rolling sum",
    #"20th percentile"])
    # "Sentinel-1 total coverage",
    # "Sentinel-1 partial coverage"])
plt.tight_layout()
plt.show()
