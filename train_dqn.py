"""
train_dqn.py - Deep Q-Network Training for API Rate Limit Defender

This script trains a DQN agent using curriculum learning to identify and block
malicious bots while protecting legitimate users.

Training Strategy:
- Phase 1: 100 episodes on easy data (warmup)
- Phase 2: 200 episodes on medium data (hardening)
- Phase 3: 500 episodes on winning data (adversarial)

Output: best_model.pt (state dict of best performing model)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
import numpy as np
from collections import deque
from typing import List, Dict, Any, Tuple
import os

# Import existing components
from environment import APIRateLimitDefenderEnv
from data import get_easy_data, get_medium_data, get_extreme_data, get_winning_data
from grader import Grader


# ============================================================================
# DQN NETWORK ARCHITECTURE
# ============================================================================

class DefenderNetwork(nn.Module):
    """
    Deep Q-Network for bot detection.
    
    Architecture:
    - Input: 3 features (normalized RPS, suspicious flag, tier flag)
    - Hidden: 2 layers x 64 units with ReLU
    - Output: 2 Q-values (noop, block)
    """
    
    def __init__(self, input_dim: int = 3, hidden_dim: int = 64, output_dim: int = 2):
        super(DefenderNetwork, self).__init__()
        
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        
        # Initialize weights using Xavier initialization
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.xavier_uniform_(self.fc3.weight)
    
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x: Tensor of shape (batch_size, input_dim)
            
        Returns:
            Q-values of shape (batch_size, output_dim)
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


# ============================================================================
# EXPERIENCE REPLAY BUFFER
# ============================================================================

class ReplayBuffer:
    """Experience replay buffer for DQN training."""
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer."""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int):
        """Sample random batch of experiences."""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        return len(self.buffer)


# ============================================================================
# DQN AGENT
# ============================================================================

