from bokeh.plotting import figure, show
from bokeh.models import LinearAxis, Range1d, HoverTool, WheelZoomTool
import os
import pandas as pd
directory = "assignment1_data"
dfs_rating = []
dfs_crashes = []
dsf_reviews = []
for filename in os.listdir(directory):
    if filename.startswith("stats_ratings_") and filename.endswith("_overview.csv"):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath, encoding='UTF-16')
        dfs_rating.append(df)
    elif filename.startswith("stats_crashes_") and filename.endswith("_overview.csv"):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath, encoding='UTF-16')
        dfs_crashes.append(df)

merged_rating = pd.concat(dfs_rating, ignore_index=True)
merged_rating['Daily Average Rating'].fillna(merged_rating['Total Average Rating'], inplace=True)
merged_crash = pd.concat(dfs_crashes, ignore_index=True)
ratings = merged_rating.drop(['Package Name'], axis=1)
crashes = merged_crash.drop(['Package Name'], axis=1)
merged_df = pd.merge(crashes, ratings, on='Date', how='inner')
merged_df['Date'] = pd.to_datetime(merged_df['Date'])
merged_df['Crashes'] = merged_df['Daily Crashes'] + merged_df['Daily ANRs']
merged_df.drop(['Daily Crashes', 'Daily ANRs'], axis=1, inplace=True)
crashes = merged_df['Crashes'].tolist()
rating = merged_df['Daily Average Rating'].tolist()
dates = merged_df['Date'].tolist()

p = figure(width=900, height=600, x_axis_type="datetime", x_axis_label='Date', tools="pan,save,reset",
           title='Correlation between Daily Crashes and User Ratings')
p.background_fill_color = "#fafafa"

crashes_renderer = p.scatter(dates, crashes, color='#de2d26', size=7, legend_label='Crashes')
p.yaxis.axis_label = "Crashes"
p.yaxis.axis_label_text_color = "#de2d26"

p.extra_y_ranges['foo'] = Range1d(-0.1, 5.2)
rating_renderer = p.scatter(dates, rating, color='blue', size=6, y_range_name="foo", legend_label='Rating')

ax2 = LinearAxis(axis_label="Rating", y_range_name="foo", axis_label_text_color='blue')
p.add_layout(ax2, 'right')

wheel_zoom = WheelZoomTool()
p.add_tools(wheel_zoom)
p.toolbar.active_scroll = wheel_zoom

tooltips_crashes = [
    ("Date", "@x{%F}"),
    ("Crashes", "@y")
]

tooltips_rating = [
    ("Date", "@x{%F}"),
    ("Daily Average Rating", "@y{0.0}")
]

hover_crashes = HoverTool(renderers=[crashes_renderer], tooltips=tooltips_crashes, formatters={'@x': 'datetime'})
hover_rating = HoverTool(renderers=[rating_renderer], tooltips=tooltips_rating, formatters={'@x': 'datetime'})
p.add_tools(hover_crashes, hover_rating)
p.legend.location = 'bottom_right'
p.legend.click_policy = "hide"
show(p)
