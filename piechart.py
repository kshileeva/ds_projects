from math import pi
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.palettes import Category20
from bokeh.transform import cumsum
import pandas as pd

# The figure will be rendered inline in my Jupyter Notebook
output_file('analysis3.html', title="a3")

# read file into Dataframe
file_path = 'combined_sales_file.csv'
df_table = pd.read_csv(file_path)

# change the date form
df = pd.DataFrame(df_table)

# groupby the transaction by country and sort it by descending order
country_transaction = df.groupby('Buyer Country')['Amount'].sum().reset_index()
country_transaction_sorted = country_transaction.sort_values(by='Amount', ascending=False)

# keep the first 9 rows, sum up the remaining rows and create a new row named 'others'
top_9 = country_transaction_sorted.head(9)
others = pd.DataFrame({'Buyer Country':['Others'],
                       'Amount': [country_transaction_sorted['Amount'][9:].sum()]
                           })
result_dataframe = pd.concat([top_9, others])

data = pd.DataFrame(result_dataframe).reset_index(drop=True)
data['angle'] = data['Amount']/data['Amount'].sum() * 2*pi
data['color'] = Category20[len(result_dataframe)]

hover = HoverTool(
    tooltips=[("Country", "@{Buyer Country}"),
              ("Amount", "@Amount{1,11}")])

c = figure(height=350, title="Pie Chart", toolbar_location=None,
           tools=[hover], x_range=(-0.5, 1.0))


c.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='Buyer Country', source=data)

c.axis.axis_label = None
c.axis.visible = False
c.grid.grid_line_color = None