class DQNAgent:
    """DQN Agent with epsilon-greedy exploration and experience replay."""
    
    def __init__(
        self,
        input_dim: int = 3,
        hidden_dim: int = 64,
        learning_rate: float = 0.001,
        gamma: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        buffer_capacity: int = 10000,
        batch_size: int = 64,
        device: str = None
    ):
        """
        Initialize DQN agent.
        
        Args:
            input_dim: Number of input features per user
            hidden_dim: Hidden layer size
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
            epsilon_start: Initial exploration rate
            epsilon_end: Minimum exploration rate
            epsilon_decay: Epsilon decay rate per episode
            buffer_capacity: Size of replay buffer
            batch_size: Batch size for training
            device: Device to use (cuda/cpu)
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_dim = input_dim
        self.gamma = gamma
        self.batch_size = batch_size
        
        # Epsilon-greedy parameters
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        
        # Networks
        self.policy_net = DefenderNetwork(input_dim, hidden_dim, output_dim=2).to(self.device)
        self.target_net = DefenderNetwork(input_dim, hidden_dim, output_dim=2).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        
        # Replay buffer
        self.memory = ReplayBuffer(buffer_capacity)
        
        # Statistics
        self.steps_done = 0
    
    def extract_features(self, user: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from user observation.
        
        Args:
            user: User dict with 'rps', 'is_suspicious_pattern', 'tier'
            
        Returns:
            Feature vector [normalized_rps, suspicious_flag, tier_flag]
        """
        # Normalize RPS to [0, 1] range
        rps_normalized = min(user["rps"] / 100.0, 1.0)
        
        # Binary flags
        suspicious_flag = float(user["is_suspicious_pattern"])
        tier_flag = float(user["tier"] == "premium")
        
        return np.array([rps_normalized, suspicious_flag, tier_flag], dtype=np.float32)
    
    def select_action(self, observation: Dict[str, Any], training: bool = True) -> Dict[str, str]:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            observation: Environment observation
            training: If True, use epsilon-greedy; else use greedy
            
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
        
        # Epsilon-greedy exploration (only during training)
        if training and random.random() < self.epsilon:
            # Random action
            if random.random() < 0.5:
                # Random block
                user = random.choice(available_users)
                return {"type": "block", "user_id": user["id"]}
            else:
                # Noop
                return {"type": "noop", "user_id": None}
        
        # Greedy action: select user with highest Q-value for blocking
        best_user_id = None
        best_q_value = float('-inf')
        
        for user in available_users:
            features = self.extract_features(user)
            features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                q_values = self.policy_net(features_tensor)
                block_q = q_values[0, 1].item()  # Q-value for blocking
            
            if block_q > best_q_value:
                best_q_value = block_q
                best_user_id = user["id"]
        
        # Decide whether to block based on Q-value comparison
        # Get Q-value for noop (take average user as reference)
        if available_users:
            avg_features = np.mean([self.extract_features(u) for u in available_users], axis=0)
            avg_tensor = torch.FloatTensor(avg_features).unsqueeze(0).to(self.device)
            with torch.no_grad():
                noop_q = self.policy_net(avg_tensor)[0, 0].item()
        else:
            noop_q = 0.0
        
        if best_q_value > noop_q and best_user_id:
            return {"type": "block", "user_id": best_user_id}
        else:
            return {"type": "noop", "user_id": None}
    
    def update_target_network(self):
        """Copy weights from policy network to target network."""
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def decay_epsilon(self):
        """Decay epsilon for exploration."""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
    
    def optimize_model(self):
        """Perform one step of optimization on the policy network."""
        if len(self.memory) < self.batch_size:
            return 0.0
        
        # Sample batch from replay buffer
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        # Convert to tensors
        state_batch = torch.FloatTensor(np.array(states)).to(self.device)
        action_batch = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        reward_batch = torch.FloatTensor(rewards).to(self.device)
        next_state_batch = torch.FloatTensor(np.array(next_states)).to(self.device)
        done_batch = torch.FloatTensor(dones).to(self.device)
        
        # Compute current Q-values
        current_q_values = self.policy_net(state_batch).gather(1, action_batch)
        
        # Compute target Q-values
        with torch.no_grad():
            next_q_values = self.target_net(next_state_batch).max(1)[0]
            target_q_values = reward_batch + (1 - done_batch) * self.gamma * next_q_values
        
        # Compute loss
        loss = F.smooth_l1_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        return loss.item()
    
    def save(self, path: str):
        """Save model state dict."""
        torch.save(self.policy_net.state_dict(), path)
        print(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model state dict."""
        self.policy_net.load_state_dict(torch.load(path, map_location=self.device))
        self.target_net.load_state_dict(self.policy_net.state_dict())
        print(f"Model loaded from {path}")


# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================

def train_episode(agent: DQNAgent, env: APIRateLimitDefenderEnv, dataset: List[Dict], training: bool = True) -> Dict[str, Any]:
    """
    Run one training episode.
    
    Args:
        agent: DQN agent
        env: Environment
        dataset: Dataset to use
        training: If True, update agent; else just evaluate
        
    Returns:
        Dict with episode statistics
    """
    obs = env.reset(dataset)
    done = False
    total_reward = 0.0
    steps = 0
    losses = []
    
    prev_state = None
    prev_action = None
    
    while not done and steps < 20:
        steps += 1
        
        # Select action
        action = agent.select_action(obs, training=training)
        
        # Convert action to state representation for replay buffer
        # For simplicity, we store the first available user's features
        # In a more sophisticated approach, you'd encode the full observation
        users = [u for u in obs.get("users", []) if u["id"] not in obs.get("blocked_users", [])]
        if users:
            current_state = agent.extract_features(users[0])
        else:
            current_state = np.zeros(agent.input_dim, dtype=np.float32)
        
        # Execute action
        next_obs, reward, done, info = env.step(action)
        total_reward += reward
        
        # Store transition in replay buffer (if training)
        if training and prev_state is not None:
            # Action encoding: 0 = noop, 1 = block
            action_idx = 1 if prev_action["type"] == "block" else 0
            agent.memory.push(prev_state, action_idx, reward, current_state, done)
        
        # Update model (if training)
        if training:
            loss = agent.optimize_model()
            if loss > 0:
                losses.append(loss)
        
        prev_state = current_state
        prev_action = action
        obs = next_obs
    
    # Evaluate final performance
    grader = Grader()
    results = grader.grade(info.get("blocked_ids", []), dataset)
    
    return {
        "total_reward": total_reward,
        "steps": steps,
        "f1": results["f1"],
        "precision": results["precision"],
        "recall": results["recall"],
        "score": results["score"],
        "avg_loss": np.mean(losses) if losses else 0.0,
        "epsilon": agent.epsilon,
        "premium_penalty": results["premium_penalty"]
    }


def validate(agent: DQNAgent, dataset: List[Dict]) -> Dict[str, Any]:
    """
    Validate agent on dataset without training.
    
    Args:
        agent: DQN agent
        dataset: Validation dataset
        
    Returns:
        Validation results
    """
    env = APIRateLimitDefenderEnv()
    results = train_episode(agent, env, dataset, training=False)
    return results


def train_curriculum(
    agent: DQNAgent,
    easy_episodes: int = 100,
    medium_episodes: int = 200,
    winning_episodes: int = 500,
    target_update_freq: int = 10,
    validation_freq: int = 50,
    save_path: str = "best_model.pt"
):
    """
    Train agent using curriculum learning.
    
    Args:
        agent: DQN agent
        easy_episodes: Number of episodes on easy data
        medium_episodes: Number of episodes on medium data
        winning_episodes: Number of episodes on winning data
        target_update_freq: Update target network every N episodes
        validation_freq: Validate every N episodes
        save_path: Path to save best model
        
    Returns:
        Training statistics
    """
    env = APIRateLimitDefenderEnv()
    best_val_f1 = 0.0
    episode_count = 0
    
    # Phase 1: Warmup on easy data
    print("="*70)
    print("PHASE 1: WARMUP (Easy Data)")
    print("="*70)
    
    for episode in range(easy_episodes):
        episode_count += 1
        dataset = get_easy_data()
        results = train_episode(agent, env, dataset, training=True)
        
        # Update target network
        if episode_count % target_update_freq == 0:
            agent.update_target_network()
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Print progress
        if (episode + 1) % 20 == 0:
            print(f"Episode {episode+1}/{easy_episodes}: "
                  f"F1={results['f1']:.3f}, "
                  f"Score={results['score']:.3f}, "
                  f"Reward={results['total_reward']:.2f}, "
                  f"Loss={results['avg_loss']:.4f}, "
                  f"ε={results['epsilon']:.3f}")
        
        # Validate periodically
        if (episode + 1) % validation_freq == 0:
            val_results = validate(agent, get_extreme_data())
            print(f"  → Validation F1: {val_results['f1']:.3f}")
            
            if val_results['f1'] > best_val_f1:
                best_val_f1 = val_results['f1']
                agent.save(save_path)
                print(f"  → New best model saved! F1: {best_val_f1:.3f}")
    
    # Phase 2: Hardening on medium data
    print("\n" + "="*70)
    print("PHASE 2: HARDENING (Medium Data)")
    print("="*70)
    
    for episode in range(medium_episodes):
        episode_count += 1
        dataset = get_medium_data()
        results = train_episode(agent, env, dataset, training=True)
        
        if episode_count % target_update_freq == 0:
            agent.update_target_network()
        
        agent.decay_epsilon()
        
        if (episode + 1) % 40 == 0:
            print(f"Episode {episode+1}/{medium_episodes}: "
                  f"F1={results['f1']:.3f}, "
                  f"Score={results['score']:.3f}, "
                  f"Reward={results['total_reward']:.2f}, "
                  f"Loss={results['avg_loss']:.4f}, "
                  f"ε={results['epsilon']:.3f}")
        
        if (episode + 1) % validation_freq == 0:
            val_results = validate(agent, get_extreme_data())
            print(f"  → Validation F1: {val_results['f1']:.3f}")
            
            if val_results['f1'] > best_val_f1:
                best_val_f1 = val_results['f1']
                agent.save(save_path)
                print(f"  → New best model saved! F1: {best_val_f1:.3f}")
    
    # Phase 3: Adversarial on winning data
    print("\n" + "="*70)
    print("PHASE 3: ADVERSARIAL (Winning Data)")
    print("="*70)
    
    for episode in range(winning_episodes):
        episode_count += 1
        dataset = get_winning_data()
        results = train_episode(agent, env, dataset, training=True)
        
        if episode_count % target_update_freq == 0:
            agent.update_target_network()
        
        agent.decay_epsilon()
        
        if (episode + 1) % 100 == 0:
            print(f"Episode {episode+1}/{winning_episodes}: "
                  f"F1={results['f1']:.3f}, "
                  f"Score={results['score']:.3f}, "
                  f"Reward={results['total_reward']:.2f}, "
                  f"Loss={results['avg_loss']:.4f}, "
                  f"ε={results['epsilon']:.3f}")
        
        if (episode + 1) % validation_freq == 0:
            val_results = validate(agent, get_extreme_data())
            print(f"  → Validation F1: {val_results['f1']:.3f}")
            
            if val_results['f1'] > best_val_f1:
                best_val_f1 = val_results['f1']
                agent.save(save_path)
                print(f"  → New best model saved! F1: {best_val_f1:.3f}")
    
    # Final validation
    print("\n" + "="*70)
    print("FINAL VALIDATION")
    print("="*70)
    
    # Load best model
    agent.load(save_path)
    
    # Test on all datasets
    for name, dataset_fn in [
        ("Easy", get_easy_data),
        ("Medium", get_medium_data),
        ("Extreme", get_extreme_data),
        ("Winning", get_winning_data)
    ]:
        val_results = validate(agent, dataset_fn())
        print(f"{name}: F1={val_results['f1']:.3f}, "
              f"Precision={val_results['precision']:.3f}, "
              f"Recall={val_results['recall']:.3f}, "
              f"Score={val_results['score']:.3f}, "
              f"Premium Penalty={val_results['premium_penalty']}")
    
    print(f"\nBest model saved to: {save_path}")
    print(f"Best validation F1: {best_val_f1:.3f}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main training entry point."""
    print("="*70)
    print("DQN Training for API Rate Limit Defender")
    print("="*70)
    
    # Check GPU availability
    print("\n🔍 GPU Check:")
    if torch.cuda.is_available():
        print(f"✅ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA Version: {torch.version.cuda}")
        print(f"✅ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print("✅ Training will use GPU (3-4x faster!)")
    else:
        print("⚠️  GPU NOT detected - training will use CPU")
        print("⚠️  This will take 20-40 minutes instead of 5-10 minutes")
        print("⚠️  To use GPU, install CUDA and PyTorch with CUDA support:")
        print("    pip install torch --index-url https://download.pytorch.org/whl/cu118")
    print()
    
    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(42)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    
    # Create agent with more stable hyperparameters
    agent = DQNAgent(
        input_dim=3,
        hidden_dim=128,           # Increased from 64 for more capacity
        learning_rate=0.0005,     # Reduced from 0.001 for stability
        gamma=0.95,
        epsilon_start=1.0,
        epsilon_end=0.05,         # Increased from 0.01 for more exploration
        epsilon_decay=0.997,      # Slower decay from 0.995 for gradual learning
        buffer_capacity=10000,
        batch_size=32             # Reduced from 64 for stability
    )
    
    print(f"🖥️  Device: {agent.device}")
    print(f"🧠 Network: {agent.policy_net}")
    print()
    
    # Train using curriculum learning
    # Optimized training with adjusted rewards and stable hyperparameters
    train_curriculum(
        agent,
        easy_episodes=100,
        medium_episodes=300,  # Balanced approach for precision learning
        winning_episodes=500,
        target_update_freq=10,
        validation_freq=50,
        save_path="best_model.pt"
    )
    
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
