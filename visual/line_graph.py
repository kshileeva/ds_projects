from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import LinearAxis, Range1d, HoverTool
import pandas as pd
output_file('../analysis1.html', title="a1")
file_path = '../combined_sales_file.csv'
df_table = pd.read_csv(file_path)
df = pd.DataFrame(df_table)
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format='mixed', errors='coerce')
df['month'] = df['Transaction Date'].dt.month
df_table['Amount'] = df_table['Amount'].astype(float)
monthly_data = df.groupby('month').agg({'Amount': 'sum', 'Description': 'count'}).reset_index()
months = monthly_data['month'].tolist()
amounts = monthly_data['Amount'].tolist()
volumes = monthly_data['Description'].tolist()
p = figure(width=600,
           height=400,
           title='Monthly Revenue and Transaction Volume Trends',
           x_axis_label='Month',
           y_axis_label='Transaction Amount'
           )

am_renderer = p.line(months, amounts, color='navy', line_width=2, legend_label='Transaction Amount')
vol_renderer = p.line(months, volumes, color='red', line_width=2, legend_label='Transaction Volume', y_range_name='volume_range')
hover_am = [
    ("Month", "@x{int}"),
    ("Transaction Amount", "@y{1.11}")
]
hover_vol = [
    ("Month", "@x{int}"),
    ("Transaction Volume", "@y")
]
p.hover.mode = 'vline'
p.extra_y_ranges = {'volume_range': Range1d(start=0, end=700)}
p.add_layout(LinearAxis(y_range_name='volume_range', axis_label='Transaction Volume'), 'right')

tool_am = HoverTool(renderers=[am_renderer], tooltips=hover_am, formatters={'@x': 'numeral'})
tool_vol = HoverTool(renderers=[vol_renderer], tooltips=hover_vol, formatters={'@x': 'numeral'})
p.legend.location = 'bottom_left'
p.legend.click_policy = "hide"
p.add_tools(tool_vol, tool_am)
show(p)
