from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import HoverTool
import pandas as pd

output_file('analysis2.html', title='a2')
file_path = 'combined_sales_file.csv'
df_table = pd.read_csv(file_path)
monthly_sku_amount = pd.DataFrame(columns=['month', 'premium', 'unlockcharactermanager'])
df = pd.DataFrame(df_table)
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

p = figure(width=550,
           height=600,
           title='Transaction Amounts by SKU ID',
           x_axis_label='Month',
           y_axis_label='Transaction Amount')

pre_renderer = p.vbar(x=monthly_sku_amount['month'], top=monthly_sku_amount['premium'], width=0.3, color='orange',
                      legend_label='premium')

unlock_renderer = p.vbar(x=monthly_sku_amount['month']+0.3, top=monthly_sku_amount['unlockcharactermanager'],
                         width=0.3, color='blue', legend_label='unlockcharactermanager')

hover_pre = [('Month', '@x{int}'), ('premium', "@top{1.11}")]
tool_pre = HoverTool(renderers=[pre_renderer], tooltips=hover_pre, formatters={'@x': 'numeral', '@y': 'printf'})

hover_unlock = [('Month', '@x{int}'), ('unlockcharactermanager', '@top{1.11}')]
tool_unlock = HoverTool(renderers=[unlock_renderer], tooltips=hover_unlock, formatters={'@x': 'numeral'})

p.add_tools(tool_pre, tool_unlock)
p.legend.click_policy = "hide"
show(p)
print(monthly_sku_amount)