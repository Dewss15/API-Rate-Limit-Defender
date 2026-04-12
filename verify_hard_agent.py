"""
Quick verification: Test HardDefenderAgent on all datasets from data.py
"""

import sys
from hard_defender_agent import HardDefenderAgent
from environment import make_env

# Avoid Windows cp1252 stdout issues in some runners
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from grader import Grader
from data import get_easy_data, get_medium_data, get_extreme_data, get_winning_data


def run_episode(agent, dataset):
    """Run one episode and return blocked user IDs"""
    env = make_env()
    observation = env.reset(dataset)
    blocked = []
    
    for _ in range(20):
        action = agent.select_action(observation)
        if action.get("type") == "block":
            user_id = action.get("user_id")
            if user_id and user_id not in blocked:
                blocked.append(user_id)
        observation, _, done, _ = env.step(action)
        if done:
            break
    
    return blocked


def main():
    print("="*80)
    print("QUICK VERIFICATION: HardDefenderAgent on data.py")
    print("="*80)
    
    agent = HardDefenderAgent(block_threshold=2.5)
    grader = Grader()
    
    datasets = [
        ("Easy", get_easy_data()),
        ("Medium", get_medium_data()),
        ("Extreme", get_extreme_data()),
        ("Winning", get_winning_data()),
    ]
    
    print("\n" + "="*80)
    print("TESTING ON ALL DATASETS")
    print("="*80)
    
    all_pass = True
    
    for name, dataset in datasets:
        print(f"\n{name} Dataset:")
        print(f"   Total users: {len(dataset)}")
        
        # Count composition
        humans = sum(1 for u in dataset if not u['is_bot'])
        bots = sum(1 for u in dataset if u['is_bot'])
        premium = sum(1 for u in dataset if u['tier'] == 'premium')
        
        print(f"   Composition: {humans} humans, {bots} bots, {premium} premium")
        
        # Run agent
        blocked = run_episode(agent, dataset)
        results = grader.grade(blocked, dataset)
        
        # Display results
        print(f"\n   Results:")
        print(f"   ├─ F1 Score:        {results['f1']:.3f}")
        print(f"   ├─ Precision:       {results['precision']:.3f}")
        print(f"   ├─ Recall:          {results['recall']:.3f}")
        print(f"   ├─ Score:           {results['score']:.3f}")
        print(f"   ├─ TP={results['TP']}, FP={results['FP']}, FN={results['FN']}, TN={results['TN']}")
        print(f"   ├─ Blocked:         {len(blocked)} users")
        print(f"   └─ Premium Penalty: {results['premium_penalty']}")
        
        # Check pass/fail
        if name == "Winning":
            threshold = 0.70
            passed = results['f1'] >= threshold and results['premium_penalty'] == 0
            status = "PASS" if passed else "FAIL"
            print(f"\n   Status: {status} (F1 >= {threshold} required)")
            if not passed:
                all_pass = False
        else:
            passed = results['premium_penalty'] == 0
            status = "PASS" if passed else "WARNING"
            print(f"\n   Status: {status} (Premium protection)")
            if not passed:
                all_pass = False
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if all_pass:
        print("\nALL TESTS PASSED!")
        print("\n   Your HardDefenderAgent works correctly on all datasets!")
        print("   Ready for hackathon submission.")
        print("\n   Next steps:")
        print("   1. Run: prepare_submission.bat")
        print("   2. Zip the submission folder")
        print("   3. Submit to hackathon platform")
    else:
        print("\nSOME TESTS FAILED!")
        print("\n   Review the results above and fix any issues.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
