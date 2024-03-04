import os
import pandas as pd
directory = "assignment1_data"

dfs = []

for filename in os.listdir(directory):
    if filename.startswith("stats_ratings_") and filename.endswith("_overview.csv"):
        filepath = os.path.join(directory, filename)
        df = pd.read_csv(filepath, encoding='UTF-16')
        dfs.append(df)

print(df)


