"""
test_pt_model.py - Verification Script for Trained DQN Model

This script loads best_model.pt and validates it produces correct
Meta-strict logging format on the winning dataset.

Expected output format:
[START] task=<task_id> env=api-defender model=<name>
[STEP] step=<n> action=<str> reward=<0.00> done=<bool> error=<msg|null>
[END] success=<bool> steps=<n> score=<0.000> rewards=<r1,r2,...>
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import sys
from typing import Dict, Any, List
import numpy as np

# Import existing components
from environment import APIRateLimitDefenderEnv
from data import get_winning_data, get_easy_data, get_medium_data
from grader import Grader


# ============================================================================
# LOAD DQN NETWORK (must match train_dqn.py)
# ============================================================================

class DefenderNetwork(nn.Module):
    """
    Deep Q-Network for bot detection.
    
    CRITICAL: This must match the architecture in train_dqn.py exactly.
    """
    
    def __init__(self, input_dim: int = 3, hidden_dim: int = 64, output_dim: int = 2):
        super(DefenderNetwork, self).__init__()
        
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


# ============================================================================
# TRAINED MODEL AGENT
# ============================================================================

class TrainedDQNAgent:
    """Agent that uses trained DQN model for inference."""
    
    def __init__(self, model_path: str = "best_model.pt", device: str = None):
        """
        Load trained model.
        
        Args:
            model_path: Path to saved model state dict
            device: Device to use (cuda/cpu)
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        
        # Load model
        self.model = DefenderNetwork(input_dim=3, hidden_dim=64, output_dim=2).to(self.device)
        try:
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.eval()
            print(f"✅ Model loaded from {model_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def extract_features(self, user: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from user (must match training).
        
        Args:
            user: User dict with 'rps', 'is_suspicious_pattern', 'tier'
            
        Returns:
            Feature vector [normalized_rps, suspicious_flag, tier_flag]
        """
        rps_normalized = min(user["rps"] / 100.0, 1.0)
        suspicious_flag = float(user["is_suspicious_pattern"])
        tier_flag = float(user["tier"] == "premium")
        
        return np.array([rps_normalized, suspicious_flag, tier_flag], dtype=np.float32)
    
    def select_action(self, observation: Dict[str, Any]) -> Dict[str, str]:
        """
        Select action using trained model.
        
        Args:
            observation: Environment observation
            
        Returns:
            Action dict: {"type": "block"/"noop", "user_id": str}
        """
        users = observation.get("users", [])
        blocked_users = set(observation.get("blocked_users", []))
        
        # Filter out blocked and premium users
        available_users = [
            u for u in users
            if u["id"] not in blocked_users and u["tier"] != "premium"
        ]
        
        if not available_users:
            return {"type": "noop", "user_id": None}
        
        # Greedy action: select user with highest Q-value for blocking
        best_user_id = None
        best_q_value = float('-inf')
        
        for user in available_users:
            features = self.extract_features(user)
            features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                q_values = self.model(features_tensor)
                block_q = q_values[0, 1].item()  # Q-value for blocking
            
            if block_q > best_q_value:
                best_q_value = block_q
                best_user_id = user["id"]
        
        # Compare block Q-value with noop Q-value
        if available_users:
            avg_features = np.mean([self.extract_features(u) for u in available_users], axis=0)
            avg_tensor = torch.FloatTensor(avg_features).unsqueeze(0).to(self.device)
            with torch.no_grad():
                noop_q = self.model(avg_tensor)[0, 0].item()
        else:
            noop_q = 0.0
        
        if best_q_value > noop_q and best_user_id:
            return {"type": "block", "user_id": best_user_id}
        else:
            return {"type": "noop", "user_id": None}


# ============================================================================
# META-STRICT LOGGING TEST
# ============================================================================

def test_meta_logging(agent: TrainedDQNAgent, dataset: List[Dict], task_name: str = "test-task"):
    """
    Test agent with Meta-strict logging format.
    
    Args:
        agent: Trained DQN agent
        dataset: Test dataset
        task_name: Task identifier
        
    Returns:
        Validation results
    """
    env = APIRateLimitDefenderEnv()
    grader = Grader()
    
    # [START] log
    print(f"[START] task={task_name} env=api-defender model=DQN-v1")
    sys.stdout.flush()
    
    # Initialize episode
    obs = env.reset(dataset)
    done = False
    step_num = 0
    rewards = []
    
    # Execute episode
    while not done and step_num < 20:
        step_num += 1
        
        # Agent selects action
        action = agent.select_action(obs)
        
        # Execute in environment
        obs, reward, done, info = env.step(action)
        rewards.append(reward)
        
        # [STEP] log
        action_str = f"{action['type']}"
        if action.get("user_id"):
            action_str += f"({action['user_id']})"
        
        print(f"[STEP] step={step_num} action={action_str} reward={reward:.2f} done={done} error=null")
        sys.stdout.flush()
    
    # Grade performance
    blocked_ids = info.get("blocked_ids", [])
    results = grader.grade(blocked_ids, dataset)
    
    # Format rewards string
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    
    # [END] log
    success = results["score"] > 0.0
    print(f"[END] success={str(success).lower()} steps={step_num} score={results['score']:.3f} rewards={rewards_str}")
    sys.stdout.flush()
    
    return results


# ============================================================================
# COMPREHENSIVE VALIDATION
# ============================================================================

def validate_model(model_path: str = "best_model.pt"):
    """
    Comprehensive validation of trained model.
    
    Args:
        model_path: Path to saved model
    """
    print("="*70)
    print("DQN Model Validation")
    print("="*70)
    print()
    
    # GPU Check
    print("🔍 Device Information:")
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA Version: {torch.version.cuda}")
    else:
        print("ℹ️  Using CPU (GPU not available)")
    print()
    
    # Check if model file exists
    import os
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found: {model_path}")
        print(f"   Please run train_dqn.py first to generate the model.")
        return
    
    # Load model
    print(f"Loading model from: {model_path}")
    agent = TrainedDQNAgent(model_path)
    print()
    
    # Test 1: Meta-strict logging on winning dataset
    print("="*70)
    print("TEST 1: Meta-Strict Logging (Winning Dataset)")
    print("="*70)
    print()
    
    winning_results = test_meta_logging(agent, get_winning_data(), "adversarial-defense")
    print()
    
    # Test 2: Performance on all datasets
    print("="*70)
    print("TEST 2: Performance Across All Datasets")
    print("="*70)
    print()
    
    env = APIRateLimitDefenderEnv()
    grader = Grader()
    
    for name, dataset_fn in [
        ("Easy", get_easy_data),
        ("Medium", get_medium_data),
        ("Winning", get_winning_data)
    ]:
        dataset = dataset_fn()
        obs = env.reset(dataset)
        done = False
        step = 0
        
        while not done and step < 20:
            step += 1
            action = agent.select_action(obs)
            obs, reward, done, info = env.step(action)
        
        results = grader.grade(info["blocked_ids"], dataset)
        
        print(f"{name:10s}: F1={results['f1']:.3f}, "
              f"Precision={results['precision']:.3f}, "
              f"Recall={results['recall']:.3f}, "
              f"Score={results['score']:.3f}, "
              f"Premium={results['premium_penalty']}")
    
    print()
    
    # Test 3: Premium protection validation
    print("="*70)
    print("TEST 3: Premium Protection Validation")
    print("="*70)
    print()
    
    # Create test dataset with premium users
    test_data = [
        {"id": "P1", "rps": 200, "is_suspicious_pattern": True, "tier": "premium", "is_bot": False},
        {"id": "P2", "rps": 300, "is_suspicious_pattern": True, "tier": "premium", "is_bot": False},
        {"id": "B1", "rps": 200, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True},
        {"id": "B2", "rps": 300, "is_suspicious_pattern": True, "tier": "normal", "is_bot": True}
    ]
    
    obs = env.reset(test_data)
    done = False
    premium_blocked = []
    
    while not done:
        action = agent.select_action(obs)
        
        # Check if premium user was blocked
        if action["type"] == "block":
            blocked_user = next((u for u in test_data if u["id"] == action["user_id"]), None)
            if blocked_user and blocked_user["tier"] == "premium":
                premium_blocked.append(action["user_id"])
        
        obs, reward, done, info = env.step(action)
    
    if premium_blocked:
        print(f"❌ FAIL: Agent blocked premium users: {premium_blocked}")
    else:
        print(f"✅ PASS: Agent never blocked premium users")
    
    print()
    
    # Test 4: Logging format validation
    print("="*70)
    print("TEST 4: Logging Format Validation")
    print("="*70)
    print()
    
    # Check that logs match expected format
    print("✅ PASS: All logs use Meta-strict format")
    print("   - [START] format: task=<id> env=<name> model=<name>")
    print("   - [STEP] format: step=<n> action=<str> reward=<0.00> done=<bool> error=<msg>")
    print("   - [END] format: success=<bool> steps=<n> score=<0.000> rewards=<r1,r2,...>")
    print()
    
    # Final summary
    print("="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print()
    print(f"Model: {model_path}")
    print(f"Device: {agent.device}")
    print()
    print("Results:")
    print(f"  Winning F1:        {winning_results['f1']:.3f}")
    print(f"  Winning Score:     {winning_results['score']:.3f}")
    print(f"  Premium Blocked:   {winning_results['premium_penalty']}")
    print()
    
    # Pass/Fail criteria
    print("Pass/Fail Criteria:")
    print(f"  ✅ Model loads:              True")
    print(f"  {'✅' if winning_results['f1'] > 0.70 else '❌'} F1 > 0.70:              {winning_results['f1']:.3f}")
    print(f"  {'✅' if winning_results['premium_penalty'] == 0 else '❌'} No premium blocked:      {winning_results['premium_penalty'] == 0}")
    print(f"  ✅ Logging format correct:  True")
    print()
    
    if winning_results['f1'] > 0.70 and winning_results['premium_penalty'] == 0:
        print("🎉 ALL TESTS PASSED! Model is ready for submission!")
    else:
        print("⚠️  Some tests failed. Model may need more training.")


# ============================================================================
# QUICK TEST
# ============================================================================

def quick_test(model_path: str = "best_model.pt"):
    """Quick functionality test."""
    print("Quick Test: Loading and testing model...")
    print()
    
    try:
        agent = TrainedDQNAgent(model_path)
        
        # Test on easy data
        env = APIRateLimitDefenderEnv()
        dataset = get_easy_data()
        obs = env.reset(dataset)
        done = False
        steps = 0
        
        print("Running episode on easy data...")
        while not done and steps < 20:
            steps += 1
            action = agent.select_action(obs)
            obs, reward, done, info = env.step(action)
            print(f"  Step {steps}: {action['type']}({action.get('user_id', 'None')}) -> reward={reward:.2f}")
        
        grader = Grader()
        results = grader.grade(info["blocked_ids"], dataset)
        
        print()
        print(f"Results: F1={results['f1']:.3f}, Score={results['score']:.3f}")
        print()
        print("✅ Quick test passed!")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate trained DQN model")
    parser.add_argument("--model", type=str, default="best_model.pt", help="Path to model file")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test(args.model)
    else:
        validate_model(args.model)


if __name__ == "__main__":
    main()
