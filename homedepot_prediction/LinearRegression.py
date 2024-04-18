from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

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

df_all['product_info'] = df_all['search_term']+"\t"+df_all['product_title']+"\t"+df_all['product_description']

df_all['word_in_title'] = df_all['product_info'].map(lambda x: str_common_word(x.split('\t')[0], x.split('\t')[1]))
df_all['word_in_description'] = df_all['product_info'].map(lambda x: str_common_word(x.split('\t')[0],
                                            x.split('\t')[2]))

df_all = df_all.drop(['search_term', 'product_title', 'product_description', 'product_info'], axis=1)

df_train = df_all.iloc[:num_train]
df_test = df_all.iloc[num_train:]
id_test = df_test['id']


y_train = df_train['relevance'].values
X_train = df_train.drop(['id','relevance'],axis=1).values
X_test = df_test.drop(['id','relevance'],axis=1).values

X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train_split, y_train_split)

y_pred = model.predict(X_test_split)

rmse = np.sqrt(mean_squared_error(y_test_split, y_pred))
print("RMSE:", rmse)