## Evidence Table

| Metric | Definition | Value | Population | Known | Unknown | Assumption | Limitation |
|---|---|---:|---:|---|---|---|---|
| Late Delivery Rate | % of valid delivered orders arriving after the estimated delivery date | 8.12% | 96,281 | Actual and estimated delivery timestamps | Exact cause of each delay | Invalid lifecycle timestamps are excluded from the KPI population | Depends on the accuracy of the estimated delivery date |
| Median Delivery Variance | Median days between actual and estimated delivery | -11.93 days | 96,281 | Actual and estimated delivery timestamps | Why individual orders differ from estimates | Negative means delivery occurred before the estimate | Sensitive to how the valid KPI population is defined |
| Median Purchase → Carrier | Median days from purchase to carrier handoff | 2.20 days | 96,281 | Purchase and carrier timestamps | Reason for seller/processing delays | Only chronologically valid timestamps are included | Extreme positive durations create a long right tail |
| Median Carrier → Customer | Median days from carrier handoff to customer delivery | 7.10 days | 96,281 | Carrier and customer delivery timestamps | Exact cause of carrier-to-customer delays | Only chronologically valid timestamps are included | Shows association with delivery performance, not causation |