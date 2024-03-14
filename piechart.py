from math import pi
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
from bokeh.models import HoverTool
import random
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
print(result_dataframe)

# Define a function to generate a random color
def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

# convert data to angle
result_dataframe['angle']=result_dataframe['Amount']/sum(result_dataframe['Amount'])*2*pi
result_dataframe['color']= [random_color() for _ in range(len(result_dataframe))]


# use piechart to visualize
p = figure(height=350,
           title="Top 10 Buyer Country",
           toolbar_location=None,
           tools="hover",
           )

p.annular_wedge(x=0,
        y=1,
        outer_radius=0.4,
        inner_radius=0.2,
        start_angle=cumsum('angle', include_zero=True),
        end_angle=cumsum('angle'),
        line_color="white",
        fill_color='color',
        legend_field='Buyer Country',
        source=result_dataframe)

hover = HoverTool(tooltips=[("Country", "@{Buyer Country}"), ("Amount", "@Amount")])
p.add_tools(hover)

# add legend
p.legend.title = 'Buyer Country'

p.legend.click_policy = "mute"
p.axis.axis_label = None
p.axis.visible = False
p.grid.grid_line_color = None

show(p)