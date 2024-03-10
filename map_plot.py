import os
import geopandas as gpd
from bokeh.plotting import figure, output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool
import pandas as pd


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


shapefile = 'ne_110m_admin_0_countries_lakes.shp'
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']

ratings_data = {
    'Country_Code': ['US', 'IT', 'GB', 'DE', 'FR'],
    'Rating': [4.2, 3.5, 4.0, 4.8, 3.9]
}
ratings_df = pd.DataFrame(ratings_data)

ratings_df.rename(columns={'Country_Code': 'country_code'}, inplace=True)

gdf = gdf.merge(ratings_df, on='country_code', how='left')


def get_geodatasource(gdf):
    import json
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson=json_data)


def plot_map(gdf, title=''):
    p = figure(title=title, height=600, width=1000)
    geosource = get_geodatasource(gdf)
    p.patches('xs', 'ys', source=geosource, line_color='black', line_width=0.5, fill_alpha=1)

    # Use the 'Rating' column directly from the GeoDataFrame
    hover = HoverTool(tooltips=[("Country", "@country"), ("Rating", "@Rating")])
    p.add_tools(hover)

    output_file('world_map.html')
    show(p)


plot_map(gdf, title='World Map')
