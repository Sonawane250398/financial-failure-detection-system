import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

# SOURCE LAYER — 1,000 clean transactions
n = 1000
source = pd.DataFrame({
    'transaction_id': [f'TXN{str(i).zfill(5)}' for i in range(1, n+1)],
    'account_id': [f'ACC{random.randint(100,150)}' for _ in range(n)],
    'transaction_date': pd.date_range('2024-01-01', periods=n, freq='H').strftime('%Y-%m-%d'),
    'amount': np.round(np.random.uniform(100, 50000, n), 2),
    'category': np.random.choice(['Revenue','COGS','OpEx','Tax','AR'], n),
    'currency': np.random.choice(['USD','EUR','GBP'], n, p=[0.7,0.2,0.1]),
    'status': 'POSTED'
})
source.to_csv('data/source_transactions.csv', index=False)

# TRANSFORMED LAYER — inject 4 real-world errors
transformed = source.copy()

# Error 1: 30 missing records (dropped in ETL)
drop_idx = np.random.choice(transformed.index, 30, replace=False)
transformed = transformed.drop(drop_idx)

# Error 2: 20 duplicate records
dupe_sample = transformed.sample(20)
transformed = pd.concat([transformed, dupe_sample], ignore_index=True)

# Error 3: 15 amount mismatches (ETL rounding/conversion bug)
mismatch_idx = np.random.choice(transformed.index, 15, replace=False)
transformed.loc[mismatch_idx, 'amount'] = transformed.loc[mismatch_idx, 'amount'] * 1.15

# Error 4: 10 category mapping errors
map_idx = np.random.choice(transformed.index, 10, replace=False)
transformed.loc[map_idx, 'category'] = 'UNKNOWN'

transformed.to_csv('data/transformed_transactions.csv', index=False)

# REPORTING LAYER — aggregate with more errors baked in
reporting = transformed.groupby(['account_id','category','transaction_date']).agg(
    total_amount=('amount','sum'),
    transaction_count=('transaction_id','count')
).reset_index()

# Error 5: 5 balance variances in reporting aggregation
var_idx = np.random.choice(reporting.index, 5, replace=False)
reporting.loc[var_idx, 'total_amount'] = reporting.loc[var_idx, 'total_amount'] * 0.88

reporting.to_csv('data/reporting_layer.csv', index=False)

print("Datasets created. Source:", len(source), "| Transformed:", len(transformed), "| Reporting rows:", len(reporting))
