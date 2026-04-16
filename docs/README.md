markdown# Financial Reporting Failure Detection System

## Business Problem
Month-end financial reporting failures — missing records, duplicate entries, 
amount mismatches, and balance variances — reach stakeholders undetected, 
causing restatements, audit findings, and reporting delays.

This system detects those failures before they reach the reporting layer.

---

## What This System Does

Simulates a 3-layer financial data pipeline (Source → Transformed → Reporting) 
with real-world ETL errors injected. Runs 5 automated reconciliation checks. 
Classifies every exception by severity. Outputs an audit-ready exception report.

---

## Architecture
Source Layer (1,000 transactions)
↓
Transformed Layer (ETL processed — errors injected)
↓
Reporting Layer (aggregated — balance variances injected)
↓
Reconciliation Engine (5 SQL checks + Python automation)
↓
Exception Report (CRITICAL / HIGH / MEDIUM — CSV output)

---

## Failure Types Detected

| Check | Failure Type | Severity |
|-------|-------------|----------|
| 1 | Missing records — dropped in ETL | CRITICAL |
| 2 | Duplicate records in transformed layer | HIGH |
| 3 | Amount mismatches > 10% variance | CRITICAL |
| 4 | Invalid category mapping (GL unmappable) | HIGH |
| 5 | Reporting layer balance variance | CRITICAL |

---

## Results

- **1,000** source transactions processed  
- **80** exceptions detected automatically  
- **50 CRITICAL** — require immediate remediation before reporting  
- **30 HIGH** — require investigation before close  
- **0** manual steps  

---

## Files

| File | Purpose |
|------|---------|
| `data/generate_data.py` | Generates 3-layer dataset with injected failures |
| `sql/reconciliation_checks.sql` | 5 SQL checks across pipeline layers |
| `python/failure_detection.py` | Automated detection engine with severity classification |
| `outputs/exception_report.csv` | Audit-ready exception output |

---

## Business Scenario

Designed around a month-end close failure scenario where ETL processing 
introduced silent errors — records dropped, amounts inflated, categories 
unmapped — that would have passed into the reporting layer undetected.

System catches all 5 failure types before stakeholder delivery.

---

## Tech Stack
Python · Pandas · SQL · CSV · Severity Classification Engine

