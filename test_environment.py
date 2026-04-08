"""
test_environment.py - Comprehensive test suite for API Rate Limit Defender Environment

Tests the environment against the evaluator to ensure metrics align correctly.
"""

from data import get_easy_data, get_medium_data, get_extreme_data, get_winning_data
from evaluator import evaluate
from environment import make_env
from models import User


def test_environment_basic():
    """Test basic environment functionality."""
    print("\n=== [TEST] TEST 1: Basic Environment Setup ===")
    
    env = make_env()
    data = get_easy_data()
    
    # Reset environment
    obs = env.reset(data)
    
    # Verify observation structure
    assert "users" in obs, "Observation missing 'users'"
    assert "blocked_users" in obs, "Observation missing 'blocked_users'"
    assert "system_health" in obs, "Observation missing 'system_health'"
    
    # Verify is_bot is hidden
    assert "is_bot" not in obs["users"][0], "[FAIL] CRITICAL: is_bot is exposed to agent!"
    
    # Verify visible fields
    assert "id" in obs["users"][0]
    assert "rps" in obs["users"][0]
    assert "is_suspicious_pattern" in obs["users"][0]
    assert "tier" in obs["users"][0]
    
    print("[PASS] Environment structure correct")
    print(f"[PASS] is_bot hidden from agent observations")
    print(f"[PASS] Initial state: {len(obs['users'])} users, health={obs['system_health']}")


def test_environment_rewards():
    """Test reward calculation."""
    print("\n=== [TEST] TEST 2: Reward Calculation ===")
    
    env = make_env()
    data = [
        {"id": "bot1", "rps": 100, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "human1", "rps": 10, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "premium1", "rps": 20, "is_suspicious_pattern": False, "tier": "premium", "is_bot": False},
    ]
    
    env.reset(data)
    
    # Test blocking a bot (should get +0.4 + health bonus)
    obs, reward, done, info = env.step({"type": "block", "user_id": "bot1"})
    assert reward > 0, f"[FAIL] Blocking bot should give positive reward, got {reward}"
    assert info["tp"] == 1, f"[FAIL] Expected TP=1, got {info['tp']}"
    print(f"[PASS] Block bot: reward={reward:.2f}, TP={info['tp']}")
    
    # Test blocking a human (should get -0.5)
    obs, reward, done, info = env.step({"type": "block", "user_id": "human1"})
    assert reward < 0, f"[FAIL] Blocking human should give negative reward, got {reward}"
    assert info["fp"] == 1, f"[FAIL] Expected FP=1, got {info['fp']}"
    print(f"[PASS] Block human: reward={reward:.2f}, FP={info['fp']}")
    
    # Test blocking premium (should track penalty)
    obs, reward, done, info = env.step({"type": "block", "user_id": "premium1"})
    assert info["premium_penalty"] == 1, f"[FAIL] Expected premium_penalty=1, got {info['premium_penalty']}"
    print(f"[PASS] Block premium: premium_penalty={info['premium_penalty']}")
    
    # Test invalid action
    obs, reward, done, info = env.step({"type": "block", "user_id": "invalid_user"})
    assert reward == -0.1, f"[FAIL] Invalid user should give -0.1, got {reward}"
    print(f"[PASS] Invalid user: reward={reward}")
    
    # Test already blocked
    env.reset(data)
    env.step({"type": "block", "user_id": "bot1"})
    obs, reward, done, info = env.step({"type": "block", "user_id": "bot1"})
    assert reward == -0.1, f"[FAIL] Already blocked should give -0.1, got {reward}"
    print(f"[PASS] Already blocked: reward={reward}")


def test_metrics_alignment():
    """Test that environment metrics match evaluator metrics."""
    print("\n=== [TEST] TEST 3: Metrics Alignment with Evaluator ===")
    
    env = make_env()
    data = get_medium_data()
    
    env.reset(data)
    
    # Simulate blocking some users
    blocked_ids = []
    for user in data:
        # Simple heuristic: block high RPS with suspicious pattern
        if user["rps"] > 30 and user["is_suspicious_pattern"]:
            env.step({"type": "block", "user_id": user["id"]})
            blocked_ids.append(user["id"])
    
    # Get final metrics from environment
    obs, reward, done, info = env.step({"type": "block", "user_id": "dummy"})  # Dummy step to get final state
    
    # Get metrics from evaluator
    eval_results = evaluate(blocked_ids, data)
    
    # Compare metrics
    print(f"\n[REPORT] Comparing Environment vs Evaluator:")
    print(f"   TP: {info['tp']} vs {eval_results['TP']} {'[PASS]' if info['tp'] == eval_results['TP'] else '[FAIL]'}")
    print(f"   FP: {info['fp']} vs {eval_results['FP']} {'[PASS]' if info['fp'] == eval_results['FP'] else '[FAIL]'}")
    print(f"   FN: {info['fn']} vs {eval_results['FN']} {'[PASS]' if info['fn'] == eval_results['FN'] else '[FAIL]'}")
    print(f"   System Health: {obs['system_health']:.4f} vs {eval_results['system_health']:.4f}")
    
    assert info['tp'] == eval_results['TP'], "[FAIL] TP mismatch!"
    assert info['fp'] == eval_results['FP'], "[FAIL] FP mismatch!"
    assert info['fn'] == eval_results['FN'], "[FAIL] FN mismatch!"
    
    print(f"\n[PASS] All metrics align with evaluator!")


