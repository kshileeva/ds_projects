from cmath import pi
from bokeh.io import output_file
from bokeh.layouts import gridplot
from bokeh.plotting import figure, save
from bokeh.models import LinearAxis, Range1d, HoverTool, WheelZoomTool
import pandas as pd
import os
from math import pi
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.palettes import Category20
from bokeh.transform import cumsum
import pandas as pd


file_path = 'combined_sales_file.csv'
df_table = pd.read_csv(file_path)
df = pd.DataFrame(df_table)
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format='mixed', errors='coerce')
df['month'] = df['Transaction Date'].dt.month
df_table['Amount'] = df_table['Amount'].astype(float)
monthly_data = df.groupby('month').agg({'Amount': 'sum', 'Description': 'count'}).reset_index()
months = monthly_data['month'].tolist()
amounts = monthly_data['Amount'].tolist()
volumes = monthly_data['Description'].tolist()
l = figure(width=800,
           height=400,
           title='Monthly Revenue and Transaction Volume Trends',
           x_axis_label='Month',
           y_axis_label='Transaction Amount'
           )

am_renderer = l.line(months, amounts, color='navy', line_width=2, legend_label='Transaction Amount')
vol_renderer = l.line(months, volumes, color='red', line_width=2, legend_label='Transaction Volume', y_range_name='volume_range')
hover_am = [
    ("Month", "@x{int}"),
    ("Transaction Amount", "@y{1.11}")
]
hover_vol = [
    ("Month", "@x{int}"),
    ("Transaction Volume", "@y")
]
l.hover.mode = 'vline'
l.extra_y_ranges = {'volume_range': Range1d(start=0, end=700)}
l.add_layout(LinearAxis(y_range_name='volume_range', axis_label='Transaction Volume'), 'right')

tool_am = HoverTool(renderers=[am_renderer], tooltips=hover_am, formatters={'@x': 'numeral'})
tool_vol = HoverTool(renderers=[vol_renderer], tooltips=hover_vol, formatters={'@x': 'numeral'})
l.legend.location = 'bottom_left'
l.legend.click_policy = "hide"
l.add_tools(tool_vol, tool_am)

monthly_sku_amount = pd.DataFrame(columns=['month', 'premium', 'unlockcharactermanager'])
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format='mixed', errors='coerce')
df['month'] = df['Transaction Date'].dt.month
premium_amount = df[df['Sku Id'] == 'premium'].groupby('month')['Amount'].sum()
unlockcharactermanager_amount = df[df['Sku Id'] == 'unlockcharactermanager'].groupby('month')['Amount'].sum()

monthly_sku_amount['month'] = premium_amount.index
monthly_sku_amount['premium'] = premium_amount.values
monthly_sku_amount['unlockcharactermanager'] = unlockcharactermanager_amount.values

month = monthly_sku_amount['month'].tolist
premium = monthly_sku_amount['premium'].tolist
unlockcharactermanager = monthly_sku_amount['month'].tolist

b = figure(width=600,
           height=600,
           title='Transaction Amounts by SKU ID',
           x_axis_label='Month',
           y_axis_label='Transaction Amount')

pre_renderer = b.vbar(x=monthly_sku_amount['month'], top=monthly_sku_amount['premium'], width=0.3, color='orange',
                      legend_label='premium')

unlock_renderer = b.vbar(x=monthly_sku_amount['month']+0.3, top=monthly_sku_amount['unlockcharactermanager'],
                         width=0.3, color='blue', legend_label='unlockcharactermanager')

hover_pre = [('Month', '@x{int}'), ('premium', "@top{1.11}")]
tool_pre = HoverTool(renderers=[pre_renderer], tooltips=hover_pre, formatters={'@x': 'numeral', '@y': 'printf'})

hover_unlock = [('Month', '@x{int}'), ('unlockcharactermanager', '@top{1.11}')]
tool_unlock = HoverTool(renderers=[unlock_renderer], tooltips=hover_unlock, formatters={'@x': 'numeral'})

b.add_tools(tool_pre, tool_unlock)
b.legend.click_policy = "hide"
country_transaction = df.groupby('Buyer Country')['Amount'].sum().reset_index()
country_transaction_sorted = country_transaction.sort_values(by='Amount', ascending=False)


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

s = figure(width=800, height=600, x_axis_type="datetime", x_axis_label='Date', tools="pan,save,reset",
           title='Correlation between Daily Crashes and User Ratings')
s.background_fill_color = "#fafafa"

crashes_renderer = s.scatter(dates, crashes, color='#de2d26', size=7, legend_label='Crashes')
s.yaxis.axis_label = "Crashes"
s.yaxis.axis_label_text_color = "#de2d26"

s.extra_y_ranges['foo'] = Range1d(-0.1, 5.2)
rating_renderer = s.scatter(dates, rating, color='blue', size=6, y_range_name="foo", legend_label='Rating')

ax2 = LinearAxis(axis_label="Rating", y_range_name="foo", axis_label_text_color='blue')
s.add_layout(ax2, 'right')

wheel_zoom = WheelZoomTool()
s.add_tools(wheel_zoom)
s.toolbar.active_scroll = wheel_zoom

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
s.add_tools(hover_crashes, hover_rating)
s.legend.location = 'bottom_right'
s.legend.click_policy = "hide"


file_path_c = 'combined_sales_file.csv'
df_table_c = pd.read_csv(file_path_c)

df_c = pd.DataFrame(df_table_c)

country_transaction_c = df_c.groupby('Buyer Country')['Amount'].sum().reset_index()
country_transaction_sorted_c = country_transaction_c.sort_values(by='Amount', ascending=False)

top_9 = country_transaction_sorted_c.head(9)
others = pd.DataFrame({'Buyer Country':['Others'],
                       'Amount': [country_transaction_sorted_c['Amount'][9:].sum()]
                           })
result_dataframe_c = pd.concat([top_9, others])

data_c = pd.DataFrame(result_dataframe_c).reset_index(drop=True)
data_c['angle'] = data_c['Amount']/data_c['Amount'].sum() * 2*pi
data_c['color'] = Category20[len(result_dataframe_c)]

hover = HoverTool(
    tooltips=[("Country", "@{Buyer Country}"),
              ("Amount", "@Amount{1,11}")])

c = figure(height=400, title="Percentage of Transaction Amounts by Country", toolbar_location=None,
           tools=[hover], x_range=(-0.5, 1.0))


c.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='Buyer Country', source=data_c)

c.axis.axis_label = None
c.axis.visible = False
c.grid.grid_line_color = None


all_grid = gridplot([[l, c], [s, b]])
output_file('all_plots.html')
save(all_grid)