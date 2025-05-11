import  pandas as pd

df = pd.read_csv("data/Transactions_cleaned.csv", on_bad_lines="skip")

print(df['listPrice'].min(), df['listPrice'].max())
df["transactionDate"] = df["transactionDate"].str.replace(r"\+AC0-", "-", regex=True)
df["transactionDate"] = pd.to_datetime(df["transactionDate"], errors="coerce", format="%d-%m-%Y")

df.to_csv('data/Transactions_cleaned2.csv',  encoding='utf-8', index=False)