def test_simple_agent():
    """Test a simple agent using the environment."""
    print("\n=== [TEST] TEST 4: Simple Agent Execution ===")
    
    env = make_env()
    data = get_winning_data()
    
    obs = env.reset(data)
    print(f"Starting with {len(obs['users'])} users, health={obs['system_health']:.2f}")
    
    done = False
    step_count = 0
    total_reward = 0
    
    # Simple agent: block users with high RPS AND suspicious pattern (avoid premium)
    while not done:
        step_count += 1
        
        # Find a user to block based on heuristic
        action = None
        for user in obs["users"]:
            if user["id"] not in obs["blocked_users"]:
                # Skip premium users
                if user["tier"] == "premium":
                    continue
                
                # Block if high RPS or suspicious
                if user["rps"] > 30 or user["is_suspicious_pattern"]:
                    action = {"type": "block", "user_id": user["id"]}
                    break
        
        # If no action found, do a dummy action to advance
        if action is None:
            action = {"type": "block", "user_id": "dummy"}
        
        obs, reward, done, info = env.step(action)
        total_reward += reward
        
        if step_count % 5 == 0:
            print(f"  Step {step_count}: Health={obs['system_health']:.2f}, "
                  f"Blocked={len(obs['blocked_users'])}, "
                  f"TP={info['tp']}, FP={info['fp']}, FN={info['fn']}")
        
        if done:
            break
    
    print(f"\n[REPORT] Episode Complete:")
    print(f"   Total Steps: {step_count}")
    print(f"   Total Reward: {total_reward:.2f}")
    print(f"   Final Health: {obs['system_health']:.2f}")
    print(f"   TP: {info['tp']} | FP: {info['fp']} | FN: {info['fn']} | TN: {info['tn']}")
    print(f"   Premium Penalties: {info['premium_penalty']}")
    
    # Compare with evaluator
    eval_results = evaluate(info['blocked_ids'], data)
    print(f"\n[REPORT] Evaluator Score: {eval_results['score']:.4f}")
    print(f"   F1: {eval_results['f1']:.4f}")
    print(f"   Precision: {eval_results['precision']:.4f}")
    print(f"   Recall: {eval_results['recall']:.4f}")
    
    print(f"\n[PASS] Agent ran successfully!")


def test_system_health_calculation():
    """Test system health calculation formula."""
    print("\n=== [TEST] TEST 5: System Health Calculation ===")
    
    env = make_env()
    data = [
        {"id": "bot1", "rps": 100, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "bot2", "rps": 100, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "human1", "rps": 10, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
        {"id": "human2", "rps": 10, "is_suspicious_pattern": False, "tier": "normal", "is_bot": False},
    ]
    
    env.reset(data)
    
    # Block 1 bot (1 TP, 0 FP, 1 FN, 2 TN)
    obs, reward, done, info = env.step({"type": "block", "user_id": "bot1"})
    expected_health = max(0, 1 - ((info['fn'] + info['fp']) / 4))
    assert abs(obs['system_health'] - expected_health) < 0.001, \
        f"[FAIL] System health mismatch: {obs['system_health']:.4f} vs {expected_health:.4f}"
    print(f"[PASS] After blocking 1 bot: Health={obs['system_health']:.4f} (FN={info['fn']}, FP={info['fp']})")
    
    # Block 1 human (1 TP, 1 FP, 1 FN, 1 TN)
    obs, reward, done, info = env.step({"type": "block", "user_id": "human1"})
    expected_health = max(0, 1 - ((info['fn'] + info['fp']) / 4))
    assert abs(obs['system_health'] - expected_health) < 0.001, \
        f"[FAIL] System health mismatch: {obs['system_health']:.4f} vs {expected_health:.4f}"
    print(f"[PASS] After blocking 1 human: Health={obs['system_health']:.4f} (FN={info['fn']}, FP={info['fp']})")
    
    # Block remaining bot (2 TP, 1 FP, 0 FN, 1 TN)
    obs, reward, done, info = env.step({"type": "block", "user_id": "bot2"})
    expected_health = max(0, 1 - ((info['fn'] + info['fp']) / 4))
    assert abs(obs['system_health'] - expected_health) < 0.001, \
        f"[FAIL] System health mismatch: {obs['system_health']:.4f} vs {expected_health:.4f}"
    print(f"[PASS] After blocking 2nd bot: Health={obs['system_health']:.4f} (FN={info['fn']}, FP={info['fp']})")
    
    print(f"\n[PASS] System health formula verified!")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("[LAUNCH] API RATE LIMIT DEFENDER - ENVIRONMENT TEST SUITE")
    print("=" * 60)
    
    try:
        test_environment_basic()
        test_environment_rewards()
        test_metrics_alignment()
        test_system_health_calculation()
        test_simple_agent()
        
        print("\n" + "=" * 60)
        print("[PASS] ALL TESTS PASSED! Environment is ready for use.")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
