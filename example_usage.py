"""
example_usage.py - Example of using the API Rate Limit Defender Environment

Shows how to integrate with the environment and evaluator.
"""

from data import get_winning_data
from evaluator import evaluate
from environment import make_env


def run_heuristic_agent():
    """
    Run a simple heuristic-based agent (similar to test.py).
    This shows how to use the environment instead of manual blocking.
    """
    print("\n=== 🤖 HEURISTIC AGENT (Environment-Based) ===\n")
    
    # Get data and create environment
    data = get_winning_data()
    env = make_env()
    
    # Reset environment
    obs = env.reset(data)
    
    done = False
    total_reward = 0
    
    # Run episode
    while not done:
        # Find next user to block (same heuristic as test.py)
        action = None
        
        for user in obs["users"]:
            if user["id"] in obs["blocked_users"]:
                continue
            
            # Skip premium users
            if user["tier"] == "premium":
                continue
            
            # Block if high RPS or suspicious pattern
            if user["rps"] > 30 or user["is_suspicious_pattern"]:
                action = {"type": "block", "user_id": user["id"]}
                break
        
        # If no more users to block, send dummy action to finish episode
        if action is None:
            action = {"type": "block", "user_id": "done"}
        
        # Take step
        obs, reward, done, info = env.step(action)
        total_reward += reward
    
    # Print results using evaluator
    results = evaluate(info["blocked_ids"], data)
    
    print("--- 📊 JUDGE'S SCORECARD ---")
    print(f"Final Score:   {results['score']:.4f}")
    print(f"F1 Score:      {results['f1']:.4f}")
    print(f"Precision:     {results['precision']:.4f}")
    print(f"Recall:        {results['recall']:.4f}")
    print(f"System Health: {results['system_health']:.2%}")
    print(f"TP: {results['TP']} | FP: {results['FP']} | FN: {results['FN']}")
    print(f"\n🎮 Episode Reward: {total_reward:.2f}")


def run_smart_agent():
    """
    Run a smarter agent that uses RPS threshold more carefully.
    """
    print("\n=== 🧠 SMART AGENT (Adaptive Threshold) ===\n")
    
    data = get_winning_data()
    env = make_env()
    
    obs = env.reset(data)
    
    done = False
    total_reward = 0
    
    # Calculate RPS statistics to set adaptive threshold
    rps_values = [u["rps"] for u in obs["users"] if u["tier"] != "premium"]
    avg_rps = sum(rps_values) / len(rps_values) if rps_values else 0
    rps_threshold = avg_rps * 2  # Block users with 2x average RPS
    
    print(f"📊 RPS Threshold: {rps_threshold:.1f} (2x average)")
    
    while not done:
        action = None
        
        for user in obs["users"]:
            if user["id"] in obs["blocked_users"]:
                continue
            
            # Never block premium
            if user["tier"] == "premium":
                continue
            
            # Block if:
            # 1. Very high RPS (likely bot)
            # 2. Suspicious pattern + above threshold RPS
            if user["rps"] > rps_threshold or \
               (user["is_suspicious_pattern"] and user["rps"] > 50):
                action = {"type": "block", "user_id": user["id"]}
                break
        
        if action is None:
            action = {"type": "block", "user_id": "done"}
        
        obs, reward, done, info = env.step(action)
        total_reward += reward
    
    results = evaluate(info["blocked_ids"], data)
    
    print("--- 📊 JUDGE'S SCORECARD ---")
    print(f"Final Score:   {results['score']:.4f}")
    print(f"F1 Score:      {results['f1']:.4f}")
    print(f"Precision:     {results['precision']:.4f}")
    print(f"Recall:        {results['recall']:.4f}")
    print(f"System Health: {results['system_health']:.2%}")
    print(f"TP: {results['TP']} | FP: {results['FP']} | FN: {results['FN']}")
    print(f"\n🎮 Episode Reward: {total_reward:.2f}")


def run_conservative_agent():
    """
    Run a conservative agent that only blocks very obvious bots.
    """
    print("\n=== 🛡️ CONSERVATIVE AGENT (High Precision) ===\n")
    
    data = get_winning_data()
    env = make_env()
    
    obs = env.reset(data)
    
    done = False
    total_reward = 0
    
    while not done:
        action = None
        
        for user in obs["users"]:
            if user["id"] in obs["blocked_users"]:
                continue
            
            # Never block premium
            if user["tier"] == "premium":
                continue
            
            # Only block if BOTH conditions are true (very conservative)
            if user["rps"] > 80 and user["is_suspicious_pattern"]:
                action = {"type": "block", "user_id": user["id"]}
                break
        
        if action is None:
            action = {"type": "block", "user_id": "done"}
        
        obs, reward, done, info = env.step(action)
        total_reward += reward
    
    results = evaluate(info["blocked_ids"], data)
    
    print("--- 📊 JUDGE'S SCORECARD ---")
    print(f"Final Score:   {results['score']:.4f}")
    print(f"F1 Score:      {results['f1']:.4f}")
    print(f"Precision:     {results['precision']:.4f}")
    print(f"Recall:        {results['recall']:.4f}")
    print(f"System Health: {results['system_health']:.2%}")
    print(f"TP: {results['TP']} | FP: {results['FP']} | FN: {results['FN']}")
    print(f"\n🎮 Episode Reward: {total_reward:.2f}")


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 API RATE LIMIT DEFENDER - AGENT COMPARISON")
    print("=" * 60)
    
    run_heuristic_agent()
    run_smart_agent()
    run_conservative_agent()
    
    print("\n" + "=" * 60)
    print("💡 Tips for RL Agent (Sakshi):")
    print("   - Agent receives obs WITHOUT is_bot field")
    print("   - Must infer bots from: rps, is_suspicious_pattern, tier")
    print("   - Premium users should rarely be blocked (big penalty)")
    print("   - System health drops with FP and FN")
    print("   - Episode ends at step 20 or health <= 0")
    print("=" * 60)
