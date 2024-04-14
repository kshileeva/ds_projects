from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from sklearn_rand_forest import df_all, df_train, clf, num_train
from sklearn.ensemble import RandomForestRegressor, BaggingRegressor

nlp = spacy.load('en_core_web_md')

# Example: Using TF-IDF for text similarity
tfidf_vectorizer = TfidfVectorizer()

# Transform text data into TF-IDF vectors
tfidf_matrix_query = tfidf_vectorizer.fit_transform(df_all['search_term'])
tfidf_matrix_title = tfidf_vectorizer.transform(df_all['product_title'])
tfidf_matrix_desc = tfidf_vectorizer.transform(df_all['product_description'])

# Compute cosine similarity between query and product title/description
similarity_title = (tfidf_matrix_query * tfidf_matrix_title.T).toarray()
similarity_desc = (tfidf_matrix_query * tfidf_matrix_desc.T).toarray()

# Add similarity scores as features
df_all['similarity_title'] = similarity_title.diagonal()
df_all['similarity_desc'] = similarity_desc.diagonal()

# Example: Using spaCy for semantic similarity
def calculate_semantic_similarity(query, text):
    query_doc = nlp(query)
    text_doc = nlp(text)
    return query_doc.similarity(text_doc)

# Calculate semantic similarity between query and product title/description
df_all['semantic_similarity_title'] = df_all.apply(lambda row: calculate_semantic_similarity(row['search_term'], row['product_title']), axis=1)
df_all['semantic_similarity_desc'] = df_all.apply(lambda row: calculate_semantic_similarity(row['search_term'], row['product_description']), axis=1)

# Define feature set for training
feature_cols = ['len_of_query', 'word_in_title', 'word_in_description', 'similarity_title', 'similarity_desc', 'semantic_similarity_title', 'semantic_similarity_desc']

# Split data into train and test sets
X_train = df_all.iloc[:num_train][feature_cols]
X_test = df_all.iloc[num_train:][feature_cols]
y_train = df_train['relevance'].values

# Train your model (e.g., RandomForestRegressor) and evaluate
# Add other features and evaluate their impact on model performance

X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X_train, y_train, test_size=0.2, random_state=0)
clf.fit(X_train_split, y_train_split)
rf = RandomForestRegressor(n_estimators=15, max_depth=6, random_state=0)
clf = BaggingRegressor(rf, n_estimators=45, max_samples=0.1, random_state=25)
clf.fit(X_train_split, y_train_split)
y_pred_split = clf.predict(X_test_split)
rmse = np.sqrt(mean_squared_error(y_test_split, y_pred_split))
print(rmse)
