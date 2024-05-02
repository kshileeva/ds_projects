import numpy as np
import pandas as pd
import xgboost as xgb
import time
from nltk import SnowballStemmer
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingRandomSearchCV

start = time.time()

df_train = pd.read_csv('depot_data/train.csv', encoding="ISO-8859-1")
df_test = pd.read_csv('depot_data/test.csv', encoding="ISO-8859-1")
df_pro_desc = pd.read_csv('depot_data/product_descriptions.csv')
stemmer = SnowballStemmer('english')

num_train = df_train.shape[0]

def str_stemmer(s):
    return " ".join([stemmer.stem(word) for word in s.lower().split()])

def str_common_word(str1, str2):
    return sum(int(str2.find(word) >= 0) for word in str1.split())

df_all = pd.concat((df_train, df_test), axis=0, ignore_index=True)
df_all = pd.merge(df_all, df_pro_desc, how='left', on='product_uid')
df_all['search_term'] = df_all['search_term'].map(lambda x: str_stemmer(x))
df_all['product_title'] = df_all['product_title'].map(lambda x: str_stemmer(x))
df_all['product_description'] = df_all['product_description'].map(lambda x: str_stemmer(x))
df_all['len_of_query'] = df_all['search_term'].map(lambda x: len(x.split())).astype(np.int64)

df_train = df_all.iloc[:num_train]
df_test = df_all.iloc[num_train:]
y_train = df_train['relevance'].values
X_train = df_train.drop(['id', 'relevance'], axis=1).values
X_test = df_test.drop(['id', 'relevance'], axis=1).values

X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(X_train, y_train, test_size=0.2, random_state=0)

param_dist = {
    'n_estimators': np.arange(50, 300, 50),
    'max_depth': np.arange(3, 10),
    'learning_rate': [0.01, 0.05, 0.1, 0.3],
    'gamma': [0, 0.1, 0.2, 0.3],
    'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1.0]
}

halving_search = HalvingRandomSearchCV(
    estimator=xgb.XGBRegressor(objective='reg:squarederror', random_state=0),
    param_distributions=param_dist,
    factor=3,
    cv=5,
    scoring='neg_mean_squared_error',
    random_state=0,
    n_jobs=-1  # use all available cores
)

halving_search.fit(X_train_split, y_train_split)

best_estimator = halving_search.best_estimator_
y_pred_val = best_estimator.predict(X_val_split)
rmse_val = np.sqrt(mean_squared_error(y_val_split, y_pred_val))

end = time.time()

print("Best Estimator:", best_estimator)
print(f"Validation RMSE: {rmse_val:.4f}")
print(f"Time taken: {end - start:.2f} seconds")
