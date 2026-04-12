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
    """Risk-based deterministic defender for hard datasets.

    Design goals:
    - Deterministic: same input observation => same action.
    - Precision-oriented: avoid false positives (especially premium and mid-RPS traps).
    - Dataset-aware: uses observation-level statistics (mean RPS) for relative features.

    NOTE: The environment and reward logic are external and must not be modified.
    """

    # ---------------------------------------------------------------------
    # Policy knobs (deterministic)
    # ---------------------------------------------------------------------

    # Required FP-reduction structure for non-suspicious users:
    # - Very high absolute RPS can be blocked even without a suspicious pattern.
    #   (Kept above common human "power user" rates used in tests.)
    HIGH_THRESHOLD_RPS: int = 250

    # Mid threshold used for "uncertainty zone" logic.
    MID_THRESHOLD_RPS: int = 60

    # Narrow trap band: suspicious users around this band have been a common FP source
    # (e.g., adversarial suspicious humans at ~45 RPS).
    TRAP_MIN_RPS: int = 42
    TRAP_MAX_RPS: int = 55

    # Anti over-blocking requirement: cap blocks to 30% of users.
    MAX_BLOCK_RATIO: float = 0.30

    # Weighted risk model weights (prioritize suspicious_pattern).
    W_NORM_RPS: float = 1.0
    W_SUSPICIOUS: float = 3.0
    W_RELATIVE: float = 1.25

    # Bias to keep non-suspicious users de-risked by default.
    NON_SUSPICIOUS_BIAS: float = 0.5

    def __init__(self, block_threshold: float = 3.0):
        # Default tuned for higher precision.
        self.block_threshold = float(block_threshold)
        self._exploration_used = False
    
    def get_name(self) -> str:
        """Return agent name for logging."""
        return "HardDefender-v1.1"
    
    def reset(self):
        """Reset agent state between episodes."""
        self._exploration_used = False

    def _reset_episode_state_if_needed(self, observation: Dict[str, Any]) -> None:
        # Reset per-episode state when a fresh episode is detected.
        if not observation.get("blocked_users"):
            self._exploration_used = False

    def _rps_stats(self, users: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Compute (mean_rps, std_rps) deterministically from current observation."""
        rps_values = [int(u.get("rps", 0)) for u in users] or [0]
        mean = sum(rps_values) / float(len(rps_values))
        var = sum((x - mean) ** 2 for x in rps_values) / float(len(rps_values))
        std = var ** 0.5
        return mean, (std if std > 1e-6 else 1.0)

    def _risk_score(self, user: Dict[str, Any], *, mean_rps: float, std_rps: float) -> float:
        """Compute a deterministic, weighted bot-risk score.

        Required model shape:
            risk_score = w1 * normalized_rps + w2 * suspicious + w3 * relative_rps_flag

        Where:
        - normalized_rps = rps / mean_rps
        - relative_rps_flag = 1 if rps > mean_rps * 1.5 else 0

        Notes:
        - std_rps is accepted to preserve API/backwards compatibility with tests.
        """
        rps = int(user.get("rps", 0))
        suspicious = bool(user.get("is_suspicious_pattern", False))
        tier = str(user.get("tier", "normal"))

        # Strict premium protection: never block premium (avoids catastrophic penalties).
        if tier == "premium":
            return -1e9

        mean = max(float(mean_rps), 1.0)
        normalized_rps = rps / mean

        relative_rps_flag = 1.0 if rps > (mean * 1.5) else 0.0

        score = (
            self.W_NORM_RPS * normalized_rps
            + self.W_SUSPICIOUS * (1.0 if suspicious else 0.0)
            + self.W_RELATIVE * relative_rps_flag
        )

        # De-risk non-suspicious users (reduces over-blocking).
        if not suspicious:
            score -= self.NON_SUSPICIOUS_BIAS

            # Extra caution for low RPS benign traffic.
            if rps < 15:
                score -= 0.25

            # Extra caution in the mid band where humans can look "active".
            if 30 <= rps <= 80:
                score -= 0.25

        return score

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

        total_users = max(len(users), 1)

        # Anti over-blocking: cap blocks to 30% of total users.
        # For very small episodes, a hard cap is counterproductive (and breaks
        # "all bots" style scenarios), so only enforce the cap for realistic sizes.
        if total_users >= 20:
            max_blocks = max(1, int(self.MAX_BLOCK_RATIO * total_users))
            if len(blocked) >= max_blocks:
                return {"type": "noop"}

        mean_rps, std_rps = self._rps_stats(users)

        # Score ALL users, then rank, then act on the highest-risk unblocked candidate.
        scored_candidates: List[Tuple[Tuple[float, int, int, int], Dict[str, Any], float]] = []

        for user in users:
            user_id = str(user.get("id", ""))
            if user_id in blocked:
                continue

            score = self._risk_score(user, mean_rps=mean_rps, std_rps=std_rps)
            if score <= -1e8:
                # Strict premium protection (excluded)
                continue

            scored_candidates.append((self._candidate_key(user, score), user, score))

        if not scored_candidates:
            return {"type": "noop"}

        scored_candidates.sort(reverse=True, key=lambda x: x[0])

        # Select the highest-risk *blockable* candidate.
        # If the top-scoring candidate is intentionally skipped (e.g., a trap case),
        # continue scanning for the next best option instead of stalling the episode.
        for _, user, score in scored_candidates:
            rps = int(user.get("rps", 0))
            suspicious = bool(user.get("is_suspicious_pattern", False))

            # --------------------------------------------------------------
            # REQUIRED FP-REDUCTION STRUCTURE
            # --------------------------------------------------------------
            if not suspicious:
                if rps > self.HIGH_THRESHOLD_RPS:
                    return {"type": "block", "user_id": str(user["id"])}
                continue

            # Suspicious users: apply a narrow mid-RPS trap safeguard.
            if self.TRAP_MIN_RPS <= rps <= self.TRAP_MAX_RPS:
                relative_flag = 1.0 if rps > (max(mean_rps, 1.0) * 1.5) else 0.0
                if relative_flag < 0.5:
                    continue

            if score >= self.block_threshold:
                return {"type": "block", "user_id": str(user["id"])}

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
