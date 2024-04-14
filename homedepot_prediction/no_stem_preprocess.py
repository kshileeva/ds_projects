import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, BaggingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

df_train = pd.read_csv('depot_data/train.csv', encoding="ISO-8859-1")
df_test = pd.read_csv('depot_data/test.csv', encoding="ISO-8859-1")
# df_attr = pd.read_csv('depot_data/attributes.csv')
df_pro_desc = pd.read_csv('depot_data/product_descriptions.csv')

num_train = df_train.shape[0]


def str_common_word(str1, str2):
    return sum(int(str2.find(word) >= 0) for word in str1.split())


df_all_ns = pd.concat((df_train, df_test), axis=0, ignore_index=True)

df_all_ns = pd.merge(df_all_ns, df_pro_desc, how='left', on='product_uid')

df_all_ns['search_term'] = df_all_ns['search_term'].map(lambda x: x.lower())
df_all_ns['product_title'] = df_all_ns['product_title'].map(lambda x: x.lower())
df_all_ns['product_description'] = df_all_ns['product_description'].map(lambda x: x.lower())

df_all_ns['len_of_query'] = df_all_ns['search_term'].map(lambda x: len(x.split())).astype(np.int64)

df_all_ns['product_info'] = df_all_ns['search_term'] + "\t" + df_all_ns['product_title'] + "\t" + df_all_ns['product_description']

df_all_ns['word_in_title'] = df_all_ns['product_info'].map(lambda x: str_common_word(x.split('\t')[0], x.split('\t')[1]))
df_all_ns['word_in_description'] = df_all_ns['product_info'].map(lambda x: str_common_word(x.split('\t')[0],
                                                                                           x.split('\t')[2]))

df_all_ns = df_all_ns.drop(['search_term', 'product_title', 'product_description', 'product_info'], axis=1)

df_train = df_all_ns.iloc[:num_train]
df_test = df_all_ns.iloc[num_train:]
id_test = df_test['id']

y_train_no_stem = df_train['relevance'].values
X_train_no_stem = df_train.drop(['id', 'relevance'], axis=1).values
X_test_no_stem = df_test.drop(['id', 'relevance'], axis=1).values

rf_no_stem = RandomForestRegressor(n_estimators=15, max_depth=6, random_state=0)
clf_no_stem = BaggingRegressor(rf_no_stem, n_estimators=45, max_samples=0.1, random_state=25)
X_train_split_ns, X_test_split_ns, y_train_split_ns, y_test_split_ns = train_test_split(X_train_no_stem, y_train_no_stem, test_size=0.2, random_state=0)
clf_no_stem.fit(X_train_split_ns, y_train_split_ns)

y_pred_split_ns = clf_no_stem.predict(X_test_split_ns)
rmse_no_stem = np.sqrt(mean_squared_error(y_test_split_ns, y_pred_split_ns))
# pd.DataFrame({"id": id_test, "relevance": y_pred}).to_csv('submission.csv', index=False)
print(rmse_no_stem)