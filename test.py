from data import get_winning_data
from evaluator import evaluate

data = get_winning_data()

blocked = []

for user in data:
    if user["tier"] == "premium":
        continue

    if user["rps"] > 30 or user["is_suspicious_pattern"]:
        blocked.append(user["id"])

results = evaluate(blocked, data)

print("\n--- 📊 JUDGE'S SCORECARD ---")
print(f"Final Score:   {results['score']:.4f}")
print(f"F1 Score:      {results['f1']:.4f}")
print(f"Precision:     {results['precision']:.4f}")
print(f"Recall:        {results['recall']:.4f}")
print(f"System Health: {results['system_health']:.2%}")
print(f"TP: {results['TP']} | FP: {results['FP']} | FN: {results['FN']}")