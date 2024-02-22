import pandas as pd
import os
folder_path = 'assignment1_data'
all_files = os.listdir(folder_path)
csv_files = [f for f in all_files if f.endswith('.csv')]

df_list = []

for csv in csv_files:
    file_path = os.path.join(folder_path, csv)
    try:
        df = pd.read_csv(file_path)
        df_list.append(df)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-16')
            df_list.append(df)
        except Exception as e:
            print(f"Could not read file {csv} because of error: {e}")
    except Exception as e:
        print(f"Could not read file {csv} because of error: {e}")

big_df = pd.concat(df_list, ignore_index=True)

big_df.to_csv(os.path.join(folder_path, 'combined_file.csv'), index=False)
print(pd.read_csv(big_df))