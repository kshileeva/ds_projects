import os
import pandas as pd
import plotly.express as px
import country_converter as coco


def assembling_data(directory="assignment1_data") -> pd.DataFrame:
    countries = []
    for filename in os.listdir(directory):
        if filename.startswith("stats_ratings_") and filename.endswith("_country.csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath, encoding='UTF-16')
            countries.append(df)
    merged_country = pd.concat(countries, ignore_index=True)
    return merged_country


def dropping_columns(data, cols: list):
    return data[cols]


def drop(country: pd.DataFrame) -> pd.DataFrame:
    columns_country = ['Country', 'Total Average Rating', 'Date', 'Daily Average Rating']
    dropped_country = dropping_columns(country, columns_country)
    return dropped_country


def calculate_weekly_average(df: pd.DataFrame) -> pd.DataFrame:
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
    short_names = coco.convert(names=iso2_values, to='name_short', not_found=None)
    df['short_name'] = short_names
    conv_df = coco.convert(names=iso2_values, to='ISO3', not_found=None)
    df['ISO3'] = conv_df
    return df


merged_country = assembling_data()
merged_country = drop(merged_country)
weekly_average = calculate_weekly_average(merged_country)
converted_country = converting_countrycode(weekly_average)


def plot_map(data):
    fig = px.choropleth(data, locations='ISO3', color='Daily Average Rating', hover_name='short_name',
                        projection='natural earth', animation_frame='Week', title='App Rating by Countries per Week',
                        color_continuous_scale='RdYlGn')
    fig.write_html("plot_map.html")
    fig.show()


plot_map(converted_country)
