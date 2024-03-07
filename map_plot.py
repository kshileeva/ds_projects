import pandas as pd
import geopandas as gpd
import os
from bokeh.plotting import figure, show


def assembling_data(directory="assignment1_data"):
    country = []
    sales = []
    for filename in os.listdir(directory):
        if filename.startswith("stats_ratings_") and filename.endswith("_country.csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath, encoding='UTF-16')
            country.append(df)
    merged_country = pd.concat(country, ignore_index=True)
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


c, s = merging()
print(c)