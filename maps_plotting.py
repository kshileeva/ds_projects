import os
import geopandas as gpd
from bokeh.layouts import row, column
from bokeh.plotting import figure, output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool, Slider, CustomJS
import pandas as pd
import country_converter as coco


def assembling_data(directory="assignment1_data") -> tuple:
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


def dropping_columns(data, cols: list) -> pd.DataFrame:
    return data[cols]


def drop() -> tuple:
    merged_country, merged_sales = assembling_data()
    columns_sales = ['Transaction Date', 'Buyer Country', 'Amount (Merchant Currency)']
    columns_country = ['Country', 'Total Average Rating', 'Date', 'Daily Average Rating']
    dropped_sales = dropping_columns(merged_sales, columns_sales)
    dropped_country = dropping_columns(merged_country, columns_country)
    return dropped_country, dropped_sales


countries, sales = drop()


def calculate_weekly_average(df: pd.DataFrame = countries) -> pd.DataFrame:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')
    df['Daily Average Rating'].fillna(df['Total Average Rating'], inplace=True)
    df['Week'] = df['Date'].dt.isocalendar().week
    res = df.groupby(['Country', 'Week']).agg({'Daily Average Rating': 'mean'}).reset_index()
    return res


def sum_of_sales(df: pd.DataFrame = sales) -> pd.DataFrame:
    df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
    df['Week'] = df['Transaction Date'].dt.isocalendar().week
    res = df.groupby(['Buyer Country', 'Week'])['Amount (Merchant Currency)'].sum().reset_index()
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


code_country = converting_countrycode(calculate_weekly_average())
code_sale = converting_countrycode(sum_of_sales())


def geodata_country(data: pd.DataFrame,
                    shapefile='ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp'):
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns = ['country', 'country_code', 'geometry']
    gdf = gdf.merge(data, on='country_code', how='left')
    gdf = gdf[gdf['country_code'] != 'ATA']
    return gdf


def get_datasource(gdf):
    import json
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson=json_data)


def filter_weekly_data(df, selected_week):
    filtered_df = df.loc[df['Week'] == selected_week]
    return filtered_df


def plot_map():
    p1 = figure(title="Weekly Rating per Country", height=300, width=750)
    p2 = figure(title="Weekly Sales per Country", height=300, width=750)
    country_geo = geodata_country(code_country)
    sale_geo = geodata_country(code_sale)
    source_country = get_datasource(country_geo)
    source_sales = get_datasource(sale_geo)
    p1.patches('xs', 'ys', source=source_country, line_color='black', line_width=0.5, fill_alpha=1)
    p2.patches('xs', 'ys', source=source_sales, line_color='black', line_width=0.5, fill_alpha=1)
    hover1 = HoverTool(
        tooltips=[("Country", "@country"), ("Rating", "@{Daily Average Rating}{0,0.00}")],
        formatters={'Week': 'numeral'})
    p1.add_tools(hover1)
    hover2 = HoverTool(
        tooltips=[("Country", "@country"), ("Amount, EUR", "@{Amount (Merchant Currency)}{0,0.00}")],
        formatters={'Week': 'numeral'})
    p2.add_tools(hover2)
    slider = Slider(start=22, end=52, value=22, step=1, title="Week", width=110)

    def update_source_data(attr, old, new):
        selected_week = slider.value  # Assuming you have defined the slider widget
        new_data_country = filter_weekly_data(code_country, selected_week)
        new_data_sales = filter_weekly_data(code_sale, selected_week)
        source_country.geojson = get_datasource(geodata_country(new_data_country)).geojson
        source_sales.geojson = get_datasource(geodata_country(new_data_sales)).geojson

    slider.on_change('value', update_source_data)

    layout = column(row(p1, p2), slider)

    output_file('world_map.html')
    show(layout)


plot_map()

