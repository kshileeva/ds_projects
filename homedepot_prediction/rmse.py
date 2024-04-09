from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn_rand_forest import X_train, y_train, clf

X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
clf.fit(X_train_split, y_train_split)

y_pred_split = clf.predict(X_test_split)
rmse = np.sqrt(mean_squared_error(y_test_split, y_pred_split))
print(rmse)