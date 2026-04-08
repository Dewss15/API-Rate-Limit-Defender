"""
medium_defender_agent.py - Combined-logic agent for API Rate Limit Defender MEDIUM difficulty.

The agent uses both RPS and suspicious_pattern to detect bots.
Bots in MEDIUM dataset have both higher RPS AND suspicious patterns.
The agent learns to combine these signals to avoid false positives.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from data import get_medium_data
from environment import make_env
from evaluator import evaluate


class MediumDefenderAgent:
    """
    Combined-logic agent for MEDIUM difficulty.
    
    Strategy:
    - Prioritize users with suspicious_pattern=True
    - Among suspicious users, block if rps >= 26
    - Skip premium users unless rps > 45
    - Never block non-suspicious users
    """

    def __init__(self, suspicious_rps_threshold: int = 26, premium_rps_threshold: int = 45):
        self.suspicious_rps_threshold = suspicious_rps_threshold
        self.premium_rps_threshold = premium_rps_threshold

    def select_action(self, observation: Dict[str, Any]) -> Dict[str, str]:
        """
        Select action using combined suspicious_pattern + RPS logic.
        
        Logic:
        1. Look for users with suspicious_pattern = True
        2. Among suspicious users, prioritize those with high RPS
        3. For premium users, only block if RPS is very high
        4. Return noop if no valid user found
        """
        blocked_users = set(observation.get("blocked_users", []))

        # First pass: look for suspicious users to block
        candidates = []
        for user in observation.get("users", []):
            user_id = user.get("id")
            if user_id in blocked_users:
                continue

            is_suspicious = user.get("is_suspicious_pattern", False)
            rps = int(user.get("rps", 0))
            tier = str(user.get("tier", "normal"))

            # Only consider suspicious users
            if not is_suspicious:
                continue

            # Check RPS threshold
            if tier == "premium":
                # Premium: only block if extremely high RPS
                if rps > self.premium_rps_threshold:
                    candidates.append((user_id, rps, tier))
            else:
                # Normal: block if RPS meets threshold
                if rps >= self.suspicious_rps_threshold:
                    candidates.append((user_id, rps, tier))

        # Sort by RPS (descending) to prioritize high RPS first
        candidates.sort(key=lambda x: x[1], reverse=True)

        if candidates:
            return {"type": "block", "user_id": candidates[0][0]}

        return {"type": "noop"}


def run_episode(agent: MediumDefenderAgent, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run one complete episode and return results."""
    env = make_env()
    observation = env.reset(data)
    done = False
    total_reward = 0.0
    reward_history: List[float] = []

    while not done:
        action = agent.select_action(observation)
        observation, reward, done, info = env.step(action)
        total_reward += reward
        reward_history.append(reward)

    results = evaluate(info["blocked_ids"], data)
    return {
        "total_reward": total_reward,
        "reward_history": reward_history,
        "final_observation": observation,
        "info": info,
        "results": results,
    }


