def evaluate(blocked_users, users):
    TP = FP = FN = 0
    total_users = len(users)

    premium_penalty = 0

    # Remove invalid IDs
    valid_ids = {user["id"] for user in users}
    blocked_users = [uid for uid in blocked_users if uid in valid_ids]

    for user in users:
        if user["is_bot"]:
            if user["id"] in blocked_users:
                TP += 1
            else:
                FN += 1
        else:
            if user["id"] in blocked_users:
                FP += 1

                if user["tier"] == "premium":
                    premium_penalty += 1

                print(f"[FP] Wrongly blocked real user: {user['id']} (tier: {user['tier']})")

    # metrics
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    
    # improved system health
    system_health = 1 - ((FN + FP) / total_users)

    # final score (balanced + realistic)
    score = max(
        0,
        (0.6 * f1) +
        (0.3 * system_health) -
        (0.1 * premium_penalty / total_users)
    )

    return {
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "system_health": system_health,
        "premium_penalty": premium_penalty,
        "score": score
    }
