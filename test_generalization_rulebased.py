"""
test_generalization_rulebased.py - Generalization Testing for Rule-Based Agents

Tests rule-based agents' ability to generalize to unseen data using:
1. Synthetic users with out-of-distribution RPS values
2. Adversarial examples designed to fool the agent
3. Edge cases and boundary conditions
4. Comparison across all three rule-based agents
"""

import random
import numpy as np
from typing import List, Dict, Any
from environment import make_env
from grader import Grader
from data import get_easy_data, get_medium_data, get_extreme_data, get_winning_data

# Import all rule-based agents
from easy_defender_agent import EasyDefenderAgent
from medium_defender_agent import MediumDefenderAgent
from hard_defender_agent import HardDefenderAgent


# ============================================================================
# Synthetic Data Generation (Same as DQN tests)
# ============================================================================

def generate_synthetic_high_rps_bots(n=20):
    """Generate bots with RPS higher than training data (600+)"""
    return [
        {
            'id': f'SYNTH_BOT_HIGH_{i}',
            'rps': random.randint(700, 1500),  # WAY higher than training (max 600)
            'is_suspicious_pattern': random.choice([True, False]),
            'tier': 'normal',
            'is_bot': True
        }
        for i in range(n)
    ]


def generate_synthetic_low_rps_humans(n=20):
    """Generate humans with RPS lower than training data (0-4)"""
    return [
        {
            'id': f'SYNTH_HUMAN_LOW_{i}',
            'rps': random.randint(0, 4),  # Lower than training (min 5)
            'is_suspicious_pattern': False,
            'tier': random.choice(['normal', 'premium']),
            'is_bot': False
        }
        for i in range(n)
    ]


def generate_synthetic_stealth_bots(n=15):
    """Generate stealth bots with moderate RPS but suspicious patterns"""
    return [
        {
            'id': f'SYNTH_STEALTH_{i}',
            'rps': random.randint(15, 35),  # Moderate RPS
            'is_suspicious_pattern': True,   # But suspicious!
            'tier': 'normal',
            'is_bot': True
        }
        for i in range(n)
    ]


def generate_synthetic_active_humans(n=15):
    """Generate active legitimate users with higher RPS"""
    return [
        {
            'id': f'SYNTH_ACTIVE_{i}',
            'rps': random.randint(60, 120),  # High but legitimate
            'is_suspicious_pattern': False,  # Not suspicious
            'tier': random.choice(['normal', 'premium']),
            'is_bot': False
        }
        for i in range(n)
    ]


def generate_adversarial_examples():
    """Generate tricky edge cases designed to confuse the agent"""
    return [
        # Adversarial 1: Stealth bot (low RPS but suspicious)
        {
            'id': 'ADV_STEALTH_1',
            'rps': 20,
            'is_suspicious_pattern': True,
            'tier': 'normal',
            'is_bot': True
        },
        # Adversarial 2: Active human (high RPS, not suspicious)
        {
            'id': 'ADV_ACTIVE_1',
            'rps': 180,
            'is_suspicious_pattern': False,
            'tier': 'normal',
            'is_bot': False
        },
        # Adversarial 3: Premium bot (should NEVER block)
        {
            'id': 'ADV_PREMIUM_BOT',
            'rps': 500,
            'is_suspicious_pattern': True,
            'tier': 'premium',
            'is_bot': True
        },
        # Adversarial 4: Normal human with suspicious pattern
        {
            'id': 'ADV_FALSE_POS',
            'rps': 45,
            'is_suspicious_pattern': True,
            'tier': 'normal',
            'is_bot': False
        },
        # Adversarial 5: Bot with no suspicious pattern (stealth)
        {
            'id': 'ADV_STEALTH_2',
            'rps': 350,
            'is_suspicious_pattern': False,
            'tier': 'normal',
            'is_bot': True
        },
        # Adversarial 6: Extreme high RPS bot
        {
            'id': 'ADV_EXTREME_HIGH',
            'rps': 2000,
            'is_suspicious_pattern': True,
            'tier': 'normal',
            'is_bot': True
        },
        # Adversarial 7: Zero RPS human
        {
            'id': 'ADV_ZERO_RPS',
            'rps': 0,
            'is_suspicious_pattern': False,
            'tier': 'normal',
            'is_bot': False
        },
        # Adversarial 8: Premium human with high RPS
        {
            'id': 'ADV_PREMIUM_HUMAN',
            'rps': 200,
            'is_suspicious_pattern': True,
            'tier': 'premium',
            'is_bot': False
        },
    ]


