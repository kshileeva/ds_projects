import pandas as pd
import xgboost as xgb
from nltk import SnowballStemmer
import re
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import time

start = time.time()

df_train = pd.read_csv('depot_data/train.csv', encoding="ISO-8859-1")
df_attributes = pd.read_csv('depot_data/attributes.csv')
df_test = pd.read_csv('depot_data/test.csv', encoding="ISO-8859-1")
df_pro_desc = pd.read_csv('depot_data/product_descriptions.csv')

num_train = df_train.shape[0]

stemmer = SnowballStemmer('english')


def str_stemmer(s):
    return " ".join([stemmer.stem(word) for word in s.lower().split()])


def str_common_word(str1, str2):
    return sum(int(str2.find(word) >= 0) for word in str1.split())


def extract_numbers_and_units(text: str) -> dict:
    units = ['ft', 'in', 'mm', 'cm', 'm']
    numbers = re.findall(r'\d*\.?\d+', text)
    extracted_units = [unit for unit in units if unit in text]
    return {
        'numbers': set(str(num) for num in numbers),
        'units': set(extracted_units)
    }


def count_common_values(str1: str, str2: str) -> float:
    if isinstance(str1, str) and isinstance(str2, str):
        data1 = extract_numbers_and_units(str1)
        data2 = extract_numbers_and_units(str2)
        common_numbers = data1['numbers'].intersection(data2['numbers'])
        common_units = data1['units'].intersection(data2['units'])
        num_common_values = len(common_numbers) + len(common_units)
        return num_common_values
    else:
        return 0


df_all = pd.concat((df_train, df_test), axis=0, ignore_index=True)
df_all = pd.merge(df_all, df_pro_desc, how='left', on='product_uid')

df_all['search_term'] = df_all['search_term'].map(lambda x: str_stemmer(x))
df_all['product_title'] = df_all['product_title'].map(lambda x: str_stemmer(x))
df_all['product_description'] = df_all['product_description'].map(lambda x: str_stemmer(x))

df_all['len_of_query'] = df_all['search_term'].map(lambda x: len(x.split())).astype(np.int64)
df_all['product_info'] = df_all['search_term'] + "\t" + df_all['product_title'] + "\t" + df_all['product_description']
df_all['word_in_title'] = df_all['product_info'].map(lambda x: str_common_word(x.split('\t')[0], x.split('\t')[1]))
df_all['word_in_description'] = df_all['product_info'].map(lambda x: str_common_word(x.split('\t')[0], x.split('\t')[2]))

df_attributes['value'] = df_attributes['value'].astype(str).map(lambda x: x.lower())
df_all = pd.merge(df_all, df_attributes, on='product_uid', how='left')

df_all['num_info'] = df_all['search_term'] + "\t" + df_all['value']


def apply_count_common_values(row):
    split_row = str(row).split('\t')
    if len(split_row) >= 2:
        return count_common_values(split_row[0], split_row[1])
    else:
        return 0


df_all['value_numbers_units'] = df_all['num_info'].apply(apply_count_common_values)

df_all = df_all.drop(['search_term', 'product_title', 'product_description', 'product_info', 'value', 'num_info', 'name'], axis=1)

df_train = df_all.iloc[:num_train]
df_test = df_all.iloc[num_train:]
id_test = df_test['id']
y_train = df_train['relevance'].values
X_train = df_train.drop(['id', 'relevance'], axis=1).values
X_test = df_test.drop(['id', 'relevance'], axis=1).values


X_train_xgb, X_test_xgb, y_train_xgb, y_test_xgb = train_test_split(X_train, y_train, test_size=0.2, random_state=0)
xg_reg = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=25, max_depth=5, learning_rate=0.1, random_state=0)

xg_reg.fit(X_train_xgb, y_train_xgb)
y_pred_xgb = xg_reg.predict(X_test_xgb)
rmse_xgb = np.sqrt(mean_squared_error(y_test_xgb, y_pred_xgb))

end = time.time()

print(f'RMSE: {rmse_xgb}')
print(f'Time: {(end - start)} sec')
