import pandas as pd
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras import backend as k
from keras.callbacks import ModelCheckpoint, EarlyStopping


def rmse_score(y_true, y_pred):
    return k.sqrt(k.mean(k.square(y_pred - y_true)))


df_train = pd.read_csv('train.csv', encoding="ISO-8859-1")
df_test = pd.read_csv('test.csv', encoding="ISO-8859-1")
df_pro_desc = pd.read_csv('product_descriptions.csv')

df_train = pd.merge(df_train, df_pro_desc, how='left', on='product_uid')
df_test = pd.merge(df_test, df_pro_desc, how='left', on='product_uid')

df_train['text'] = df_train['search_term'] + ' ' + df_train['product_title'] + ' ' + df_train['product_description']
df_test['text'] = df_test['search_term'] + ' ' + df_test['product_title'] + ' ' + df_test['product_description']

tokenizer = Tokenizer()
tokenizer.fit_on_texts(df_train['text'])
X_train_seq = tokenizer.texts_to_sequences(df_train['text'])
X_test_seq = tokenizer.texts_to_sequences(df_test['text'])

# sequences padding
max_seq_length = max([len(seq) for seq in X_train_seq])
X_train_padded = pad_sequences(X_train_seq, maxlen=max_seq_length)
X_test_padded = pad_sequences(X_test_seq, maxlen=max_seq_length)

y_train = df_train['relevance'].values

scaler = MinMaxScaler()
y_train_scaled = scaler.fit_transform(y_train.reshape(-1, 1)).reshape(-1)

X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(X_train_padded, y_train_scaled,
                                                                          test_size=0.2, random_state=42)
# defining model parameters
num_words = len(tokenizer.word_index) + 1  # unique words in data
embedding_dim = 50
model = Sequential()
model.add(Embedding(input_dim=num_words, output_dim=embedding_dim, input_length=max_seq_length))
model.add(LSTM(units=100))
model.add(Dense(units=1, activation='linear'))
# fitting
model.compile(optimizer=Adam(learning_rate=0.01), loss=rmse_score, metrics=['mse'])

# define callbacks
checkpoint = ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True, mode='min')
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
history = model.fit(X_train_split, y_train_split,
                    epochs=10, batch_size=32,
                    validation_split=0.2,
                    callbacks=[checkpoint, early_stopping])

# evaluation
loss, rmse_value = model.evaluate(X_val_split, y_val_split)
print(f"Validation Loss: {loss}, RMSE: {rmse_value}")

y_test_pred = model.predict(X_test_padded)
y_test_pred_rescaled = scaler.inverse_transform(y_test_pred).reshape(-1)
submission = pd.DataFrame({"id": df_test['id'], "relevance": y_test_pred_rescaled})
submission.to_csv('submission.csv', index=True)
