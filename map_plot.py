import os
import pandas as pd
import plotly.express as px
import country_converter as coco

def assembling_data(directory="assignment1_data"):
    countries = []
    sales = []
    for filename in os.listdir(directory):
        if filename.startswith("stats_ratings_") and filename.endswith("_country.csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath, encoding='UTF-16')
            countries.append(df)
    merged_country = pd.concat(countries, ignore_index=True)
    for filename in os.listdir(directory):
        if filename.startswith("sales_"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            sales.append(df)
    merged_sales = pd.concat(sales, ignore_index=True)
    return merged_country, merged_sales


def dropping_columns(data, cols: list):
    return data[cols]


def drop() -> tuple:
    merged_country, merged_sales = assembling_data()
    columns_sales = ['Transaction Date', 'Buyer Country', 'Amount (Merchant Currency)']
    columns_country = ['Country', 'Total Average Rating', 'Date', 'Daily Average Rating']
    dropped_sales = dropping_columns(merged_sales, columns_sales)
    dropped_country = dropping_columns(merged_country, columns_country)
    return dropped_country, dropped_sales


countries, sales = drop()


def sum_of_sales(df: pd.DataFrame = sales) -> pd.DataFrame:
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    df['Week'] = df['Transaction Date'].dt.isocalendar().week
    res = df.groupby(['Buyer Country', 'Week'])['Amount (Merchant Currency)'].sum().reset_index()
    return res


def calculate_weekly_average(df: pd.DataFrame = countries) -> pd.DataFrame:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')
    df['Daily Average Rating'].fillna(df['Total Average Rating'], inplace=True)
    df['Week'] = df['Date'].dt.isocalendar().week
    res = df.groupby(['Country', 'Week']).agg({'Daily Average Rating': 'mean'}).reset_index()
    return res


def converting_countrycode(df: pd.DataFrame) -> pd.DataFrame:
    if 'Country' in df.columns:
        df = df.rename(columns={'Country': 'country_code'})
    elif 'Buyer Country' in df.columns:
        df = df.rename(columns={'Buyer Country': 'country_code'})
    iso2_values = df['country_code']
    conv_df = coco.convert(names=iso2_values, to='ISO3', not_found=None)
    df['country_code'] = conv_df
    return df


sale = sum_of_sales(sales)
country = calculate_weekly_average(countries)
conv_sale = converting_countrycode(sale)
conv_country = converting_countrycode(country)

def plot_map(data1, data2):
    fig1 = px.choropleth(data1, locations='country_code', color='Daily Average Rating', hover_name='country_code',
                        projection='natural earth', animation_frame='Week',
                        title='Country Rating')
    fig1.write_html("plot_map.html")
    fig1.show()

plot_map(conv_country, conv_sale)









# def geodata_country(shapefile='ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp'):
#     gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#     gdf.columns = ['country', 'country_code', 'geometry']
#     ratings_df = countries.rename(columns={'Country': 'country_code'})
#     iso2_values = ratings_df['country_code']
#     ratings_conv = coco.convert(names=iso2_values, to='ISO3', not_found=None)
#     ratings_df['country_code'] = ratings_conv
#     gdf = gdf.merge(ratings_df, on='country_code', how='left')
#     gdf = gdf[gdf['country_code'] != 'ATA']
#     return gdf
#
#
# def get_geodatasource(gdf):
#     import json
#     json_data = json.dumps(json.loads(gdf.to_json()))
#     return GeoJSONDataSource(geojson=json_data)
#
#
# def plot_map(gdf, title=''):
#     p = figure(title=title, height=500, width=950)
#     hover = HoverTool(
#         tooltips=[("Country", "@country"), ("Rating", "@{Total Average Rating}")],
#         formatters={'Date': 'datetime'})
#     p.add_tools(hover)
#     reset_data_button = Button(label="Reset map", background='black', width=110)
#     slider = Slider(start=1, end=24, value=24, step=1, title="Week", width=110)
#     palette = ['#008000', '#FFC500', '#ff0000', '#c70000']
#     color_mapper = LinearColorMapper(palette=palette, low=0, high=4, nan_color='#838383')
#     tick_labels = {'4': '>4'}
#     color_bar = ColorBar(color_mapper=color_mapper, label_standoff=6, width=500, height=20,
#                          border_line_color=None, location=(0, 0), major_label_overrides=tick_labels,
#                          title='Rating')
#     geosource = get_geodatasource(gdf)
#     p.patches('xs', 'ys', source=geosource, line_color='black', line_width=0.5, fill_alpha=1)
#     p.background_fill_color = "beige"
#     p.background_fill_alpha = 0.2
#     callback = CustomJS(args=dict(source=geosource), code="""
#         var data = source.data;
#         var week = cb_obj.value;
#         var indices = [];
#         for (var i = 0; i < data['week'].length; i++) {
#             if (data['week'][i] == week) {
#                 indices.push(i);
#             }
#         }
#         source.selected.indices = indices;
#         source.change.emit();
#     """)
#
#     slider.js_on_change('value', callback)
#     from bokeh.layouts import column
#     layout = column(p, slider)
#
#     output_file('world_map.html')
#     show(layout)
#
#
# plot_map(geodata_country(), title='Weekly Average Rating per Country')