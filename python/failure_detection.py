import pandas as pd
import numpy as np
from datetime import datetime


# Load datasets
source = pd.read_csv('data/source_transactions.csv')
transformed = pd.read_csv('data/transformed_transactions.csv')
reporting = pd.read_csv('data/reporting_layer.csv')

exceptions = []


def log_exception(txn_id, failure_type, severity, detail):
    exceptions.append({
        'detected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'transaction_id': txn_id,
        'failure_type': failure_type,
        'severity': severity,
        'detail': detail
    })


# CHECK 1: Missing records
missing = source[~source['transaction_id'].isin(transformed['transaction_id'])]
for _, row in missing.iterrows():
    log_exception(
        row['transaction_id'],
        'MISSING_IN_TRANSFORM',
        'CRITICAL',
        f"Amount ${row['amount']:,.2f} | Category {row['category']} | Date {row['transaction_date']}"
    )

# CHECK 2: Duplicates
dupes = transformed[transformed.duplicated('transaction_id', keep=False)]
dup_ids = dupes['transaction_id'].unique()
for tid in dup_ids:
    count = len(dupes[dupes['transaction_id'] == tid])
    log_exception(tid, 'DUPLICATE_RECORD', 'HIGH', f"Appears {count}x in transformed layer")

# CHECK 3: Amount mismatches
merged = source.merge(transformed, on='transaction_id', suffixes=('_src', '_trn'))
merged['variance'] = abs(merged['amount_src'] - merged['amount_trn'])
merged['variance_pct'] = merged['variance'] / merged['amount_src']
mismatches = merged[merged['variance'] > 0.01]
for _, row in mismatches.iterrows():
    severity = (
        'CRITICAL'
        if row['variance_pct'] > 0.10
        else ('HIGH' if row['variance_pct'] > 0.05 else 'MEDIUM')
    )
    log_exception(
        row['transaction_id'],
        'AMOUNT_MISMATCH',
        severity,
        f"Source ${row['amount_src']:,.2f} → Transformed ${row['amount_trn']:,.2f} | Variance {row['variance_pct']*100:.1f}%"
    )

# CHECK 4: Category mapping errors
valid_categories = {'Revenue', 'COGS', 'OpEx', 'Tax', 'AR'}
bad_cats = transformed[~transformed['category'].isin(valid_categories)]
for _, row in bad_cats.iterrows():
    log_exception(
        row['transaction_id'],
        'INVALID_CATEGORY',
        'HIGH',
        f"Invalid category '{row['category']}' — cannot map to GL account"
    )

# CHECK 5: Reporting balance variance
# Aggregated totals don't match transformed layer totals
t_agg = (
    transformed.groupby(['account_id', 'category', 'transaction_date'])['amount']
    .sum()
    .reset_index()
)
t_agg.columns = ['account_id', 'category', 'transaction_date', 'expected_total']
rep_check = t_agg.merge(reporting, on=['account_id', 'category', 'transaction_date'])
rep_check['balance_var'] = abs(rep_check['expected_total'] - rep_check['total_amount'])
variances = rep_check[rep_check['balance_var'] > 1.00]
for _, row in variances.iterrows():
    log_exception(
        f"AGG-{row['account_id']}",
        'REPORTING_BALANCE_VARIANCE',
        'CRITICAL',
        f"Expected ${row['expected_total']:,.2f} | Reported ${row['total_amount']:,.2f} | Gap ${row['balance_var']:,.2f}"
    )

# Output exception report
df_exceptions = pd.DataFrame(exceptions)
df_exceptions.to_csv('outputs/exception_report.csv', index=False)

# Summary
print("\n=== FAILURE DETECTION SUMMARY ===")
print(f"Total Exceptions Detected: {len(df_exceptions)}")
print(df_exceptions['severity'].value_counts().to_string())
print(f"\nException report saved → outputs/exception_report.csv")

