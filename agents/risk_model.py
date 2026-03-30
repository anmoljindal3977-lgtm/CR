import pandas as pd
import joblib

def predict_risk(data: dict) -> dict:
    # loading model
    model = joblib.load('models/risk_model.pkl')

    # preparing input
    # adding same feature used during training
    data['income_credit_ratio'] = data['AMT_INCOME_TOTAL'] / data['AMT_CREDIT']

    required_columns = [
        'AMT_CREDIT', 'AMT_INCOME_TOTAL', 'AMT_ANNUITY',
        'DAYS_BIRTH', 'DAYS_EMPLOYED',
        'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3',
        'income_credit_ratio'
    ]
    df = pd.DataFrame([data])
    df = df[required_columns]

    # predicting risk
    p_default = model.predict_proba(df)[0][1]

    return {
        "p_default": float(p_default),
        "model_used": "lightgbm",
        "comment": "simple probability from model"
    }