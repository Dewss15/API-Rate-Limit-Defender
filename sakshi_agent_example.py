"""
sakshi_agent_example.py - Example of integrating a trained RL agent

This shows how Sakshi would integrate her trained DQN/PPO agent
into the main.py framework.
"""

import torch
import torch.nn as nn
from typing import Dict, Any
from main import BaseAgent
from openenv_models import Action


# ============================================================================
# STEP 1: Define Your Model Architecture
# ============================================================================

class DQNNetwork(nn.Module):
    """
    Example DQN architecture.
    Modify this to match your actual trained model.
    """
    
    def __init__(self, input_dim=10, hidden_dim=128, output_dim=2):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, output_dim)
        )
    
    def forward(self, x):
        return self.network(x)


# ============================================================================
# STEP 2: Create Your Agent Class
# ============================================================================

class SakshiAgent(BaseAgent):
    """
    Sakshi's trained RL agent.
    
    This agent wraps a trained PyTorch model and integrates it with
    the main.py execution framework.
    """
    
    def __init__(self, model_path: str = "best_model.pt", confidence_threshold: float = 0.7):
        """
        Initialize Sakshi's agent.
        
        Args:
            model_path: Path to saved PyTorch model
            confidence_threshold: Threshold for blocking decision (0.0 to 1.0)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load trained model
        self.model = self._load_model(model_path)
        if self.model:
            self.model.to(self.device)
            self.model.eval()
        
        print(f"[INFO] Sakshi's agent loaded from {model_path}")
        print(f"[INFO] Using device: {self.device}")
        print(f"[INFO] Confidence threshold: {confidence_threshold}")
    
    def _load_model(self, path: str):
        """Load trained model from checkpoint."""
        try:
            # Option 1: Load full model
            model = torch.load(path, map_location=self.device)
            
            # Option 2: Load state dict only
            # model = DQNNetwork(input_dim=10, hidden_dim=128, output_dim=2)
            # model.load_state_dict(torch.load(path, map_location=self.device))
            
            return model
            
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return None
    
    def get_name(self) -> str:
        """Return agent name for logging."""
        return "Sakshi-DQN-v1"
    
    def select_action(self, observation: Dict[str, Any]) -> Action:
        """
        Select action using trained model.
        
        Args:
            observation: Dict with 'users', 'blocked_users', 'system_health'
            
        Returns:
            Action: Pydantic Action model
        """
        if self.model is None:
            # Fallback to simple heuristic if model failed to load
            return self._fallback_action(observation)
        
        users = observation.get("users", [])
        blocked_users = set(observation.get("blocked_users", []))
        system_health = observation.get("system_health", 1.0)
        
        # Iterate through users and evaluate each
        best_user_id = None
        best_confidence = 0.0
        
        for user in users:
            user_id = user["id"]
            
            # Skip already blocked
            if user_id in blocked_users:
                continue
            
            # CRITICAL: Never block premium (hard constraint)
            if user["tier"] == "premium":
                continue
            
            # Extract features and get model prediction
            features = self._extract_features(user, observation)
            block_confidence = self._predict(features)
            
            # Track user with highest blocking confidence
            if block_confidence > best_confidence:
                best_confidence = block_confidence
                best_user_id = user_id
        
        # Make decision based on best confidence
        if best_confidence >= self.confidence_threshold and best_user_id:
            return Action(type="block", user_id=best_user_id)
        
        return Action(type="noop", user_id=None)
    
    def _extract_features(self, user: Dict, observation: Dict) -> torch.Tensor:
        """
        Extract features from user and observation.
        
        IMPORTANT: These features MUST match what you used during training!
        
        Args:
            user: Single user dict
            observation: Full observation dict
            
        Returns:
            torch.Tensor: Feature vector
        """
        # Example feature set (customize to match your training)
        features = []
        
        # User-level features
        features.append(user["rps"] / 100.0)  # Normalized RPS
        features.append(float(user["is_suspicious_pattern"]))
        features.append(float(user["tier"] == "premium"))
        
        # Derived user features
        rps = user["rps"]
        features.append(float(rps < 10))   # Very low RPS
        features.append(float(10 <= rps < 30))  # Low RPS
        features.append(float(30 <= rps < 50))  # Medium RPS
        features.append(float(50 <= rps < 100)) # High RPS
        features.append(float(rps >= 100))      # Very high RPS
        
        # Context features (system state)
        features.append(observation["system_health"])
        
        # Blocking rate
        total_users = len(observation["users"])
        blocked_count = len(observation["blocked_users"])
        block_rate = blocked_count / total_users if total_users > 0 else 0
        features.append(block_rate)
        
        # Convert to tensor
        return torch.tensor(features, dtype=torch.float32, device=self.device)
    
    def _predict(self, features: torch.Tensor) -> float:
        """
        Get blocking confidence from model.
        
        Args:
            features: Feature tensor
            
        Returns:
            float: Block confidence (0.0 to 1.0)
        """
        try:
            with torch.no_grad():
                # Forward pass
                output = self.model(features)
                
                # Interpret output based on your model architecture
                
                # Option 1: Binary classification (2 outputs)
                # output = [noop_logit, block_logit]
                if output.shape[-1] == 2:
                    probs = torch.softmax(output, dim=-1)
                    block_prob = probs[1].item()  # Second output is block
                
                # Option 2: Single output (block probability)
                elif output.shape[-1] == 1:
                    block_prob = torch.sigmoid(output).item()
                
                # Option 3: Q-values (2 actions: noop=0, block=1)
                else:
                    # Assume output is Q-values, pick action with max Q
                    block_prob = 1.0 if output[1] > output[0] else 0.0
                
                return block_prob
                
        except Exception as e:
            print(f"[ERROR] Prediction error: {e}")
            return 0.0
    
    def _fallback_action(self, observation: Dict[str, Any]) -> Action:
        """Fallback to heuristic if model fails."""
        users = observation.get("users", [])
        blocked_users = set(observation.get("blocked_users", []))
        
        for user in users:
            if user["id"] in blocked_users:
                continue
            
            if user["tier"] == "premium":
                continue
            
            # Simple heuristic: block high RPS + suspicious
            if user["rps"] >= 60 and user["is_suspicious_pattern"]:
                return Action(type="block", user_id=user["id"])
        
        return Action(type="noop", user_id=None)
    
    def reset(self):
        """Reset agent state (optional, for stateful agents)."""
        # If your agent maintains internal state between episodes, reset it here
        pass


# ============================================================================
# STEP 3: Integration Example
# ============================================================================

def main_with_sakshi_agent():
    """
    Example of running main.py with Sakshi's agent.
    """
    from main import ExecutionEngine
    
    # Create Sakshi's agent
    agent = SakshiAgent(
        model_path="best_model.pt",  # Path to your trained model
        confidence_threshold=0.7      # Adjust based on precision/recall tradeoff
    )
    
    # Create execution engine
    engine = ExecutionEngine(agent)
    
    # Run all tasks
    results = engine.run_all_tasks()
    
    # Print summary
    engine.print_final_summary(results)


# ============================================================================
# STEP 4: Testing Your Agent
# ============================================================================

def test_feature_extraction():
    """Test that feature extraction works correctly."""
    agent = SakshiAgent(model_path="best_model.pt")
    
    # Example observation
    observation = {
        "users": [
            {"id": "U1", "rps": 50, "is_suspicious_pattern": True, "tier": "normal"},
            {"id": "U2", "rps": 5, "is_suspicious_pattern": False, "tier": "premium"}
        ],
        "blocked_users": [],
        "system_health": 0.95
    }
    
    # Extract features for first user
    user = observation["users"][0]
    features = agent._extract_features(user, observation)
    
    print("Feature shape:", features.shape)
    print("Feature values:", features)
    
    # Get prediction
    confidence = agent._predict(features)
    print(f"Block confidence: {confidence:.3f}")
    
    # Get action
    action = agent.select_action(observation)
    print(f"Action: {action.type} ({action.user_id})")


def test_on_single_task():
    """Test agent on a single task."""
    from data import get_easy_data
    from environment import APIRateLimitDefenderEnv
    from grader import Grader
    
    # Create agent
    agent = SakshiAgent(model_path="best_model.pt", confidence_threshold=0.7)
    
    # Create environment
    env = APIRateLimitDefenderEnv()
    data = get_easy_data()
    obs = env.reset(data)
    
    # Run episode
    done = False
    step = 0
    rewards = []
    
    while not done and step < 20:
        step += 1
        action = agent.select_action(obs)
        obs, reward, done, info = env.step(action.to_env_action())
        rewards.append(reward)
        print(f"Step {step}: {action.type}({action.user_id}) -> reward={reward:.2f}")
    
    # Grade
    grader = Grader()
    results = grader.grade(info["blocked_ids"], data)
    
    print("\nResults:")
    print(f"  F1:       {results['f1']:.3f}")
    print(f"  Score:    {results['score']:.3f}")
    print(f"  Rewards:  {sum(rewards):.2f}")


# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    # Option 1: Test feature extraction
    # test_feature_extraction()
    
    # Option 2: Test on single task
    # test_on_single_task()
    
    # Option 3: Run full evaluation
    main_with_sakshi_agent()
