"""
test_generalization.py - Comprehensive Generalization Testing Suite

Tests the DQN model's ability to generalize to unseen data using:
1. Synthetic users with out-of-distribution RPS values
2. Adversarial examples designed to fool the model
3. Edge cases and boundary conditions
4. Statistical analysis of generalization performance
"""

import torch
import random
import numpy as np
from typing import List, Dict, Any
from environment import APIRateLimitDefenderEnv
from models import User
from grader import Grader
from data import get_easy_data, get_medium_data, get_extreme_data, get_winning_data


class DefenderNetwork(torch.nn.Module):
    """DQN Network Architecture (must match train_dqn.py)"""
    def __init__(self, input_dim=3, hidden_dim=64):
        super(DefenderNetwork, self).__init__()
        self.fc1 = torch.nn.Linear(input_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = torch.nn.Linear(hidden_dim, 2)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


def load_model(model_path="best_model.pt"):
    """Load trained DQN model"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DefenderNetwork(input_dim=3, hidden_dim=64)
    
    try:
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict)
        model.eval()
        print(f"✅ Model loaded from {model_path}")
        return model, device
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, device


def extract_features(user: Dict[str, Any]) -> torch.Tensor:
    """Extract and normalize features from user data"""
    # Normalize RPS to [0, 1]
    rps_normalized = user['rps'] / 600.0
    
    # Convert boolean to float
    suspicious = 1.0 if user['is_suspicious_pattern'] else 0.0
    
    # Convert tier to binary
    tier = 1.0 if user['tier'] == 'premium' else 0.0
    
    return torch.FloatTensor([rps_normalized, suspicious, tier])


def get_action(model, user: Dict[str, Any], device) -> str:
    """Get model's action for a user"""
    features = extract_features(user).unsqueeze(0).to(device)
    
    with torch.no_grad():
        q_values = model(features)
        action_idx = q_values.argmax().item()
    
    # action_idx: 0 = noop, 1 = block
    if action_idx == 1:
        return user['id']
    return None


def run_episode(model, dataset: List[Dict], device, max_steps=20):
    """Run one episode and collect blocked users"""
    blocked_users = []
    
    for user in dataset[:max_steps]:
        action = get_action(model, user, device)
        if action:
            blocked_users.append(action)
    
    return blocked_users


def evaluate_on_dataset(model, dataset: List[Dict], device, dataset_name: str):
    """Evaluate model on a dataset"""
    grader = Grader()
    
    # Run episode
    blocked_ids = run_episode(model, dataset, device)
    
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
# GENERALIZATION TEST 1: Synthetic Users (Out of Distribution)
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


# ============================================================================
# GENERALIZATION TEST 2: Adversarial Examples
# ============================================================================

def generate_adversarial_examples():
    """Generate tricky edge cases designed to confuse the model"""
    return [
        # Adversarial 1: Stealth bot (low RPS but suspicious)
        {
            'id': 'ADV_STEALTH_1',
            'rps': 20,
            'is_suspicious_pattern': True,
            'tier': 'normal',
            'is_bot': True  # Should block, but low RPS might confuse model
        },
        # Adversarial 2: Active human (high RPS, not suspicious)
        {
            'id': 'ADV_ACTIVE_1',
            'rps': 180,
            'is_suspicious_pattern': False,
            'tier': 'normal',
            'is_bot': False  # Should NOT block, but high RPS might trigger
        },
        # Adversarial 3: Premium bot (should NEVER block despite being bot)
        {
            'id': 'ADV_PREMIUM_BOT',
            'rps': 500,
            'is_suspicious_pattern': True,
            'tier': 'premium',
            'is_bot': True  # Premium protection should prevent blocking
        },
        # Adversarial 4: Normal human with suspicious pattern (false positive trap)
        {
            'id': 'ADV_FALSE_POS',
            'rps': 45,
            'is_suspicious_pattern': True,
            'tier': 'normal',
            'is_bot': False  # Should NOT block (human with unusual pattern)
        },
        # Adversarial 5: Bot with no suspicious pattern (stealth)
        {
            'id': 'ADV_STEALTH_2',
            'rps': 350,
            'is_suspicious_pattern': False,  # Tries to hide
            'tier': 'normal',
            'is_bot': True
        },
        # Adversarial 6: Extreme high RPS bot
        {
            'id': 'ADV_EXTREME_HIGH',
            'rps': 2000,  # WAY outside training range
            'is_suspicious_pattern': True,
            'tier': 'normal',
            'is_bot': True
        },
        # Adversarial 7: Zero RPS human
        {
            'id': 'ADV_ZERO_RPS',
            'rps': 0,  # Edge case: no requests
            'is_suspicious_pattern': False,
            'tier': 'normal',
            'is_bot': False
        },
        # Adversarial 8: Premium human with high RPS (should NEVER block)
        {
            'id': 'ADV_PREMIUM_HUMAN',
            'rps': 200,
            'is_suspicious_pattern': True,
            'tier': 'premium',
            'is_bot': False  # Premium protection crucial
        },
    ]


# ============================================================================
# GENERALIZATION TEST 3: Boundary Conditions
# ============================================================================

def generate_boundary_cases():
    """Generate users at decision boundaries"""
    return [
        # Boundary 1: RPS exactly at typical threshold (50)
        {'id': 'BOUND_RPS_50', 'rps': 50, 'is_suspicious_pattern': False, 'tier': 'normal', 'is_bot': False},
        {'id': 'BOUND_RPS_50_BOT', 'rps': 50, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        
        # Boundary 2: RPS at 100 (common threshold)
        {'id': 'BOUND_RPS_100', 'rps': 100, 'is_suspicious_pattern': False, 'tier': 'normal', 'is_bot': False},
        {'id': 'BOUND_RPS_100_BOT', 'rps': 100, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        
        # Boundary 3: Very low RPS (1-5)
        {'id': 'BOUND_RPS_1', 'rps': 1, 'is_suspicious_pattern': False, 'tier': 'normal', 'is_bot': False},
        {'id': 'BOUND_RPS_5_BOT', 'rps': 5, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        
        # Boundary 4: Training max RPS (600)
        {'id': 'BOUND_RPS_600', 'rps': 600, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
        {'id': 'BOUND_RPS_601', 'rps': 601, 'is_suspicious_pattern': True, 'tier': 'normal', 'is_bot': True},
    ]


# ============================================================================
# MAIN TESTING SUITE
# ============================================================================

def main():
    print("="*80)
    print("DQN MODEL GENERALIZATION TESTING SUITE")
    print("="*80)
    
    # Load model
    model, device = load_model("best_model.pt")
    if model is None:
        print("❌ Cannot proceed without model")
        return
    
    print(f"🖥️  Device: {device}")
    print()
    
    # ========================================================================
    # BASELINE: Test on Known Datasets
    # ========================================================================
    print("="*80)
    print("BASELINE: Performance on Known Datasets")
    print("="*80)
    
    baseline_results = {}
    baseline_results['easy'] = evaluate_on_dataset(model, get_easy_data(), device, "Easy Dataset (Seen)")
    baseline_results['medium'] = evaluate_on_dataset(model, get_medium_data(), device, "Medium Dataset (Seen)")
    baseline_results['extreme'] = evaluate_on_dataset(model, get_extreme_data(), device, "Extreme Dataset (UNSEEN)")
    baseline_results['winning'] = evaluate_on_dataset(model, get_winning_data(), device, "Winning Dataset (Seen)")
    
    # ========================================================================
    # TEST 1: Synthetic Out-of-Distribution Users
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 1: Synthetic Out-of-Distribution Users")
    print("="*80)
    print("Testing model on users with RPS values OUTSIDE training range...")
    
    synthetic_dataset = (
        generate_synthetic_high_rps_bots(20) +
        generate_synthetic_low_rps_humans(20) +
        generate_synthetic_stealth_bots(15) +
        generate_synthetic_active_humans(15)
    )
    random.shuffle(synthetic_dataset)
    
    synthetic_results = evaluate_on_dataset(
        model, synthetic_dataset, device, 
        "Synthetic Dataset (70 users, OUT OF DISTRIBUTION)"
    )
    
    # ========================================================================
    # TEST 2: Adversarial Examples
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 2: Adversarial Examples")
    print("="*80)
    print("Testing model on tricky edge cases designed to confuse it...")
    
    adversarial_dataset = generate_adversarial_examples()
    adversarial_results = evaluate_on_dataset(
        model, adversarial_dataset, device,
        "Adversarial Dataset (8 edge cases)"
    )
    
    # Detailed adversarial analysis
    print("\n📋 Detailed Adversarial Analysis:")
    blocked = run_episode(model, adversarial_dataset, device)
    
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
    print("Testing model at decision boundaries...")
    
    boundary_dataset = generate_boundary_cases()
    boundary_results = evaluate_on_dataset(
        model, boundary_dataset, device,
        "Boundary Dataset (8 boundary cases)"
    )
    
    # ========================================================================
    # TEST 4: RPS Range Sensitivity
    # ========================================================================
    print("\n" + "="*80)
    print("TEST 4: RPS Range Sensitivity Analysis")
    print("="*80)
    print("Testing how model performs across different RPS ranges...")
    
    rps_ranges = [
        (0, 50, "Very Low"),
        (50, 100, "Low"),
        (100, 200, "Medium"),
        (200, 400, "High"),
        (400, 600, "Very High (Training Max)"),
        (600, 1000, "Extreme (Out of Training)"),
    ]
    
    print(f"\n{'RPS Range':30s} | F1    | Precision | Recall | Tested")
    print("-" * 80)
    
    for min_rps, max_rps, label in rps_ranges:
        # Create test dataset for this RPS range
        test_set = [
            {
                'id': f'RPS_{min_rps}_{max_rps}_{i}',
                'rps': random.randint(min_rps, max_rps),
                'is_suspicious_pattern': random.choice([True, False]),
                'tier': 'normal',
                'is_bot': random.random() > 0.5
            }
            for i in range(20)
        ]
        
        if test_set:
            grader = Grader()
            blocked = run_episode(model, test_set, device)
            results = grader.grade(blocked, test_set)
            
            print(f"{label} ({min_rps}-{max_rps}):".ljust(30) + 
                  f" | {results['f1']:.3f} | {results['precision']:.3f}     | "
                  f"{results['recall']:.3f}  | {len(test_set)}")
    
    # ========================================================================
    # SUMMARY REPORT
    # ========================================================================
    print("\n" + "="*80)
    print("GENERALIZATION SUMMARY REPORT")
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
        print("  ❌ Poor generalization (gap > 0.2, likely overfitting)")
    
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
    
    print("\n📈 Key Insights:")
    
    # Insight 1: Generalization quality
    if synthetic_results['f1'] >= 0.60:
        print("  ✅ Model generalizes well to out-of-distribution RPS values")
    else:
        print("  ⚠️  Model struggles with RPS values outside training range")
    
    # Insight 2: Adversarial robustness
    if adversarial_results['f1'] >= 0.50:
        print("  ✅ Model is somewhat robust to adversarial examples")
    else:
        print("  ❌ Model is vulnerable to adversarial examples")
    
    # Insight 3: Precision
    if synthetic_results['precision'] >= 0.60:
        print("  ✅ Low false positive rate on new data")
    else:
        print("  ⚠️  High false positive rate (blocks too many legitimate users)")
    
    # Insight 4: Recall
    if synthetic_results['recall'] >= 0.60:
        print("  ✅ Catches most bots even on new data")
    else:
        print("  ⚠️  Misses many bots on new data")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE!")
    print("="*80)
    print("\n💡 Recommendation:")
    
    if avg_unseen >= 0.65 and total_premium_penalty == 0:
        print("  ✅ Model demonstrates GOOD generalization capability")
        print("  ✅ Safe to deploy on real-world data")
        print("  ✅ Ready for hackathon submission")
    elif avg_unseen >= 0.50:
        print("  ⚠️  Model has MODERATE generalization capability")
        print("  ⚠️  May need more training data or feature engineering")
        print("  ✅ Acceptable for hackathon submission")
    else:
        print("  ❌ Model has POOR generalization capability")
        print("  ❌ Consider using rule-based agent instead")
        print("  ❌ Need to retrain with more data or better features")
    
    print()


if __name__ == "__main__":
    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    main()