def generate_boundary_cases():
    """Generate users at decision boundaries"""
    return [
        # Boundary 1: RPS exactly at typical threshold (50)
        {'id': 'BOUND_RPS_50', 'rps': 50, 'is_suspicious_pattern': False, 'tier': 'normal', 'is_bot': False},
        {'id': 'BOUND_RPS_50_BOT', 'rps': 50, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        
        # Boundary 2: RPS at 100
        {'id': 'BOUND_RPS_100', 'rps': 100, 'is_suspicious_pattern': False, 'tier': 'normal', 'is_bot': False},
        {'id': 'BOUND_RPS_100_BOT', 'rps': 100, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        
        # Boundary 3: Very low RPS
        {'id': 'BOUND_RPS_1', 'rps': 1, 'is_suspicious_pattern': False, 'tier': 'normal', 'is_bot': False},
        {'id': 'BOUND_RPS_5_BOT', 'rps': 5, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        
        # Boundary 4: Training max RPS (600)
        {'id': 'BOUND_RPS_600', 'rps': 600, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        {'id': 'BOUND_RPS_601', 'rps': 601, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
    ]


# ============================================================================
# Rule-Based Agent Execution
# ============================================================================

def run_episode(agent, dataset: List[Dict], max_steps=20):
    """Run one episode with a rule-based agent"""
    env = make_env()
    observation = env.reset(dataset)
    
    blocked_users = []
    done = False
    steps = 0
    
    while not done and steps < max_steps:
        # Get agent's action
        action = agent.select_action(observation)
        
        # Execute action in environment
        observation, reward, done, info = env.step(action)
        
        # Track blocked users
        if action.get("type") == "block":
            user_id = action.get("user_id")
            if user_id and user_id not in blocked_users:
                blocked_users.append(user_id)
        
        steps += 1
    
    return blocked_users


def evaluate_on_dataset(agent, dataset: List[Dict], dataset_name: str):
    """Evaluate rule-based agent on a dataset"""
    grader = Grader()
    
    # Run episode
    blocked_ids = run_episode(agent, dataset)
    
    # Grade results
    results = grader.grade(blocked_ids, dataset)
    
    print(f"\n{dataset_name}:")
    print(f"  F1:        {results['f1']:.3f}")
    print(f"  Precision: {results['precision']:.3f}")
    print(f"  Recall:    {results['recall']:.3f}")
    print(f"  Score:     {results['score']:.3f}")
    print(f"  TP={results['TP']}, FP={results['FP']}, FN={results['FN']}")
    print(f"  Premium Penalty: {results['premium_penalty']}")
    
    return results


# ============================================================================
# MAIN TESTING SUITE
# ============================================================================

def test_agent(agent_name: str, agent):
    """Test a single agent across all generalization tests"""
    
    print("\n" + "="*80)
    print(f"TESTING: {agent_name}")
    print("="*80)
    
    # ========================================================================
    # BASELINE: Test on Known Datasets
    # ========================================================================
    print("\n" + "="*80)
    print("BASELINE: Performance on Known Datasets")
    print("="*80)
    
    baseline_results = {}
    baseline_results['easy'] = evaluate_on_dataset(agent, get_easy_data(), "Easy Dataset (Seen)")
    baseline_results['medium'] = evaluate_on_dataset(agent, get_medium_data(), "Medium Dataset (Seen)")
    baseline_results['extreme'] = evaluate_on_dataset(agent, get_extreme_data(), "Extreme Dataset (UNSEEN)")
    baseline_results['winning'] = evaluate_on_dataset(agent, get_winning_data(), "Winning Dataset (Seen)")
    
    # ========================================================================
    # TEST 1: Synthetic Out-of-Distribution Users
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 1: Synthetic Out-of-Distribution Users")
    print("="*80)
    
    synthetic_dataset = (
        generate_synthetic_high_rps_bots(20) +
        generate_synthetic_low_rps_humans(20) +
        generate_synthetic_stealth_bots(15) +
        generate_synthetic_active_humans(15)
    )
    random.shuffle(synthetic_dataset)
    
    synthetic_results = evaluate_on_dataset(
        agent, synthetic_dataset,
        "Synthetic Dataset (70 users, OUT OF DISTRIBUTION)"
    )
    
    # ========================================================================
    # TEST 2: Adversarial Examples
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 2: Adversarial Examples")
    print("="*80)
    
    adversarial_dataset = generate_adversarial_examples()
    adversarial_results = evaluate_on_dataset(
        agent, adversarial_dataset,
        "Adversarial Dataset (8 edge cases)"
    )
    
    # Detailed adversarial analysis
    print("\n📋 Detailed Adversarial Analysis:")
    blocked = run_episode(agent, adversarial_dataset)
    
    for user in adversarial_dataset:
        was_blocked = user['id'] in blocked
        should_block = user['is_bot'] and user['tier'] != 'premium'
        
        status = "✅ CORRECT" if (was_blocked == should_block) else "❌ WRONG"
        action = "BLOCKED" if was_blocked else "ALLOWED"
        
        print(f"  {user['id']:20s} | RPS={user['rps']:4d} | Susp={str(user['is_suspicious_pattern']):5s} | "
              f"Tier={user['tier']:7s} | Bot={str(user['is_bot']):5s} | {action:7s} | {status}")
    
    # ========================================================================
    # TEST 3: Boundary Conditions
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 3: Boundary Conditions")
    print("="*80)
    
    boundary_dataset = generate_boundary_cases()
    boundary_results = evaluate_on_dataset(
        agent, boundary_dataset,
        "Boundary Dataset (8 boundary cases)"
    )
    
    # ========================================================================
    # SUMMARY FOR THIS AGENT
    # ========================================================================
    print("\n" + "="*80)
    print(f"SUMMARY: {agent_name}")
    print("="*80)
    
    print("\n📊 F1 Score Comparison:")
    print(f"  Easy (Seen):          {baseline_results['easy']['f1']:.3f}")
    print(f"  Medium (Seen):        {baseline_results['medium']['f1']:.3f}")
    print(f"  Winning (Seen):       {baseline_results['winning']['f1']:.3f}")
    print(f"  Extreme (UNSEEN):     {baseline_results['extreme']['f1']:.3f} ⭐")
    print(f"  Synthetic (UNSEEN):   {synthetic_results['f1']:.3f} ⭐")
    print(f"  Adversarial:          {adversarial_results['f1']:.3f}")
    print(f"  Boundary Cases:       {boundary_results['f1']:.3f}")
    
    print("\n🎯 Generalization Score:")
    avg_unseen = (baseline_results['extreme']['f1'] + synthetic_results['f1']) / 2
    avg_seen = (baseline_results['easy']['f1'] + baseline_results['medium']['f1'] + baseline_results['winning']['f1']) / 3
    
    print(f"  Average on SEEN data:   {avg_seen:.3f}")
    print(f"  Average on UNSEEN data: {avg_unseen:.3f}")
    print(f"  Generalization Gap:     {abs(avg_seen - avg_unseen):.3f}")
    
    if abs(avg_seen - avg_unseen) < 0.1:
        print("  ✅ Excellent generalization! (gap < 0.1)")
    elif abs(avg_seen - avg_unseen) < 0.2:
        print("  ⚠️  Good generalization (gap < 0.2)")
    else:
        print("  ❌ Poor generalization (gap > 0.2)")
    
    print("\n🛡️  Premium Protection:")
    total_premium_penalty = sum([
        baseline_results['easy']['premium_penalty'],
        baseline_results['medium']['premium_penalty'],
        baseline_results['extreme']['premium_penalty'],
        baseline_results['winning']['premium_penalty'],
        synthetic_results['premium_penalty'],
        adversarial_results['premium_penalty'],
        boundary_results['premium_penalty'],
    ])
    
    if total_premium_penalty == 0:
        print(f"  ✅ PERFECT: Never blocked premium users across ALL tests")
    else:
        print(f"  ❌ FAILED: Blocked {total_premium_penalty} premium users")
    
    return {
        'baseline': baseline_results,
        'synthetic': synthetic_results,
        'adversarial': adversarial_results,
        'boundary': boundary_results,
        'avg_seen': avg_seen,
        'avg_unseen': avg_unseen,
        'generalization_gap': abs(avg_seen - avg_unseen),
        'premium_penalty': total_premium_penalty
    }


def main():
    print("="*80)
    print("RULE-BASED AGENTS GENERALIZATION TESTING SUITE")
    print("="*80)
    print("\nComparing all three rule-based agents across generalization tests:")
    print("  1. EasyDefenderAgent (Simple RPS threshold)")
    print("  2. MediumDefenderAgent (RPS + Suspicious pattern)")
    print("  3. HardDefenderAgent (Risk-based scoring)")
    print()
    
    # Initialize all agents
    agents = {
        "EasyDefenderAgent": EasyDefenderAgent(rps_threshold=30, premium_rps_threshold=80),
        "MediumDefenderAgent": MediumDefenderAgent(suspicious_rps_threshold=26, premium_rps_threshold=45),
        "HardDefenderAgent": HardDefenderAgent(block_threshold=2.5)
    }
    
    # Test each agent
    all_results = {}
    for agent_name, agent in agents.items():
        all_results[agent_name] = test_agent(agent_name, agent)
    
    # ========================================================================
    # COMPARATIVE ANALYSIS
    # ========================================================================
    print("\n\n" + "="*80)
    print("COMPARATIVE ANALYSIS: ALL AGENTS")
    print("="*80)
    
    print("\n📊 Winning Dataset F1 (Primary Metric):")
    for agent_name in agents.keys():
        winning_f1 = all_results[agent_name]['baseline']['winning']['f1']
        status = "✅ PASS" if winning_f1 >= 0.70 else "❌ FAIL"
        print(f"  {agent_name:25s}: {winning_f1:.3f} {status}")
    
    print("\n🌍 Generalization Performance (UNSEEN data):")
    for agent_name in agents.keys():
        avg_unseen = all_results[agent_name]['avg_unseen']
        print(f"  {agent_name:25s}: {avg_unseen:.3f}")
    
    print("\n📏 Generalization Gap (lower is better):")
    for agent_name in agents.keys():
        gap = all_results[agent_name]['generalization_gap']
        status = "✅" if gap < 0.1 else "⚠️" if gap < 0.2 else "❌"
        print(f"  {agent_name:25s}: {gap:.3f} {status}")
    
    print("\n🛡️  Premium Protection:")
    for agent_name in agents.keys():
        penalty = all_results[agent_name]['premium_penalty']
        status = "✅ PERFECT" if penalty == 0 else f"❌ {penalty} violations"
        print(f"  {agent_name:25s}: {status}")
    
    print("\n🏆 Best Agent for Each Metric:")
    
    # Best winning F1
    best_winning = max(agents.keys(), key=lambda k: all_results[k]['baseline']['winning']['f1'])
    print(f"  Best Winning F1:       {best_winning} ({all_results[best_winning]['baseline']['winning']['f1']:.3f})")
    
    # Best generalization
    best_generalization = max(agents.keys(), key=lambda k: all_results[k]['avg_unseen'])
    print(f"  Best Generalization:   {best_generalization} ({all_results[best_generalization]['avg_unseen']:.3f})")
    
    # Lowest gap
    best_gap = min(agents.keys(), key=lambda k: all_results[k]['generalization_gap'])
    print(f"  Lowest Gen Gap:        {best_gap} ({all_results[best_gap]['generalization_gap']:.3f})")
    
    # Best adversarial
    best_adversarial = max(agents.keys(), key=lambda k: all_results[k]['adversarial']['f1'])
    print(f"  Best Adversarial:      {best_adversarial} ({all_results[best_adversarial]['adversarial']['f1']:.3f})")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE!")
    print("="*80)
    
    print("\n💡 Key Insights:")
    print("  • Rule-based agents are inherently interpretable and debuggable")
    print("  • They generalize well if thresholds are well-calibrated")
    print("  • No training required - instant deployment")
    print("  • Fixed logic may struggle with evolving attack patterns")
    print("  • Compare with DQN results to see ML vs Rules tradeoff")
    print()


if __name__ == "__main__":
    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    main()
