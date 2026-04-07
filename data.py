# User format:
# {
#   "id": "U1",
#   "rps": int,
#   "is_suspicious_pattern": True/False,
#   "tier": "normal/premium",
#   "is_bot": True/False
# }

# 🟢 EASY (10 users → obvious)
def get_easy_data():
    return [
        # 👤 Users (7)
        {"id": "U1", "rps": 3, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U2", "rps": 5, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U3", "rps": 4, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U4", "rps": 6, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U5", "rps": 5, "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},
        {"id": "U6", "rps": 4, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "U7", "rps": 6, "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},

        # 🤖 Bots (3)
        {"id": "U8", "rps": 400, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "U9", "rps": 500, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "U10", "rps": 600, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
    ]


# 🟡 MEDIUM (20 users → overlap starts)
def get_medium_data():
    data = []

    # 👤 Users (14)
    for i in range(1, 15):
        data.append({
            "id": f"U{i}",
            "rps": 20 + (i % 10),
            "is_suspicious_pattern": False,
            "tier": "normal" if i % 3 else "premium",
            "is_bot": False
        })

    # 🤖 Bots (6)
    for i in range(15, 21):
        data.append({
            "id": f"U{i}",
            "rps": 25 + (i % 10),
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    return data


# 🔴 EXTREME (40 users → confusing)
def get_extreme_data():
    data = []

    # 👤 Normal users (20)
    for i in range(1, 21):
        data.append({
            "id": f"U{i}",
            "rps": 10 + (i % 20),
            "is_suspicious_pattern": False,
            "tier": "normal",
            "is_bot": False
        })

    # 👑 VIP users (8 → trap)
    for i in range(21, 29):
        data.append({
            "id": f"U{i}",
            "rps": 50 + (i % 20),
            "is_suspicious_pattern": True,
            "tier": "premium",
            "is_bot": False
        })

    # 🤖 Bots (12 → mixed types)
    for i in range(29, 41):
        data.append({
            "id": f"U{i}",
            "rps": [5, 15, 40, 80][i % 4],  # low + medium + high bots
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    return data


# 🏆 WINNING LEVEL (80 users → realistic system 🔥)
def get_winning_data():
    data = []

    # 👤 Normal users (40)
    for i in range(1, 41):
        data.append({
            "id": f"U{i}",
            "rps": 5 + (i % 20),
            "is_suspicious_pattern": False,
            "tier": "normal",
            "is_bot": False
        })

    # 👑 VIP users (16 → trap)
    for i in range(41, 57):
        data.append({
            "id": f"U{i}",
            "rps": 40 + (i % 40),
            "is_suspicious_pattern": True,
            "tier": "premium",
            "is_bot": False
        })

    # 🤖 Bots (24 → mixed behavior)
    for i in range(57, 81):
        data.append({
            "id": f"U{i}",
            "rps": (i % 3) * 100 + (i % 10),
            "is_suspicious_pattern": True,
            "tier": "normal",
            "is_bot": True
        })

    # 🔥 HARD CASES (VERY IMPORTANT)
    data.append({
        "id": "U100",
        "rps": 45,
        "is_suspicious_pattern": True,
        "tier": "normal",
        "is_bot": False   # confusing human
    })

    data.append({
        "id": "U101",
        "rps": 10,
        "is_suspicious_pattern": False,
        "tier": "normal",
        "is_bot": True   # stealth bot
    })

    data.append({
        "id": "U102",
        "rps": 80,
        "is_suspicious_pattern": True,
        "tier": "premium",
        "is_bot": False  # VIP trap
    })

    return data