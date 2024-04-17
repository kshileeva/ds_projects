import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, BaggingRegressor
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_squared_error
from nltk.stem import SnowballStemmer
import time

start = time.time()
df_train = pd.read_csv('depot_data/train.csv', encoding="ISO-8859-1")
df_test = pd.read_csv('depot_data/test.csv', encoding="ISO-8859-1")
df_pro_desc = pd.read_csv('depot_data/product_descriptions.csv')

# Initialize stemmer
stemmer = SnowballStemmer('english')

# Function to perform stemming
def str_stemmer(s):
    return " ".join([stemmer.stem(word) for word in s.lower().split()])

# Apply stemming to text columns
df_train['search_term'] = df_train['search_term'].map(str_stemmer)
df_train['product_title'] = df_train['product_title'].map(str_stemmer)
df_pro_desc['product_description'] = df_pro_desc['product_description'].map(str_stemmer)

# Merge datasets
df_all = pd.concat([df_train, df_test], axis=0, ignore_index=True)
df_all = pd.merge(df_all, df_pro_desc, how='left', on='product_uid')

tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, stop_words='english')

tfidf_matrix_search_term = tfidf.fit_transform(df_all['search_term'])
tfidf_matrix_product_title = tfidf.fit_transform(df_all['product_title'])
tfidf_matrix_product_description = tfidf.fit_transform(df_all['product_description'])

X_tfidf = np.hstack([tfidf_matrix_search_term.toarray(),
                     tfidf_matrix_product_title.toarray(),
                     tfidf_matrix_product_description.toarray()])

X_train_tfidf = X_tfidf[:df_train.shape[0]]
X_test_tfidf = X_tfidf[df_train.shape[0]:]

y_train = df_train['relevance'].values

X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X_train_tfidf, y_train, test_size=0.2, random_state=0)

rf = RandomForestRegressor(n_estimators=15, max_depth=6, random_state=0)
clf = BaggingRegressor(rf, n_estimators=45, max_samples=0.1, random_state=25)
clf.fit(X_train_split, y_train_split)

y_pred_split = clf.predict(X_test_split)

# Calculate RMSE
rmse = np.sqrt(mean_squared_error(y_test_split, y_pred_split))

end = time.time()

print("RMSE:", rmse)
print("Time:", end - start)
