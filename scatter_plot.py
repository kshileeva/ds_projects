from bokeh.plotting import figure, show
from bokeh.models import LogAxis, DataRange1d, ColumnDataSource, DatetimeTickFormatter
from datetime import datetime
import numpy as np
import os
import pandas as pd
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
source = ColumnDataSource(merged_df)
p = figure(x_axis_type='datetime', x_axis_label='Date', y_axis_label='Daily Average Rating')
p.scatter(x='Date', y='Daily Average Rating', source=source, color='blue')
p.extra_y_ranges = {"second_y_axis": DataRange1d(start=0, end=90)}
p.add_layout(LogAxis(y_range_name="second_y_axis", axis_label="Crashes"), 'right')
p.scatter(x='Date', y='Crashes', source=source, color='red', y_range_name="second_y_axis")
show(p)