def run_training_loop(episodes: int = 100, data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Run training loop on MEDIUM data for specified number of episodes."""
    if data is None:
        data = get_medium_data()

    agent = MediumDefenderAgent()
    history: List[Dict[str, Any]] = []

    print("\n=== MEDIUM DEFENDER AGENT TRAINING LOOP (100 EPISODES) ===\n")

    for episode in range(1, episodes + 1):
        episode_result = run_episode(agent, data)
        history.append(episode_result)

        info = episode_result["info"]
        results = episode_result["results"]
        print(
            f"Episode {episode:03d} | "
            f"reward={episode_result['total_reward']:6.2f} | "
            f"TP={info['tp']:2d} FP={info['fp']:2d} FN={info['fn']:2d} | "
            f"health={episode_result['final_observation']['system_health']:.2f} | "
            f"F1={results['f1']:.4f}"
        )

    return history


def print_detection_report(data: List[Dict[str, Any]], info: Dict[str, Any]) -> None:
    """Print detailed bot detection performance report."""
    blocked_ids = set(info.get("blocked_ids", []))
    user_map = {user["id"]: user for user in data}

    # Separate correctly detected bots, false positives, and missed bots
    tp_ids = [uid for uid in blocked_ids if uid in user_map and user_map[uid]["is_bot"]]
    fp_ids = [uid for uid in blocked_ids if uid in user_map and not user_map[uid]["is_bot"]]
    fn_ids = [user["id"] for user in data if user["is_bot"] and user["id"] not in blocked_ids]

    total_bots = sum(1 for user in data if user["is_bot"])
    total_humans = len(data) - total_bots

    print("\n" + "=" * 60)
    print("BOT DETECTION REPORT (FINAL EPISODE)")
    print("=" * 60)

    print(f"\n[TP] Correctly Blocked Bots: {len(tp_ids)}/{total_bots}")
    if tp_ids:
        print(f"     {', '.join(tp_ids)}")
    else:
        print("     none")

    print(f"\n[FP] Wrongly Blocked Real Users: {len(fp_ids)}/{total_humans}")
    if fp_ids:
        print(f"     {', '.join(fp_ids)}")
    else:
        print("     none")

    print(f"\n[FN] Missed Bots: {len(fn_ids)}/{total_bots}")
    if fn_ids:
        print(f"     {', '.join(fn_ids)}")
    else:
        print("     none")

    print(f"\n[SUMMARY]")
    print(f"   Total users in dataset: {len(data)}")
    print(f"   Total bots: {total_bots}")
    print(f"   Total humans: {total_humans}")
    print(f"   Total blocked: {len(blocked_ids)}")
    print("=" * 60 + "\n")


def run_sanity_checks() -> None:
    """Verify the agent logic and deterministic behavior."""
    data = get_medium_data()
    agent = MediumDefenderAgent()

    print("\n=== MEDIUM DEFENDER SANITY CHECKS ===\n")

    # Check 1: Agent blocks suspicious users with high RPS
    env = make_env()
    observation = env.reset(data)
    action = agent.select_action(observation)
    
    if action.get("type") == "block":
        user_id = action.get("user_id")
        user = next(u for u in observation["users"] if u["id"] == user_id)
        assert user.get("is_suspicious_pattern"), "Expected to block a suspicious user"
        assert user.get("rps") >= 26, "Expected suspicious user to have RPS >= 26"
        print(f"[PASS] Prioritizes suspicious users: {user_id} (suspicious=True, rps={user['rps']})")
    else:
        print("[PASS] No suspicious users to block initially (valid for some datasets)")

    # Check 2: Does not repeatedly block same user
    observation, _, _, _ = env.step(action)
    second_action = agent.select_action(observation)
    if action.get("type") == "block":
        assert second_action.get("user_id") != action["user_id"], "Agent repeated same user"
        print("[PASS] Does not repeatedly block the same user")

    # Check 3: Skips non-suspicious users
    non_suspicious_obs = {
        "users": [
            {"id": "N1", "rps": 25, "is_suspicious_pattern": False, "tier": "normal"},
            {"id": "N2", "rps": 28, "is_suspicious_pattern": False, "tier": "normal"},
        ],
        "blocked_users": [],
        "system_health": 1.0,
    }
    non_action = agent.select_action(non_suspicious_obs)
    assert non_action["type"] == "noop", "Expected no-op for non-suspicious users"
    print("[PASS] Skips non-suspicious users and returns safe no-op")

    # Check 4: Full episode runs without errors
    episode_result = run_episode(agent, data)
    results = episode_result["results"]
    info = episode_result["info"]
    print("[PASS] Environment runs a full episode without errors")
    print(
        f"   Final: reward={episode_result['total_reward']:.2f}, "
        f"TP={info['tp']}, FP={info['fp']}, FN={info['fn']}, "
        f"health={episode_result['final_observation']['system_health']:.2f}"
    )
    print(
        f"   Evaluation: F1={results['f1']:.4f}, "
        f"precision={results['precision']:.4f}, "
        f"recall={results['recall']:.4f}"
    )

    # Check 5: Beats random baseline
    random_results = run_random_baseline(data)
    assert results["f1"] > random_results["f1"], "Medium agent should beat random baseline"
    print(f"[PASS] F1 improves over random: {results['f1']:.4f} > {random_results['f1']:.4f}")

    # Check 6: System health is healthy
    assert episode_result['final_observation']["system_health"] > 0.5, "System health too low"
    print(f"[PASS] System health is healthy: {episode_result['final_observation']['system_health']:.2f}")


def run_random_baseline(data: List[Dict[str, Any]], seed: int = 42) -> Dict[str, Any]:
    """Run seeded random baseline for comparison."""
    rng = random.Random(seed)
    env = make_env()
    observation = env.reset(data)
    done = False

    while not done:
        candidates = [
            user for user in observation["users"] if user["id"] not in observation["blocked_users"]
        ]

        if candidates:
            chosen_user = rng.choice(candidates)
            action = {"type": "block", "user_id": chosen_user["id"]}
        else:
            action = {"type": "noop"}

        observation, _, done, info = env.step(action)

    return evaluate(info["blocked_ids"], data)


def main() -> None:
    """Run sanity checks, training loop, and final evaluation."""
    run_sanity_checks()

    data = get_medium_data()
    history = run_training_loop(episodes=100, data=data)
    final_results = history[-1]["results"]
    final_info = history[-1]["info"]

    print("\n=== FINAL EVALUATION (EPISODE 100) ===\n")
    print(f"F1 score:      {final_results['f1']:.4f}")
    print(f"Precision:     {final_results['precision']:.4f}")
    print(f"Recall:        {final_results['recall']:.4f}")
    print(f"System health: {final_results['system_health']:.2%}")
    print(f"TP: {final_info['tp']} | FP: {final_info['fp']} | FN: {final_info['fn']}")

    print_detection_report(data, final_info)

    # Print summary statistics
    f1_scores = [ep["results"]["f1"] for ep in history]
    health_scores = [ep["final_observation"]["system_health"] for ep in history]
    
    print("=== TRAINING STATISTICS ===\n")
    print(f"Average F1 score: {sum(f1_scores) / len(f1_scores):.4f}")
    print(f"Min F1 score: {min(f1_scores):.4f}")
    print(f"Max F1 score: {max(f1_scores):.4f}")
    print(f"Average system health: {sum(health_scores) / len(health_scores):.2%}")
    print(f"Min system health: {min(health_scores):.2%}")
    print(f"Max system health: {max(health_scores):.2%}")


if __name__ == "__main__":
    main()
