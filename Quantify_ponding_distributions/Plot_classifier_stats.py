## Plot classifier statistical summary

## Import packages
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc_file

# Matplotlib parameters file
rc_file("/Users/exnihilo/Box_Sync/Data/Soil_flooding_data_figs_docs/Documents/aguposter2018rc")

## Global variables
statsPath = "/Users/exnihilo/tmp/2017-05/Statistics/Collected_training_stats.csv"

# Which columns are we using?
keepCols = ['Date',
            'Accuracy',
            'Kappa',
            "Neg Pred Value",
            "Specificity"]

# Note that we're inverting the standard definitions for negative prediction
# and specificity; the model assumed '0' was the positive class instead of '1'
renameCols = {"Accuracy":"Overall accuracy",
    "Neg Pred Value":"Consumer's accuracy for water",
    "Specificity":"Producer's accuracy for water"}

## Main script run
# Open the CSV file
df = pd.read_csv(statsPath)

# Restrict to the columns we're using for plotting
df = df.get(keepCols)
# Rename some of the columns
df = df.rename(renameCols, axis = 'columns')
#df["Date"] = pd.to_datetime(df["Date"], format = "%Y-%m-%d")
df = df.set_index("Date")

## Plot the data
fig, ax = plt.subplots()
barWidth = 0.12
colorList = ["gold", "coral", "mediumturquoise", "steelblue"]

barIndex = np.arange(len(df.index))

for i, col in enumerate(df):
    ax.bar(barIndex + (barWidth * (i - (len(df.columns) / 2 ) ) ) + (barWidth / 2),
        df[col].values,
        width = barWidth,
        color = colorList[i],
        label = col)
# Rotates labels and aligns them horizontally to left 
plt.setp( ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
plt.xlabel("Date")
plt.ylabel("Proportion")
# Turn on left and right Y-axis tick marks, turn them inside the plot
plt.tick_params(right=True, which="both", direction="in")
plt.xticks(barIndex, df.index)
ax.legend(loc = 'lower left')
plt.tight_layout()
plt.show()
