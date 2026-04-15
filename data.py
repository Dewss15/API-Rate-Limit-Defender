# User format:
# {
#   "id": "U1",
#   "rps": int,
#   "is_suspicious_pattern": True/False,
#   "tier": "normal/premium",
#   "is_bot": True/False
# }

import random

# 🟢 EASY (10 users → obvious)
def get_easy_data():
    random.seed(42)
    return [
        # 👤 Users (7) - low to medium RPS
        {"id": "U1", "rps": random.randint(3, 8), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U2", "rps": random.randint(5, 10), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U3", "rps": random.randint(4, 9), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U4", "rps": random.randint(6, 12), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U5", "rps": random.randint(8, 15), "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},
        {"id": "U6", "rps": random.randint(4, 9), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U7", "rps": random.randint(10, 20), "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},

        # 🤖 Bots (3) - high RPS
        {"id": "U8", "rps": random.randint(50, 80), "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "U9", "rps": random.randint(60, 100), "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "U10", "rps": random.randint(70, 120), "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
    ]


# 🟡 MEDIUM (20 users → overlap starts)
def get_medium_data():
    random.seed(123)
    data = []

    # 👤 Users (14) - realistic RPS
    for i in range(1, 15):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(5, 30) if i % 2 else random.randint(8, 25),
            "is_suspicious_pattern": False,
            "tier": "normal" if i % 3 else "premium",
            "is_bot": False
        })

    # 🤖 Bots (6) - higher RPS
    for i in range(15, 21):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(40, 80),
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    return data


# 🔴 EXTREME (40 users → confusing)
def get_extreme_data():
    random.seed(456)
    data = []

    # 👤 Normal users (20) - realistic RPS
    for i in range(1, 21):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(5, 25),
            "is_suspicious_pattern": False,
            "tier": "normal",
            "is_bot": False
        })

    # 👑 VIP users (8 → trap - higher RPS but legit)
    for i in range(21, 29):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(20, 60),
            "is_suspicious_pattern": random.choice([True, False]),  # Some have patterns
            "tier": "premium",
            "is_bot": False
        })

    # 🤖 Bots (12 → mixed types)
    for i in range(29, 41):
        bot_type = i % 3
        if bot_type == 0:  # Low profile bot
            rps = random.randint(5, 15)
        elif bot_type == 1:  # Medium bot
            rps = random.randint(25, 45)
        else:  # High profile bot
            rps = random.randint(50, 100)

        data.append({
            "id": f"U{i}",
            "rps": rps,
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    return data


# 🏆 WINNING LEVEL (80 users → realistic system 🔥)
def get_winning_data():
    random.seed(789)
    data = []

    # 👤 Normal users (40) - low to medium RPS
    for i in range(1, 41):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(5, 25),
            "is_suspicious_pattern": False,
            "tier": "normal",
            "is_bot": False
        })

    # 👑 VIP users (16 → trap - high RPS but legit)
    for i in range(41, 57):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(15, 60),
            "is_suspicious_pattern": random.choice([True, False]),
            "tier": "premium",
            "is_bot": False
        })

    # 🤖 Bots (24 → mixed behavior)
    for i in range(57, 81):
        bot_type = i % 4
        if bot_type == 0:  # Stealth bot
            rps = random.randint(8, 18)
        elif bot_type == 1:  # Regular bot
            rps = random.randint(30, 60)
        elif bot_type == 2:  # Aggressive bot
            rps = random.randint(70, 120)
        else:  # Very aggressive
            rps = random.randint(100, 200)

        data.append({
            "id": f"U{i}",
            "rps": rps,
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    # 🔥 HARD CASES (VERY IMPORTANT)
    data.append({
        "id": "U100",
        "rps": random.randint(35, 55),
        "is_suspicious_pattern": True,
        "tier": "normal",
        "is_bot": False   # confusing human
    })

    data.append({
        "id": "U101",
        "rps": random.randint(8, 16),
        "is_suspicious_pattern": False,
        "tier": "normal",
        "is_bot": True   # stealth bot
    })

    data.append({
        "id": "U102",
        "rps": random.randint(70, 100),
        "is_suspicious_pattern": True,
        "tier": "premium",
        "is_bot": False  # VIP trap
    })

    return data