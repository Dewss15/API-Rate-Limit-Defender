"""
validate_openenv.py - OpenEnv Compliance Validation Script

Run this before submission to ensure all requirements are met.
"""

import os
import sys
import json
import yaml
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if required file exists."""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists


def validate_openenv_yaml():
    """Validate openenv.yaml structure."""
    print("\n=== Validating openenv.yaml ===")
    
    try:
        with open("openenv.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        required_fields = ["name", "version", "description", "tasks"]
        for field in required_fields:
            if field in config:
                print(f"✅ {field}: {config.get(field)[:50] if isinstance(config.get(field), str) else config.get(field)}")
            else:
                print(f"❌ Missing field: {field}")
                return False
        
        # Validate tasks
        tasks = config.get("tasks", {})
        required_tasks = ["easy-triage", "behavioral-analysis", "adversarial-defense"]
        
        for task in required_tasks:
            if task in tasks:
                task_config = tasks[task]
                if "description" in task_config and "expected_difficulty" in task_config:
                    print(f"✅ Task: {task} ({task_config['expected_difficulty']})")
                else:
                    print(f"❌ Task {task} missing required fields")
                    return False
            else:
                print(f"❌ Missing task: {task}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating openenv.yaml: {e}")
        return False


def validate_grader():
    """Validate grader matches evaluator.py."""
    print("\n=== Validating Grader ===")
    
    try:
        from grader import Grader
        from data import get_easy_data
        
        grader = Grader()
        data = get_easy_data()
        
        # Test with sample blocking
        blocked = [u["id"] for u in data if u["rps"] > 100]
        result = grader.grade(blocked, data)
        
        print(f"✅ Grader runs successfully")
        print(f"   Score: {result['score']:.4f}")
        print(f"   F1: {result['f1']:.4f}")
        
        # Validate against evaluator
        if grader.validate_against_evaluator(blocked, data):
            print(f"✅ Grader matches evaluator.py EXACTLY")
            return True
        else:
            print(f"❌ Grader does NOT match evaluator.py")
            return False
        
    except Exception as e:
        print(f"❌ Grader validation failed: {e}")
        return False


def validate_inference():
    """Validate inference.py can run."""
    print("\n=== Validating Inference ===")
    
    try:
        # Test imports
        from inference import HeuristicAgent, run_task
        from grader import Grader
        from data import get_easy_data
        
        print(f"✅ Imports successful")
        
        # Test heuristic agent
        agent = HeuristicAgent(rps_threshold=50)
        grader = Grader()
        
        print(f"✅ Agent and grader initialized")
        
        # Quick test run (just first few steps)
        from environment import make_env
        env = make_env()
        data = get_easy_data()
        obs = env.reset(data)
        
        action = agent.select_action(obs)
        obs, reward, done, info = env.step(action)
        
        print(f"✅ Environment step successful")
        print(f"   Action: {action}")
        print(f"   Reward: {reward}")
        
        return True
        
    except Exception as e:
        print(f"❌ Inference validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_models():
    """Validate Pydantic models."""
    print("\n=== Validating Models ===")
    
    try:
        from openenv_models import (
            UserObservation, Observation, Action, 
            Reward, StepResult, TaskMetadata
        )
        
        # Test UserObservation
        user = UserObservation(
            id="U1",
            rps=50,
            is_suspicious_pattern=True,
            tier="normal"
        )
        print(f"✅ UserObservation: {user.id}")
        
        # Test Observation
        obs = Observation(
            users=[user],
            blocked_users=[],
            system_health=1.0
        )
        print(f"✅ Observation: {len(obs.users)} users")
        
        # Test Action
        action = Action(type="block", user_id="U1")
        print(f"✅ Action: {action.type}")
        
        # Test Reward
        reward = Reward(reward=0.4)
        print(f"✅ Reward: {reward.reward}")
        
        return True
        
    except Exception as e:
        print(f"❌ Models validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_environment():
    """Validate environment compatibility."""
    print("\n=== Validating Environment ===")
    
    try:
        from environment import make_env
        from data import get_easy_data
        
        env = make_env()
        data = get_easy_data()
        
        # Test reset
        obs = env.reset(data)
        print(f"✅ reset() works")
        
        # Verify is_bot is hidden
        if "is_bot" in obs["users"][0]:
            print(f"❌ CRITICAL: is_bot is exposed in observation!")
            return False
        else:
            print(f"✅ is_bot is hidden from observation")
        
        # Test step
        action = {"type": "block", "user_id": obs["users"][0]["id"]}
        obs2, reward, done, info = env.step(action)
        print(f"✅ step() works")
        
        # Verify info structure
        required_info = ["tp", "fp", "fn", "tn", "premium_penalty", "blocked_ids"]
        for field in required_info:
            if field not in info:
                print(f"❌ Missing info field: {field}")
                return False
        print(f"✅ Info dict structure correct")
        
        # Test system_health formula
        total_users = len(data)
        expected_health = max(0, 1 - ((info["fn"] + info["fp"]) / total_users))
        if abs(obs2["system_health"] - expected_health) < 1e-6:
            print(f"✅ System health formula correct")
        else:
            print(f"❌ System health formula mismatch")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("🚀 OpenEnv Compliance Validation")
    print("=" * 60)
    
    # Check required files
    print("\n=== Checking Required Files ===")
    required_files = [
        "openenv.yaml",
        "openenv_models.py",
        "grader.py",
        "inference.py",
        "requirements.txt",
        "Dockerfile",
        "environment.py",
        "models.py",
        "data.py",
        "evaluator.py"
    ]
    
    files_ok = all(check_file_exists(f) for f in required_files)
    
    if not files_ok:
        print("\n❌ Missing required files!")
        sys.exit(1)
    
    # Run validation checks
    checks = [
        ("OpenEnv YAML", validate_openenv_yaml),
        ("Pydantic Models", validate_models),
        ("Environment", validate_environment),
        ("Grader", validate_grader),
        ("Inference", validate_inference),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} validation crashed: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✅ ALL CHECKS PASSED - READY FOR SUBMISSION!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test inference: python inference.py")
        print("2. Build Docker: docker build -t api-defender .")
        print("3. Run container: docker run api-defender")
        print("4. Submit to hackathon/OpenEnv")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ VALIDATION FAILED - FIX ERRORS BEFORE SUBMISSION")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
