from bokeh.models import ColumnDataSource, LinearAxis, Range1d
from bokeh.plotting import figure, show
from numpy import arange, linspace, pi, sin
import pandas as pd
import os
directory = "assignment1_data"
dfs_rating = []
dfs_crashes = []
for filename in os.listdir(directory):
    if filename.startswith("stats_ratings_") and filename.endswith("_overview.csv"):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath, encoding='UTF-16')
        dfs_rating.append(df)
    if filename.startswith("stats_crashes_") and filename.endswith("_overview.csv"):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath, encoding='UTF-16')
        dfs_crashes.append(df)
merged_rating = pd.concat(dfs_rating, ignore_index=True)
merged_rating = merged_rating.fillna(0)
merged_crash = pd.concat(dfs_crashes, ignore_index=True)
ratings = merged_rating.drop(['Package Name'], axis=1)
crashes = merged_crash.drop(['Package Name'], axis=1)
merged_df = pd.merge(crashes, ratings, on='Date', how='inner')
merged_df['Date'] = pd.to_datetime(merged_df['Date'])
merged_df['Crashes'] = merged_df['Daily Crashes'] + merged_df['Daily ANRs']
merged_df.drop(['Daily Crashes', 'Daily ANRs'], axis=1, inplace=True)

x = arange(-2*pi, 2*pi, 0.2)
y = merged_df['Crashes']
y2 = merged_df['Daily Average Rating']
dates = pd.date_range(start='2024-01-01', periods=len(x))

source = ColumnDataSource(data={'x': merged_df['Date'], 'y': y, 'y2': y2})

# Create figure
p = figure(x_axis_type='datetime', y_axis_label='Crashes', width=800, height=500)

# Plot Crashes on primary y-axis
p.scatter('x', 'y2', source=source, color="navy", size=8)

# Define the range for the secondary y-axis (ratings)
p.extra_y_ranges = {"ratings": Range1d(start=0, end=5)}

# Plot Ratings on secondary y-axis
p.scatter('x', 'y', source=source, color="crimson", size=8, y_range_name="ratings")

# Add secondary y-axis to the plot
ax2 = LinearAxis(y_range_name="ratings", axis_label="Rating")
p.add_layout(ax2, 'right')

# Show the plot
show(p)
