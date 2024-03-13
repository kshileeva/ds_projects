import os
import geopandas as gpd
from bokeh.layouts import row, column
from bokeh.plotting import figure, output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool, Slider, LinearColorMapper, ColorBar
import pandas as pd
import country_converter as coco
import panel as pn
import panel.widgets as pnw


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


def get_weekly_data(selected_week, df):
    filtered_df = df[df['Week'] == selected_week]
    geojson_data = filtered_df.to_json()
    geojson_data_source = GeoJSONDataSource(geojson=geojson_data)
    return geojson_data_source


def plot_map():
    palette = ['#8B4513', '#c70000', '#ff0000', '#FFA500', '#FFFF00', '#008000']
    ratings = [float('-inf'), 0, 1, 2, 3, 4, float('inf')]
    rating_labels = ['NaN', '0-1', '1-2', '2-3', '3-4', '4-5']
    p1 = figure(title="Weekly Rating per Country", height=300, width=750)
    p2 = figure(title="Weekly Sales per Country", height=300, width=750)
    country_geo = geodata_country(code_country)
    sale_geo = geodata_country(code_sale)
    source_country = get_datasource(country_geo)
    source_sales = get_datasource(sale_geo)
    color_mapper = LinearColorMapper(palette=palette, low=min(ratings), high=max(ratings), nan_color='#F5F5DC')
    p1.patches('xs', 'ys', source=source_country, line_color='black', line_width=0.5,
               fill_alpha=1, fill_color={'field': 'Daily Average Rating', 'transform': color_mapper})
    p2.patches('xs', 'ys', source=source_sales, line_color='black', line_width=0.5, fill_alpha=1)
    hover1 = HoverTool(
        tooltips=[("Country", "@country"), ("Rating", "@{Daily Average Rating}{0,0.00}")],
        formatters={'Week': 'numeral'})
    p1.add_tools(hover1)
    hover2 = HoverTool(
        tooltips=[("Country", "@country"), ("Amount, EUR", "@{Amount (Merchant Currency)}{0,0.00}")],
        formatters={'Week': 'numeral'})
    p2.add_tools(hover2)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=6, width=500, height=20,
                         border_line_color=None, location=(0, 0),
                         major_label_overrides=dict(zip(ratings, rating_labels)),
                         title='Rating')
    p1.add_layout(color_bar, 'below')

    def update_map1(attr, old, new):
        selected_week = slider.value
        new_country_source = get_weekly_data(selected_week, source_country)
        return new_country_source

    def update_map2(attr, old, new):
        selected_week = slider.value
        new_sales_source = get_weekly_data(selected_week, source_sales)
        return new_sales_source

    slider = Slider(start=22, end=52, value=22, step=1, title="Week", width=200)
    slider.on_change('value', update_map1)
    slider.on_change('value', update_map2)
    layout = column(row(p1, p2), slider)

    output_file('world_map.html')
    show(layout)

plot_map()
