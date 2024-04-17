import pandas as pd
from nltk import WordNetLemmatizer, word_tokenize, pos_tag
import nltk
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
nltk.download('stopwords')
stop_words = set(nltk.corpus.stopwords.words('english'))
df_train = pd.read_csv('depot_data/train.csv', encoding="ISO-8859-1")
df_test = pd.read_csv('depot_data/test.csv', encoding="ISO-8859-1")
df_attr = pd.read_csv('depot_data/attributes.csv')
df_pro_desc = pd.read_csv('depot_data/product_descriptions.csv')

df_attr = pd.merge(df_attr, df_pro_desc, how='left', on='product_uid')
df_all = pd.concat([df_train, df_test], axis=0, ignore_index=True)
df_all = pd.merge(df_all, df_attr, how='left', on='product_uid')

def lemmatize_text(text):
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text.lower())
    tagged_tokens = pos_tag(tokens)
    lemmatized_tokens = []
    for token, tag in tagged_tokens:
        if token not in stop_words and (tag.startswith('N') or tag.startswith('J')):
            lemmatized_tokens.append(lemmatizer.lemmatize(token, pos=get_wordnet_pos(tag)))
        else:
            lemmatized_tokens.append(token)
    return lemmatized_tokens

# Function to get WordNet POS tag from Penn Treebank POS tag
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return 'a'  # Adjective
    elif treebank_tag.startswith('N'):
        return 'n'  # Noun
    else:
        return None

# Apply lemmatization to relevant columns
text_columns = ['value', 'product_description']
for col in text_columns:
    df_all[col + '_lemmatized'] = df_all[col].apply(lambda x: lemmatize_text(str(x)))

# Extract nouns and adjectives from lemmatized text
nlp = spacy.load('en_core_web_sm')

def extract_nouns_adjectives(tokens):
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc if token.pos_ in {'NOUN', 'ADJ'}]

# Apply extraction to relevant columns
for col in text_columns:
    df_all[col + '_nouns_adjectives'] = df_all[col + '_lemmatized'].apply(extract_nouns_adjectives)

# Function to calculate matching based on nouns and adjectives
def calculate_matching(row):
    search_terms = set(row['search_term_nouns_adjectives'])
    attribute_terms = set(row['value_nouns_adjectives'])
    return len(search_terms.intersection(attribute_terms)) / len(search_terms.union(attribute_terms))

# Apply matching calculation
df_all['matching_score'] = df_all.apply(calculate_matching, axis=1)

# Display resulting DataFrame with new features
print(df_all.head())
# df_train = df_all[df_all['relevance'].notnull()]
# X = df_train[['cosine_similarity']].values
# y = df_train['relevance'].values
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
#
# rf = RandomForestRegressor(n_estimators=25, random_state=0)
# rf.fit(X_train, y_train)
#
# y_pred = rf.predict(X_test)
# rmse = np.sqrt(mean_squared_error(y_test, y_pred))
# print(f"RMSE: {rmse}")