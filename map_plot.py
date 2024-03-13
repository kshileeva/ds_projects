import os
import pandas as pd
import plotly.express as px
import country_converter as coco
import plotly.graph_objects as go


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
    df = df.sort_values(by='Transaction Date')
    df['Week'] = df['Transaction Date'].dt.isocalendar().week
    res = df.groupby(['Buyer Country', 'Week'])['Amount (Merchant Currency)'].sum().reset_index()
    idx = pd.MultiIndex.from_product([res['Buyer Country'].unique(), range(22, 53)],
                                     names=['Buyer Country', 'Week'])
    res = res.set_index(['Buyer Country', 'Week']).reindex(idx, fill_value=0).reset_index()
    res.columns = ['Country', 'Week', 'Amount(EUR)']
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
    iso2_values = df['country_code']
    conv_df = coco.convert(names=iso2_values, to='ISO3', not_found=None)
    df['country_code'] = conv_df
    return df


sale = sum_of_sales(sales)
country = calculate_weekly_average(countries)
conv_sale = converting_countrycode(sale)
conv_country = converting_countrycode(country)


def plot_map_combined(data1, data2):
    fig1 = px.choropleth(data1, locations='country_code', color='Daily Average Rating', hover_name='country_code',
                         projection='natural earth', animation_frame='Week',
                         title='Country Rating per Week')
    fig2 = px.choropleth(data2, locations='country_code', color='Amount(EUR)', hover_name='country_code',
                         projection='natural earth', animation_frame='Week',
                         title='Weekly Sales')

    fig1.update_geos(showcountries=True)
    fig2.update_geos(showcountries=True)

    fig1.update_layout(height=600, width=800, title_text='Country Rating and Weekly Sales')
    fig2.update_layout(height=600, width=800)

    fig1.write_html("plot_map_combined.html")
    fig2.write_html("plot_map_combined.html")
    fig = fluidPage()
    fig = go.Figure(fig1['data'] + fig2['data'], layout=row(fig1.layout, fig2))

    fig.show()


plot_map_combined(conv_country, conv_sale)
