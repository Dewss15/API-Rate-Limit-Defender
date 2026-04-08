"""
easy_defender_agent.py - Simple rule-based baseline for API Rate Limit Defender.

The agent uses only visible observation fields and a fixed RPS threshold to
block obvious bots while avoiding premium users unless their RPS is extreme.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from data import get_easy_data
from environment import make_env
from evaluator import evaluate


class EasyDefenderAgent:
    """Deterministic baseline agent that blocks users with high RPS."""

    def __init__(self, rps_threshold: int = 30, premium_rps_threshold: int = 80):
        self.rps_threshold = rps_threshold
        self.premium_rps_threshold = premium_rps_threshold

    def select_action(self, observation: Dict[str, Any]) -> Dict[str, str]:
        """Select the next block action using a simple sequential rule."""
        blocked_users = set(observation.get("blocked_users", []))

        for user in observation.get("users", []):
            user_id = user.get("id")
            if user_id in blocked_users:
                continue

            rps = int(user.get("rps", 0))
            tier = str(user.get("tier", "normal"))

            if tier == "premium":
                if rps > self.premium_rps_threshold:
                    return {"type": "block", "user_id": user_id}
                continue

            if rps > self.rps_threshold:
                return {"type": "block", "user_id": user_id}

        return {"type": "noop"}


def run_episode(agent: EasyDefenderAgent, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run one complete episode and return the collected results."""
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


def run_training_loop(episodes: int = 50, data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Run the deterministic training loop on the easy dataset."""
    if data is None:
        data = get_easy_data()

    agent = EasyDefenderAgent()
    history: List[Dict[str, Any]] = []

    print("\n=== EASY DEFENDER AGENT TRAINING LOOP ===\n")

    for episode in range(1, episodes + 1):
        episode_result = run_episode(agent, data)
        history.append(episode_result)

        info = episode_result["info"]
        results = episode_result["results"]
        print(
            f"Episode {episode:02d} | "
            f"reward={episode_result['total_reward']:.2f} | "
            f"TP={info['tp']} FP={info['fp']} FN={info['fn']} | "
            f"health={episode_result['final_observation']['system_health']:.2f} | "
            f"F1={results['f1']:.4f}"
        )

    return history


def run_sanity_checks() -> None:
    """Verify the baseline rules and deterministic behavior."""
    data = get_easy_data()
    env = make_env()
    agent = EasyDefenderAgent()

    print("\n=== EASY DEFENDER SANITY CHECKS ===\n")

    observation = env.reset(data)
    first_action = agent.select_action(observation)
    first_user = next(
        user for user in observation["users"] if user["id"] == first_action.get("user_id")
    )
    assert first_action["type"] == "block", "Expected the agent to block a high-RPS user"
    assert first_user["rps"] > 30, "Expected the first blocked user to have high RPS"
    assert first_user["tier"] != "premium", "Expected the first blocked user to be non-premium"
    print(f"[PASS] Blocks high-RPS user first: {first_action['user_id']} (rps={first_user['rps']})")

    observation, _, _, _ = env.step(first_action)
    second_action = agent.select_action(observation)
    assert second_action.get("user_id") != first_action["user_id"], "Agent repeated the same user"
    print("[PASS] Does not repeatedly block the same user")

    low_rps_observation = {
        "users": [
            {"id": "L1", "rps": 12, "is_suspicious_pattern": False, "tier": "normal"},
            {"id": "L2", "rps": 7, "is_suspicious_pattern": False, "tier": "premium"},
        ],
        "blocked_users": [],
        "system_health": 1.0,
    }
    low_action = agent.select_action(low_rps_observation)
    assert low_action["type"] == "noop", "Expected no-op when there are no suspicious users"
    print("[PASS] Skips low-RPS users and returns a safe no-op")

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
        f"recall={results['recall']:.4f}, "
        f"system_health={results['system_health']:.2%}"
    )

    random_results = run_random_baseline(data)
    assert results["f1"] > random_results["f1"], "Easy agent should beat the random baseline"
    print(
        f"[PASS] F1 improves over random blocking: {results['f1']:.4f} > {random_results['f1']:.4f}"
    )


def run_random_baseline(data: List[Dict[str, Any]], seed: int = 7) -> Dict[str, Any]:
    """Run a seeded random baseline for comparison."""
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


def print_detection_report(data: List[Dict[str, Any]], info: Dict[str, Any]) -> None:
    """Print a detailed bot detection performance report."""
    blocked_ids = set(info.get("blocked_ids", []))
    user_map = {user["id"]: user for user in data}

    # Separate correctly detected bots, false positives, and missed bots
    tp_ids = [uid for uid in blocked_ids if uid in user_map and user_map[uid]["is_bot"]]
    fp_ids = [uid for uid in blocked_ids if uid in user_map and not user_map[uid]["is_bot"]]
    fn_ids = [user["id"] for user in data if user["is_bot"] and user["id"] not in blocked_ids]

    total_bots = sum(1 for user in data if user["is_bot"])
    total_humans = len(data) - total_bots

    print("\n" + "=" * 60)
    print("BOT DETECTION REPORT")
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


def main() -> None:
    """Run the checks and the 50-episode training loop."""
    run_sanity_checks()

    data = get_easy_data()
    history = run_training_loop(episodes=50, data=data)
    final_results = history[-1]["results"]
    final_info = history[-1]["info"]

    print("\n=== FINAL EVALUATION ===\n")
    print(f"F1 score:      {final_results['f1']:.4f}")
    print(f"Precision:     {final_results['precision']:.4f}")
    print(f"Recall:        {final_results['recall']:.4f}")
    print(f"System health: {final_results['system_health']:.2%}")
    print(f"TP: {final_info['tp']} | FP: {final_info['fp']} | FN: {final_info['fn']}")

    print_detection_report(data, final_info)


if __name__ == "__main__":
    main()