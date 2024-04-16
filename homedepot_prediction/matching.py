import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

df_train = pd.read_csv('depot_data/train.csv', encoding="ISO-8859-1")
df_test = pd.read_csv('depot_data/test.csv', encoding="ISO-8859-1")
df_attr = pd.read_csv('depot_data/attributes.csv')
df_pro_desc = pd.read_csv('depot_data/product_descriptions.csv')

# Merge relevant data
df_attr = pd.merge(df_attr, df_pro_desc, how='left', on='product_uid')
df_all = pd.concat([df_train, df_test], axis=0, ignore_index=True)
df_all = pd.merge(df_all, df_attr, how='left', on='product_uid')

# Create a single TF-IDF vectorizer
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df_all['search_term'] + " " + df_all['product_title'])  # Combine search_term and product_title

# Calculate Cosine Similarity
cosine_similarity_matrix = cosine_similarity(tfidf_matrix)
df_all['cosine_similarity'] = cosine_similarity_matrix.diagonal()

# Prepare data for training
df_train = df_all[df_all['relevance'].notnull()]
X = df_train[['cosine_similarity']].values
y = df_train['relevance'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

rf = RandomForestRegressor(n_estimators=25, random_state=0)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"RMSE: {rmse}")