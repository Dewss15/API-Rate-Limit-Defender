"""
quick_test.py - Quick smoke test for OpenEnv compliance

Run this for a fast check before full validation.
"""

import json
import sys


def quick_test():
    """Run quick smoke tests."""
    print("🚀 Quick OpenEnv Smoke Test\n")
    
    passed = 0
    failed = 0
    
    # Test 1: Imports
    print("1️⃣  Testing imports...")
    try:
        from environment import make_env
        from data import get_easy_data
        from grader import Grader
        from inference import HeuristicAgent
        from openenv_models import Observation, Action
        print("   ✅ All imports successful\n")
        passed += 1
    except Exception as e:
        print(f"   ❌ Import failed: {e}\n")
        failed += 1
        return
    
    # Test 2: Environment
    print("2️⃣  Testing environment...")
    try:
        env = make_env()
        data = get_easy_data()
        obs = env.reset(data)
        
        if "is_bot" in obs["users"][0]:
            print("   ❌ CRITICAL: is_bot exposed!\n")
            failed += 1
        else:
            print("   ✅ is_bot hidden correctly")
            
        action = {"type": "block", "user_id": obs["users"][0]["id"]}
        obs2, reward, done, info = env.step(action)
        print(f"   ✅ step() works (reward: {reward})\n")
        passed += 1
    except Exception as e:
        print(f"   ❌ Environment test failed: {e}\n")
        failed += 1
    
    # Test 3: Grader
    print("3️⃣  Testing grader...")
    try:
        grader = Grader()
        data = get_easy_data()
        blocked = [u["id"] for u in data if u["rps"] > 100]
        result = grader.grade(blocked, data)
        
        print(f"   ✅ Grader works")
        print(f"      Score: {result['score']:.4f}")
        print(f"      F1: {result['f1']:.4f}\n")
        passed += 1
    except Exception as e:
        print(f"   ❌ Grader test failed: {e}\n")
        failed += 1
    
    # Test 4: Agent
    print("4️⃣  Testing agent...")
    try:
        agent = HeuristicAgent()
        obs = {"users": [{"id": "U1", "rps": 100, "is_suspicious_pattern": True, "tier": "normal"}],
               "blocked_users": [], "system_health": 1.0}
        action = agent.select_action(obs)
        print(f"   ✅ Agent works")
        print(f"      Action: {action}\n")
        passed += 1
    except Exception as e:
        print(f"   ❌ Agent test failed: {e}\n")
        failed += 1
    
    # Test 5: JSON Logging
    print("5️⃣  Testing JSON logging...")
    try:
        test_log = {"event": "STEP", "step": 1, "action": {"type": "block", "user_id": "U1"}, "reward": 0.4, "done": False}
        json_str = json.dumps(test_log)
        parsed = json.loads(json_str)
        print(f"   ✅ JSON serialization works")
        print(f"      Log: {json_str[:60]}...\n")
        passed += 1
    except Exception as e:
        print(f"   ❌ JSON test failed: {e}\n")
        failed += 1
    
    # Summary
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\n✅ Basic smoke tests passed!")
        print("   Run 'python validate_openenv.py' for full validation")
        return 0
    else:
        print("\n❌ Some tests failed!")
        print("   Fix errors before running full validation")
        return 1


if __name__ == "__main__":
    sys.exit(quick_test())
