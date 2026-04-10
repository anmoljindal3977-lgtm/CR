import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from lightgbm import LGBMClassifier


def train_model():
    df = pd.read_csv('data/application_train.csv')

    selected_columns = [
        'AMT_CREDIT', 'AMT_INCOME_TOTAL', 'AMT_ANNUITY',
        'DAYS_BIRTH', 'DAYS_EMPLOYED',
        'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3',
        'TARGET'
    ]
    df = df[selected_columns].dropna()
    df['income_credit_ratio'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']

    X = df.drop('TARGET', axis=1)
    y = df['TARGET']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LGBMClassifier(n_estimators=150, learning_rate=0.05, max_depth=6)
    model.fit(X_train, y_train)

    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/risk_model.pkl')

    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)

    print(f"Train complete: accuracy={accuracy:.4f}, auc={auc:.4f}")


if __name__ == '__main__':
    train_model()
