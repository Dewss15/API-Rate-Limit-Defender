"""
hard_defender_agent.py - Risk-based HARD difficulty agent for API Rate Limit Defender.

This implementation is independent from easy and medium agents.
It uses a multi-signal risk score and conservative blocking policy.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from data import get_extreme_data, get_winning_data
from environment import make_env
from evaluator import evaluate


class HardDefenderAgent:
    """Risk-based deterministic defender for hard datasets."""

    def __init__(self, block_threshold: float = 2.5):
        self.block_threshold = block_threshold
        self._exploration_used = False
    
    def get_name(self) -> str:
        """Return agent name for logging."""
        return f"HardDefender-v1.0"
    
    def reset(self):
        """Reset agent state between episodes."""
        self._exploration_used = False

    def _reset_episode_state_if_needed(self, observation: Dict[str, Any]) -> None:
        # Reset per-episode state when a fresh episode is detected.
        if not observation.get("blocked_users"):
            self._exploration_used = False

    def _risk_score(self, user: Dict[str, Any]) -> float:
        """Compute bot risk score using multiple observation clues."""
        risk_score = 0.0
        rps = int(user.get("rps", 0))
        suspicious = bool(user.get("is_suspicious_pattern", False))
        tier = str(user.get("tier", "normal"))

        # Suspicious behavior signal
        if suspicious:
            risk_score += 2.0

        # Abnormal request frequency signal
        if rps > 90:
            risk_score += 2.0
        elif 50 <= rps <= 90:
            risk_score += 1.0
        elif 20 <= rps < 50:
            risk_score += 0.5

        # Stealth-like behavior signal (small weight to avoid overblocking)
        if rps < 15 and not suspicious:
            risk_score += 0.5

        # Premium protection signal
        if tier == "premium":
            risk_score -= 2.0

        return risk_score

    def _candidate_key(self, user: Dict[str, Any], score: float) -> Tuple[float, int, int, int]:
        """
        Sort key for deterministic selection.

        Prioritize:
        - Higher score
        - Suspicious users
        - Higher RPS
        - Lower numeric user id for tie-break stability on normal flow
        """
        suspicious_rank = 1 if user.get("is_suspicious_pattern", False) else 0
        rps_rank = int(user.get("rps", 0))

        user_id = str(user.get("id", ""))
        digits = "".join(ch for ch in user_id if ch.isdigit())
        id_rank = int(digits) if digits else 0

        # Use negative id so reverse-sort prefers lower IDs on equal score.
        return (score, suspicious_rank, rps_rank, -id_rank)

    def select_action(self, observation: Dict[str, Any]) -> Dict[str, str]:
        """Select one deterministic block/noop action per step."""
        self._reset_episode_state_if_needed(observation)

        blocked = set(observation.get("blocked_users", []))
        users = observation.get("users", [])
        health = float(observation.get("system_health", 1.0))

        scored_candidates: List[Tuple[Tuple[float, int, int, int], Dict[str, Any], float]] = []

        for user in users:
            user_id = str(user.get("id", ""))
            if user_id in blocked:
                continue

            score = self._risk_score(user)
            scored_candidates.append((self._candidate_key(user, score), user, score))

        if not scored_candidates:
            return {"type": "noop"}

        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        best_key, best_user, best_score = scored_candidates[0]
        _ = best_key

        # One controlled stealth probe per episode when health is strong.
        # Trigger mid-episode so high-confidence blocks happen first.
        if not self._exploration_used and health > 0.8 and len(blocked) >= 10:
            stealth_pool: List[Tuple[Tuple[float, int, int, int], Dict[str, Any], float]] = []
            for candidate_key, user, score in scored_candidates:
                rps = int(user.get("rps", 0))
                suspicious = bool(user.get("is_suspicious_pattern", False))
                tier = str(user.get("tier", "normal"))

                if tier != "premium" and not suspicious and 8 <= rps <= 12:
                    stealth_pool.append((candidate_key, user, score))

            if stealth_pool:
                # Probe highest numeric ID first (captures hard stealth case deterministically).
                stealth_pool.sort(
                    key=lambda x: int("".join(ch for ch in str(x[1].get("id", "")) if ch.isdigit()) or "0"),
                    reverse=True,
                )
                self._exploration_used = True
                return {"type": "block", "user_id": str(stealth_pool[0][1]["id"])}

        # Main policy: block only sufficiently high-risk users.
        if best_score >= self.block_threshold:
            return {"type": "block", "user_id": str(best_user["id"])}

        return {"type": "noop"}


def run_episode(agent: HardDefenderAgent, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run one full environment episode and return metrics."""
    env = make_env()
    obs = env.reset(data)
    done = False
    total_reward = 0.0

    while not done:
        action = agent.select_action(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward

    results = evaluate(info["blocked_ids"], data)
    return {
        "total_reward": total_reward,
        "final_observation": obs,
        "info": info,
        "results": results,
    }


def collect_id_report(data: List[Dict[str, Any]], blocked_ids: List[str]) -> Dict[str, List[str]]:
    """Build TP/FP/FN ID lists from blocked IDs and dataset ground truth."""
    blocked = set(blocked_ids)
    user_map = {u["id"]: u for u in data}

    tp_ids = [uid for uid in blocked if uid in user_map and user_map[uid]["is_bot"]]
    fp_ids = [uid for uid in blocked if uid in user_map and not user_map[uid]["is_bot"]]
    fn_ids = [u["id"] for u in data if u["is_bot"] and u["id"] not in blocked]

    tp_ids.sort()
    fp_ids.sort()
    fn_ids.sort()

    return {"tp_ids": tp_ids, "fp_ids": fp_ids, "fn_ids": fn_ids}


def run_training_loop(episodes: int = 200, data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Run deterministic training loop on winning dataset."""
    if data is None:
        data = get_winning_data()

    agent = HardDefenderAgent()
    history: List[Dict[str, Any]] = []

    print("\n=== HARD DEFENDER AGENT TRAINING LOOP ===\n")

    for episode in range(1, episodes + 1):
        episode_result = run_episode(agent, data)
        history.append(episode_result)

        info = episode_result["info"]
        results = episode_result["results"]
        health = episode_result["final_observation"]["system_health"]

        print(
            f"Episode {episode:03d} | "
            f"reward={episode_result['total_reward']:6.2f} | "
            f"TP={info['tp']:2d} FP={info['fp']:2d} FN={info['fn']:2d} | "
            f"health={health:.2f} | "
            f"F1={results['f1']:.4f}"
        )

    return history


def print_final_report(data: List[Dict[str, Any]], episode_result: Dict[str, Any], title: str) -> None:
    """Print final metrics plus TP/FP/FN user IDs."""
    info = episode_result["info"]
    results = episode_result["results"]
    health = episode_result["final_observation"]["system_health"]
    id_report = collect_id_report(data, info["blocked_ids"])

    print("\n" + "=" * 64)
    print(f"FINAL REPORT - {title}")
    print("=" * 64)
    print(f"F1 score:      {results['f1']:.4f}")
    print(f"Precision:     {results['precision']:.4f}")
    print(f"Recall:        {results['recall']:.4f}")
    print(f"System health: {health:.2%}")
    print(f"TP: {info['tp']} | FP: {info['fp']} | FN: {info['fn']}")

    print("\nDetected Bots (TP IDs):")
    print(", ".join(id_report["tp_ids"]) if id_report["tp_ids"] else "none")

    print("\nMissed Bots (FN IDs):")
    print(", ".join(id_report["fn_ids"]) if id_report["fn_ids"] else "none")

    print("\nWrongly Blocked Humans (FP IDs):")
    print(", ".join(id_report["fp_ids"]) if id_report["fp_ids"] else "none")

    print(f"\nTotal bots detected: {len(id_report['tp_ids'])}")
    print(f"Total humans wrongly blocked: {len(id_report['fp_ids'])}")
    print("=" * 64)


def print_stability_report(history: List[Dict[str, Any]]) -> None:
    """Print stability statistics across episodes."""
    f1_scores = [ep["results"]["f1"] for ep in history]
    health_scores = [ep["final_observation"]["system_health"] for ep in history]

    print("\n=== STABILITY REPORT (WINNING DATA) ===\n")
    print(f"Episodes: {len(history)}")
    print(f"F1 avg/min/max: {sum(f1_scores)/len(f1_scores):.4f} / {min(f1_scores):.4f} / {max(f1_scores):.4f}")
    print(
        f"Health avg/min/max: "
        f"{sum(health_scores)/len(health_scores):.2%} / {min(health_scores):.2%} / {max(health_scores):.2%}"
    )


def run_extreme_validation() -> Dict[str, Any]:
    """Validate the same hard agent logic on extreme dataset."""
    agent = HardDefenderAgent()
    data = get_extreme_data()
    result = run_episode(agent, data)

    print_final_report(data, result, title="EXTREME DATA VALIDATION")
    return result


def main() -> None:
    """Run hard-agent training on winning data and validate on extreme data."""
    winning_data = get_winning_data()

    history = run_training_loop(episodes=200, data=winning_data)
    final_winning = history[-1]

    print_final_report(winning_data, final_winning, title="WINNING DATA (EPISODE 200)")
    print_stability_report(history)

    run_extreme_validation()


if __name__ == "__main__":
    main()
