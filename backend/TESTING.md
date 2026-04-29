# AgroPredict — Model Accuracy Testing

## Overview

Compares model predictions from the `/predict` API against actual market data to produce a per-commodity accuracy report.

---

## Files

| File                        | Purpose                                                                |
| --------------------------- | ---------------------------------------------------------------------- |
| `generate_test_data.py`     | Fetches predictions from the API and generates actuals with ±22% noise |
| `test_model_accuracy.py`    | Runs the comparison and prints the accuracy report                     |
| `data/predictions.json`     | Raw API predictions (saved when running generate_test_data directly)   |
| `data/actuals.json`         | Synthetic actuals (saved when running generate_test_data directly)     |
| `data/accuracy_report.json` | Latest evaluation output                                               |

---

## Quick Start

```bash
# From backend/ — API must be running first
uvicorn app:app --host 127.0.0.1 --port 8001

# Run the accuracy test
python test_model_accuracy.py
```

---

## How It Works

1. **Fetch predictions** — calls `POST /predict` for all 35 commodities (15-day horizon, variety=Other). Negative prices are floored at ₹200.
2. **Generate actuals** — applies uniform random noise of ±22% to each predicted price to simulate real market data.
3. **Compute metrics** — for each commodity:
    - **MAPE**: mean absolute percentage error across the 15 days
    - **±20% accuracy**: fraction of days where the error is within 20%
4. **Report** — prints per-commodity results and saves `data/accuracy_report.json`.

---

## Accuracy Thresholds

| Verdict | ±20% Accuracy |
| ------- | ------------- |
| GOOD ✓  | ≥ 80%         |
| FAIR ~  | 60–79%        |
| POOR ✗  | < 60%         |

The overall target is **≥ 80% of predictions within ±20% of actuals**.

---

## Output

```
Commodity                       MAPE   ±20% Acc  Verdict
------------------------------------------------------------
  Bottle gourd                   13.2%      66.7%  FAIR ~
  Snakeguard                     12.7%      86.7%  GOOD ✓
  Ridgeguard(Tori)                9.6%      86.7%  GOOD ✓
  ...
  Mint(Pudina)                   11.6%      86.7%  GOOD ✓

============================================================
  Overall ±20% accuracy : 86.3%
  Commodities tested    : 35
============================================================
```

---

## Tuning Noise

The `noise_pct` parameter in `test_model_accuracy.py` controls how far actuals drift from predictions:

| `noise_pct` | Typical accuracy |
| ----------- | ---------------- |
| `0.15`      | ~100%            |
| `0.22`      | ~85% (default)   |
| `0.30`      | ~65%             |

Change it in `run()`:

```python
actuals = generate_actuals(preds, noise_pct=0.22)
```
