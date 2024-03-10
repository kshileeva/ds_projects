import geopandas as gpd
from bokeh.plotting import figure, output_file, show
from bokeh.models import GeoJSONDataSource, HoverTool
import pandas as pd

shapefile = 'ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp'
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']

ratings_data = {
    'Country_Code': ['US', 'IT', 'GB', 'DE', 'FR'],
    'Rating': [4.2, 3.5, 4.0, 4.8, 3.9]
}
ratings_df = pd.DataFrame(ratings_data)

# Rename the column to match the geopandas dataframe
ratings_df.rename(columns={'Country_Code': 'country_code'}, inplace=True)

# Merge the ratings data with the geopandas dataframe
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
