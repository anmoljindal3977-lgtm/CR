import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from lightgbm import LGBMClassifier
import joblib
import os

# load the data
df = pd.read_csv('data/application_train.csv')

# using only a few columns to keep model simple
selected_columns = [
    'AMT_CREDIT', 'AMT_INCOME_TOTAL', 'AMT_ANNUITY',
    'DAYS_BIRTH', 'DAYS_EMPLOYED',
    'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3',
    'TARGET'
]
df = df[selected_columns]

# simple ratio to see if income can handle credit
df['income_credit_ratio'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']

# dropping missing values for now
df = df.dropna()

# show first 5 rows
print("First 5 rows:")
print(df.head())

# show columns
print("Columns:")
print(df.columns.tolist())

# print dataset shape after cleaning
print("Dataset shape after cleaning:")
print(df.shape)

# using lightgbm instead of basic model
# not tuning much, just default params

# split data into train/test (80/20)
X = df.drop('TARGET', axis=1)
y = df['TARGET']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# create model
model = LGBMClassifier(
    n_estimators=150,
    learning_rate=0.05,
    max_depth=6
)

# train model using same train/test split
model.fit(X_train, y_train)

# save model
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/risk_model.pkl')

# predict probability using
y_pred_proba = model.predict_proba(X_test)[:, 1]

# print accuracy and ROC AUC score
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)
print(f"Accuracy: {accuracy:.4f}")
print(f"AUC: {auc:.4f}")