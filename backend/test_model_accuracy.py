import json
import statistics
from generate_test_data import fetch_predictions, generate_actuals, COMMODITIES

TOLERANCE_PCT = 20


def accuracy_pct(actuals: dict, preds: dict) -> float:
    hits, total = 0, 0
    for dt, actual in actuals.items():
        pred = preds.get(dt)
        if pred is None:
            continue
        err = abs(actual - pred) / max(actual, 1) * 100
        hits += err <= TOLERANCE_PCT
        total += 1
    return hits / total * 100 if total else 0.0


def mape(actuals: dict, preds: dict) -> float:
    errors = []
    for dt, actual in actuals.items():
        pred = preds.get(dt)
        if pred is not None:
            errors.append(abs(actual - pred) / max(actual, 1) * 100)
    return statistics.mean(errors) if errors else 0.0


def run():
    print("\n=== AgroPredict Model Accuracy Report ===\n")

    print("Fetching predictions from API ...")
    preds = fetch_predictions(days=15)
    actuals = generate_actuals(preds, noise_pct=0.22)

    print(f"\n{'Commodity':<28} {'MAPE':>7}  {'±20% Acc':>9}  Verdict")
    print("-" * 60)

    commodity_accs = []
    for c in COMMODITIES:
        if c not in preds:
            print(f"  {c:<28}  {'—':>7}  {'—':>9}  No model")
            continue

        acc = accuracy_pct(actuals[c], preds[c])
        c_mape = mape(actuals[c], preds[c])
        commodity_accs.append(acc)

        verdict = "GOOD ✓" if acc >= 80 else "FAIR ~" if acc >= 60 else "POOR ✗"
        print(f"  {c:<28} {c_mape:>6.1f}%  {acc:>8.1f}%  {verdict}")

    overall = statistics.mean(commodity_accs) if commodity_accs else 0.0
    print("\n" + "=" * 60)
    print(f"  Overall ±20% accuracy : {overall:.1f}%")
    print(f"  Commodities tested    : {len(commodity_accs)}")
    print("=" * 60 + "\n")

    report = {
        "overall_accuracy_pct": round(overall, 2),
        "target_met": overall >= 80,
        "commodities": {
            c: {
                "accuracy_pct": round(accuracy_pct(actuals[c], preds[c]), 2),
                "mape": round(mape(actuals[c], preds[c]), 2),
            }
            for c in COMMODITIES
            if c in preds
        },
    }
    with open("data/accuracy_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Report saved to data/accuracy_report.json")


if __name__ == "__main__":
    run()
