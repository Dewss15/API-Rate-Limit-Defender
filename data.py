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
        # 👤 Normal users (7)
        {"id": "U1", "rps": random.randint(3, 8), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U2", "rps": random.randint(5, 10), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U3", "rps": random.randint(4, 9), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U4", "rps": random.randint(6, 12), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U5", "rps": random.randint(8, 15), "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},
        {"id": "U6", "rps": random.randint(4, 9), "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U7", "rps": random.randint(10, 20), "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},

        # 🤖 Bots (3)
        {"id": "U8", "rps": random.randint(50, 80), "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "U9", "rps": random.randint(60, 100), "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "U10", "rps": random.randint(70, 120), "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
    ]


# 🟡 MEDIUM (20 users → realistic overlap)
def get_medium_data():
    random.seed(123)
    data = []

    # 👤 Normal users (14)
    for i in range(1, 15):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(5, 30),
            "is_suspicious_pattern": False,
            "tier": "premium" if i % 4 == 0 else "normal",
            "is_bot": False
        })

    # 🤖 Bots (6)
    for i in range(15, 21):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(30, 80),
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    # 🔥 Edge cases (IMPORTANT)
    data.append({
        "id": "U21",
        "rps": random.randint(10, 18),
        "is_suspicious_pattern": False,
        "tier": "normal",
        "is_bot": True   # stealth bot
    })

    data.append({
        "id": "U22",
        "rps": random.randint(25, 40),
        "is_suspicious_pattern": False,
        "tier": "normal",
        "is_bot": False  # heavy legit user
    })

    return data


# 🔴 EXTREME (40 users → confusing cases)
def get_extreme_data():
    random.seed(456)
    data = []

    # 👤 Normal users (20)
    for i in range(1, 21):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(5, 25),
            "is_suspicious_pattern": False,
            "tier": "normal",
            "is_bot": False
        })

    # 👑 Premium users (8 → tricky)
    for i in range(21, 29):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(20, 60),
            "is_suspicious_pattern": random.choice([True, False]),
            "tier": "premium",
            "is_bot": False
        })

    # 🤖 Bots (12 → mixed)
    for i in range(29, 41):
        rps = random.choice([
            random.randint(5, 15),    # stealth
            random.randint(20, 40),   # medium
            random.randint(50, 100)   # aggressive
        ])

        data.append({
            "id": f"U{i}",
            "rps": rps,
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    return data


# 🏆 WINNING LEVEL (80+ users → real-world simulation)
def get_winning_data():
    random.seed(789)
    data = []

    # 👤 Normal users (40)
    for i in range(1, 41):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(5, 25),
            "is_suspicious_pattern": False,
            "tier": "normal",
            "is_bot": False
        })

    # 👑 Premium users (16 → trap)
    for i in range(41, 57):
        data.append({
            "id": f"U{i}",
            "rps": random.randint(15, 60),
            "is_suspicious_pattern": random.choice([True, False]),
            "tier": "premium",
            "is_bot": False
        })

    # 🤖 Bots (24 → realistic attack mix)
    for i in range(57, 81):
        bot_type = random.choice(["stealth", "medium", "aggressive"])

        if bot_type == "stealth":
            rps = random.randint(8, 18)
            pattern = random.choice([False, True])
        elif bot_type == "medium":
            rps = random.randint(30, 60)
            pattern = True
        else:
            rps = random.randint(70, 150)
            pattern = True

        data.append({
            "id": f"U{i}",
            "rps": rps,
            "is_suspicious_pattern": pattern,
            "tier": "normal",
            "is_bot": True
        })

    # 🔥 CRITICAL EDGE CASES
    data.extend([
        {
            "id": "U100",
            "rps": random.randint(35, 55),
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": False  # confusing human
        },
        {
            "id": "U101",
            "rps": random.randint(8, 16),
            "is_suspicious_pattern": False,
            "tier": "normal",
            "is_bot": True   # stealth bot
        },
        {
            "id": "U102",
            "rps": random.randint(70, 100),
            "is_suspicious_pattern": True,
            "tier": "premium",
            "is_bot": False  # VIP trap
        }
    ])

    return data
