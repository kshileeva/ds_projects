from math import pi
from bokeh.io import output_file, save
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d, HoverTool, WheelZoomTool
from bokeh.palettes import Category20
from bokeh.transform import cumsum
import pandas as pd
import os

# Load and preprocess data
file_path = 'combined_sales_file.csv'
df = pd.read_csv(file_path)
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format='mixed', errors='coerce')
df['month'] = df['Transaction Date'].dt.month
df['Amount'] = df['Amount'].astype(float)

# Monthly data
monthly_data = df.groupby('month').agg({'Amount': 'sum', 'Description': 'count'}).reset_index()
months = monthly_data['month'].tolist()
amounts = monthly_data['Amount'].tolist()
volumes = monthly_data['Description'].tolist()

# Plot monthly revenue and transaction volume trends
line_plot = figure(
    width=800,
    height=400,
    title='Monthly Revenue and Transaction Volume Trends',
    x_axis_label='Month',
    y_axis_label='Transaction Amount'
)
amount_renderer = line_plot.line(months, amounts, color='navy', line_width=2, legend_label='Transaction Amount')
volume_renderer = line_plot.line(months, volumes, color='red', line_width=2, legend_label='Transaction Volume',
                                 y_range_name='volume_range')

line_plot.hover.mode = 'vline'
line_plot.extra_y_ranges = {'volume_range': Range1d(start=0, end=700)}
line_plot.add_layout(LinearAxis(y_range_name='volume_range', axis_label='Transaction Volume'), 'right')

tool_amount = HoverTool(renderers=[amount_renderer], tooltips=[("Month", "@x{int}"), ("Transaction Amount", "@y{1.11}")]
                        , formatters={'@x': 'numeral'})
tool_volume = HoverTool(renderers=[volume_renderer], tooltips=[("Month", "@x{int}"), ("Transaction Volume", "@y")],
                        formatters={'@x': 'numeral'})

line_plot.legend.location = 'bottom_left'
line_plot.legend.click_policy = "hide"
line_plot.add_tools(tool_volume, tool_amount)

# Monthly SKU data
monthly_sku_amount = pd.DataFrame(columns=['month', 'premium', 'unlockcharactermanager'])
premium_amount = df[df['Sku Id'] == 'premium'].groupby('month')['Amount'].sum()
unlockcharactermanager_amount = df[df['Sku Id'] == 'unlockcharactermanager'].groupby('month')['Amount'].sum()

monthly_sku_amount['month'] = premium_amount.index
monthly_sku_amount['premium'] = premium_amount.values
monthly_sku_amount['unlockcharactermanager'] = unlockcharactermanager_amount.values

# Plot SKU transaction amounts
bar_plot = figure(
    width=600,
    height=600,
    title='Transaction Amounts by SKU ID',
    x_axis_label='Month',
    y_axis_label='Transaction Amount'
)
premium_renderer = bar_plot.vbar(x=monthly_sku_amount['month'], top=monthly_sku_amount['premium'], width=0.3,
                                 color='orange', legend_label='premium')
unlock_renderer = bar_plot.vbar(x=monthly_sku_amount['month'] + 0.3, top=monthly_sku_amount['unlockcharactermanager'],
                                width=0.3, color='blue', legend_label='unlockcharactermanager')

tool_premium = HoverTool(renderers=[premium_renderer], tooltips=[('Month', '@x{int}'), ('premium', "@top{1.11}")],
                         formatters={'@x': 'numeral', '@y': 'printf'})
tool_unlock = HoverTool(renderers=[unlock_renderer], tooltips=[('Month', '@x{int}'), ('unlockcharactermanager', '@top{1.11}')], formatters={'@x': 'numeral'})

bar_plot.add_tools(tool_premium, tool_unlock)
bar_plot.legend.click_policy = "hide"

# Daily crashes and ratings correlation
directory = "assignment1_data"
dfs_rating, dfs_crashes = [], []
for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if filename.startswith("stats_ratings_") and filename.endswith("_overview.csv"):
        dfs_rating.append(pd.read_csv(filepath, encoding='UTF-16'))
    elif filename.startswith("stats_crashes_") and filename.endswith("_overview.csv"):
        dfs_crashes.append(pd.read_csv(filepath, encoding='UTF-16'))

