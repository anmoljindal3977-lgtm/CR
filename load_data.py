import pandas as pd

# load the data
df = pd.read_csv('data/application_train.csv')

# show first 5 rows
print("First 5 rows:")
print(df.head())

# show columns
print("Columns:")
print(df.columns.tolist())