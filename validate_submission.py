"""
validate_submission.py - Validate all submission files work correctly

Checks:
1. All required files exist
2. Files can be imported without errors
3. HardDefenderAgent works with main.py
4. Basic functionality test
"""

import sys
import os
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if file exists and return True/False"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {filepath}")
    return exists


def test_imports():
    """Test that all files can be imported"""
    print("\n" + "="*80)
    print("TESTING IMPORTS")
    print("="*80)
    
    try:
        print("\n📦 Importing core modules...")
        from environment import APIRateLimitDefenderEnv, make_env
        print("  ✅ environment.py")
        
        from models import User
        print("  ✅ models.py")
        
        from data import get_easy_data, get_medium_data, get_extreme_data, get_winning_data
        print("  ✅ data.py")
        
        from evaluator import evaluate
        print("  ✅ evaluator.py")
        
        from grader import Grader
        print("  ✅ grader.py")
        
        from hard_defender_agent import HardDefenderAgent
        print("  ✅ hard_defender_agent.py")
        
        from openenv_models import Action, Observation, UserObservation
        print("  ✅ openenv_models.py")
        
        import main
        print("  ✅ main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_compatibility():
    """Test that HardDefenderAgent works with main.py"""
    print("\n" + "="*80)
    print("TESTING AGENT COMPATIBILITY")
    print("="*80)
    
    try:
        from hard_defender_agent import HardDefenderAgent
        from data import get_easy_data
        
        # Create agent
        agent = HardDefenderAgent(block_threshold=2.5)
        print("\n  ✅ Agent created successfully")
        
        # Check required methods
        assert hasattr(agent, 'select_action'), "Missing select_action method"
        print("  ✅ Has select_action method")
        
        assert hasattr(agent, 'get_name'), "Missing get_name method"
        print("  ✅ Has get_name method")
        
        assert hasattr(agent, 'reset'), "Missing reset method"
        print("  ✅ Has reset method")
        
        # Test get_name
        name = agent.get_name()
        print(f"  ✅ Agent name: {name}")
        
        # Test reset
        agent.reset()
        print("  ✅ Reset works")
        
        # Test select_action
        dataset = get_easy_data()
        from environment import make_env
        env = make_env()
        obs = env.reset(dataset)
        
        action = agent.select_action(obs)
        print(f"  ✅ select_action returns: {action}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ COMPATIBILITY ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Run a quick episode to verify everything works"""
    print("\n" + "="*80)
    print("TESTING BASIC FUNCTIONALITY")
    print("="*80)
    
    try:
        from hard_defender_agent import HardDefenderAgent
        from environment import make_env
        from grader import Grader
        from data import get_easy_data
        
        # Setup
        agent = HardDefenderAgent(block_threshold=2.5)
        env = make_env()
        dataset = get_easy_data()
        grader = Grader()
        
        print(f"\n  📊 Dataset: {len(dataset)} users")
        
        # Run episode
        obs = env.reset(dataset)
        blocked = []
        done = False
        steps = 0
        
        while not done and steps < 20:
            action = agent.select_action(obs)
            obs, reward, done, info = env.step(action)
            
            if action.get("type") == "block":
                user_id = action.get("user_id")
                if user_id and user_id not in blocked:
                    blocked.append(user_id)
            
            steps += 1
        
        # Grade
        results = grader.grade(blocked, dataset)
        
        print(f"\n  📈 Results:")
        print(f"     Steps:          {steps}")
        print(f"     Blocked:        {len(blocked)} users")
        print(f"     F1 Score:       {results['f1']:.3f}")
        print(f"     Precision:      {results['precision']:.3f}")
        print(f"     Recall:         {results['recall']:.3f}")
        print(f"     Premium Penalty: {results['premium_penalty']}")
        
        # Validate
        assert results['f1'] >= 0.90, f"F1 too low: {results['f1']}"
        print("  ✅ F1 >= 0.90")
        
        assert results['premium_penalty'] == 0, f"Premium penalty: {results['premium_penalty']}"
        print("  ✅ No premium violations")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FUNCTIONALITY ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("="*80)
    print("SUBMISSION FILES VALIDATION")
    print("="*80)
    
    # Check required files
    print("\n" + "="*80)
    print("CHECKING REQUIRED FILES")
    print("="*80)
    
    required_files = [
        "environment.py",
        "models.py",
        "data.py",
        "evaluator.py",
        "grader.py",
        "hard_defender_agent.py",
        "main.py",
        "openenv.yaml",
        "openenv_models.py",
    ]
    
    print("\n📁 Core files:")
    all_exist = all(check_file_exists(f) for f in required_files)
    
    if not all_exist:
        print("\n❌ FAILED: Some required files are missing!")
        return 1
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Agent Compatibility", test_agent_compatibility),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        passed = test_func()
        results.append((test_name, passed))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("="*80)
        print("\nYour submission files are working correctly!")
        print("\nNext steps:")
        print("  1. Run: prepare_submission.bat")
        print("  2. Zip the submission folder")
        print("  3. Submit to hackathon platform")
        return 0
    else:
        print("❌ SOME VALIDATION TESTS FAILED!")
        print("="*80)
        print("\nPlease fix the errors above before submitting.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