merged_rating = pd.concat(dfs_rating, ignore_index=True)
merged_rating['Daily Average Rating'].fillna(merged_rating['Total Average Rating'], inplace=True)
merged_crash = pd.concat(dfs_crashes, ignore_index=True)

merged_df = pd.merge(
    merged_crash.drop(['Package Name'], axis=1),
    merged_rating.drop(['Package Name'], axis=1),
    on='Date',
    how='inner'
)
merged_df['Date'] = pd.to_datetime(merged_df['Date'])
merged_df['Crashes'] = merged_df['Daily Crashes'] + merged_df['Daily ANRs']
merged_df.drop(['Daily Crashes', 'Daily ANRs'], axis=1, inplace=True)

dates = merged_df['Date'].tolist()
crashes = merged_df['Crashes'].tolist()
ratings = merged_df['Daily Average Rating'].tolist()

scatter_plot = figure(
    width=800, height=600, x_axis_type="datetime", x_axis_label='Date',
    tools="pan,save,reset", title='Correlation between Daily Crashes and User Ratings'
)
scatter_plot.background_fill_color = "#fafafa"

crashes_renderer = scatter_plot.scatter(dates, crashes, color='#de2d26', size=7, legend_label='Crashes')
scatter_plot.yaxis.axis_label = "Crashes"
scatter_plot.yaxis.axis_label_text_color = "#de2d26"

scatter_plot.extra_y_ranges['foo'] = Range1d(-0.1, 5.2)
ratings_renderer = scatter_plot.scatter(dates, ratings, color='blue', size=6, y_range_name="foo", legend_label='Rating')

scatter_plot.add_layout(LinearAxis(axis_label="Rating", y_range_name="foo", axis_label_text_color='blue'), 'right')

scatter_plot.add_tools(WheelZoomTool())
scatter_plot.toolbar.active_scroll = 'auto'

hover_crashes = HoverTool(renderers=[crashes_renderer], tooltips=[("Date", "@x{%F}"), ("Crashes", "@y")],
                          formatters={'@x': 'datetime'})
hover_ratings = HoverTool(renderers=[ratings_renderer], tooltips=[("Date", "@x{%F}"),
                                                                  ("Daily Average Rating", "@y{0.0}")], formatters={'@x': 'datetime'})

scatter_plot.add_tools(hover_crashes, hover_ratings)
scatter_plot.legend.location = 'bottom_right'
scatter_plot.legend.click_policy = "hide"

# Pie chart of transaction amounts by country
df_c = pd.read_csv(file_path)
country_transaction = df_c.groupby('Buyer Country')['Amount'].sum().reset_index()
country_transaction_sorted = country_transaction.sort_values(by='Amount', ascending=False)

top_9 = country_transaction_sorted.head(9)
others = pd.DataFrame({'Buyer Country': ['Others'], 'Amount': [country_transaction_sorted['Amount'][9:].sum()]})
result_dataframe = pd.concat([top_9, others])

data = pd.DataFrame(result_dataframe).reset_index(drop=True)
data['angle'] = data['Amount'] / data['Amount'].sum() * 2 * pi
data['color'] = Category20[len(result_dataframe)]

hover = HoverTool(tooltips=[("Country", "@{Buyer Country}"), ("Amount", "@Amount{1,11}")])

pie_chart = figure(
    height=400, title="Percentage of Transaction Amounts by Country",
    toolbar_location=None, tools=[hover], x_range=(-0.5, 1.0)
)
pie_chart.wedge(
    x=0, y=1, radius=0.4, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
    line_color="white", fill_color='color', legend_field='Buyer Country', source=data
)
pie_chart.axis.axis_label = None
pie_chart.axis.visible = False
pie_chart.grid.grid_line_color = None

# Combine all plots
all_grid = gridplot([[line_plot, pie_chart], [scatter_plot, bar_plot]])
output_file('all_plots.html')
save(all_grid)
