"""
This script evaluates the alt credit agent using test data.
"""

import pandas as pd
from sklearn.metrics import precision_recall_fscore_support
from agents.alt_credit import generate_alt_credit

# loading sample data
df = pd.read_csv('data/application_test.csv')
required_columns = [
    'AMT_CREDIT', 'AMT_INCOME_TOTAL', 'AMT_ANNUITY', 'DAYS_BIRTH', 'DAYS_EMPLOYED',
    'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'SK_ID_CURR'
]
df = df[required_columns]
df = df.head(20)

# creating basic labels
labels = []
for _, row in df.iterrows():
    if row['AMT_INCOME_TOTAL'] < 150000:
        labels.append(1)  # high risk
    else:
        labels.append(0)  # low risk

# testing alt credit agent
predictions = []
for _, row in df.iterrows():
    data = row.to_dict()
    result = generate_alt_credit(data)
    alt_credit_score = result['alt_credit_score']
    if alt_credit_score > 0.6:
        pred = 0
    else:
        pred = 1
    predictions.append(pred)

# compute metrics
precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')

print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")