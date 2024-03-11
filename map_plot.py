import os
import geopandas as gpd
from bokeh.plotting import figure, output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool, Slider, CustomJS
import pandas as pd
import country_converter as coco


def assembling_data(directory="assignment1_data", countries: list = [], sales: list = []):
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


def merging():
    merged_country, merged_sales = assembling_data()
    columns_sales = ['Transaction Date', 'Buyer Country', 'Amount (Merchant Currency)']
    columns_country = ['Country', 'Total Average Rating', 'Date']
    dropped_sales = dropping_columns(merged_sales, columns_sales)
    dropped_country = dropping_columns(merged_country, columns_country)
    pd.to_datetime(dropped_sales['Transaction Date'])
    pd.to_datetime(dropped_country['Date'])
    return dropped_country, dropped_sales


countries, sales = merging()


def sales_sum(df):
    grouped_df = df.groupby(['Transaction Date', 'Buyer Country'])['Amount (Merchant Currency)'].sum().reset_index()
    return grouped_df


sale = sales_sum(sales)


def geodata_country(shapefile='ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp'):
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country', 'country_code', 'geometry']
    ratings_df = countries.rename(columns={'Country': 'country_code'})
    iso2_values = ratings_df['country_code']
    ratings_conv = coco.convert(names=iso2_values, to='ISO3', not_found=None)
    ratings_df['country_code'] = ratings_conv
    gdf = gdf.merge(ratings_df, on='country_code', how='left')
    gdf = gdf[gdf['country_code'] != 'ATA']
    return gdf


def get_geodatasource(gdf):
    import json
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson=json_data)


def plot_map(gdf, title=''):
    p = figure(title=title, height=500, width=950)
    geosource = get_geodatasource(gdf)
    p.patches('xs', 'ys', source=geosource, line_color='black', line_width=0.5, fill_alpha=1)
    hover = HoverTool(
        tooltips=[("Country", "@country"), ("Rating", "@{Total Average Rating}")],
        formatters={'Date': 'datetime'})
    p.add_tools(hover)
    slider = Slider(start=1, end=24, value=24, step=1, title="Week", width=110)
    callback = CustomJS(args=dict(source=geosource), code="""
        var data = source.data;
        var week = cb_obj.value;
        var indices = [];
        for (var i = 0; i < data['week'].length; i++) {
            if (data['week'][i] == week) {
                indices.push(i);
            }
        }
        source.selected.indices = indices;
        source.change.emit();
    """)

    slider.js_on_change('value', callback)
    from bokeh.layouts import column
    layout = column(p, slider)

    output_file('world_map.html')
    show(layout)


plot_map(geodata_country(), title='World Map')