"""
environment.py - API Rate Limit Defender RL Environment

A deterministic OpenEnv-compatible environment for training agents
to identify and block malicious bot traffic while preserving legitimate users.
"""

from typing import Dict, List, Any, Tuple, Set, Optional
from models import User, Observation, StepInfo


class APIRateLimitDefenderEnv:
    """
    API Rate Limit Defender Environment.
    
    The agent's goal is to block bots while minimizing false positives
    (blocking legitimate users). The agent receives observations that
    exclude the is_bot field, requiring it to infer bot status from
    other signals (rps, suspicious_pattern, tier).
    
    Actions:
        - block(user_id): Block a specific user
    
    Rewards:
        - +0.4 for blocking a bot
        - -0.7 for blocking a human (increased penalty for better precision)
        - Additional penalty tracked for blocking premium humans
        - +0.1 bonus if system_health > 0.8
    
    Episode ends when:
        - system_health <= 0
        - steps >= 20
    """

    # Constants
    MAX_STEPS: int = 20
    REWARD_BLOCK_BOT: float = 0.4
    REWARD_BLOCK_HUMAN: float = -0.7  # Increased penalty to reduce false positives
    REWARD_HEALTH_BONUS: float = 0.1
    PENALTY_INVALID_ACTION: float = -0.1
    PENALTY_ALREADY_BLOCKED: float = -0.1

    def __init__(self):
        """Initialize the environment."""
        self.users: Dict[str, User] = {}
        self.blocked_users: Set[str] = set()
        self.system_health: float = 1.0
        self.steps: int = 0
        self._initialized: bool = False

    def reset(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reset the environment with a new dataset.
        
        Args:
            dataset: List of user dictionaries containing all user attributes
                     including is_bot (ground truth for evaluation)
        
        Returns:
            Initial observation dictionary (excludes is_bot)
        """
        # Initialize users from dataset
        self.users = {}
        for user_data in dataset:
            user = User.from_dict(user_data)
            self.users[user.id] = user
        
        # Reset environment state
        self.blocked_users = set()
        self.system_health = 1.0
        self.steps = 0
        self._initialized = True
        
        return self._get_observation().to_dict()

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Action dictionary with format {"type": "block", "user_id": str}
        
        Returns:
            Tuple of (observation, reward, done, info)
        """
        if not self._initialized:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        if not isinstance(action, dict):
            action = {}
        
        self.steps += 1
        reward = 0.0
        premium_penalty_this_step = 0
        valid_action = False
        
        # Parse and validate action
        action_type = action.get("type", "")
        user_id = action.get("user_id", "")
        
        if action_type == "block":
            reward, premium_penalty_this_step, valid_action = self._handle_block_action(user_id)
        elif action_type == "noop":
            reward = 0.0
        else:
            # Invalid action type
            reward = self.PENALTY_INVALID_ACTION
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        # Update system health based on metrics
        total_users = len(self.users)
        if total_users > 0:
            self.system_health = max(0.0, 1.0 - ((metrics["fn"] + metrics["fp"]) / total_users))
        
        # Health bonus (only for valid actions)
        if valid_action and self.system_health > 0.8:
            reward += self.REWARD_HEALTH_BONUS
        
        # Check done condition
        done = self._is_done()
        
        # Build info dictionary
        info = StepInfo(
            tp=metrics["tp"],
            fp=metrics["fp"],
            fn=metrics["fn"],
            tn=metrics["tn"],
            premium_penalty=premium_penalty_this_step,
            blocked_ids=list(self.blocked_users)
        ).to_dict()
        
        # Get observation
        observation = self._get_observation().to_dict()
        
        return observation, reward, done, info

    def _handle_block_action(self, user_id: str) -> Tuple[float, int, bool]:
        """
        Handle a block action.
        
        Args:
            user_id: The ID of the user to block
        
        Returns:
            Tuple of (reward, premium_penalty_count, valid_action)
        """
        premium_penalty = 0
        
        # Check if user exists
        if user_id not in self.users:
            return self.PENALTY_INVALID_ACTION, 0, False
        
        # Check if already blocked
        if user_id in self.blocked_users:
            return self.PENALTY_ALREADY_BLOCKED, 0, False
        
        # Block the user
        self.blocked_users.add(user_id)
        user = self.users[user_id]
        
        # Calculate reward based on whether user is a bot
        if user.is_bot:
            # Correctly blocked a bot
            reward = self.REWARD_BLOCK_BOT
        else:
            # Incorrectly blocked a human
            reward = self.REWARD_BLOCK_HUMAN
            # Track premium penalty separately (do NOT double subtract)
            if user.tier == "premium":
                premium_penalty = 1
        
        return reward, premium_penalty, True

    def _calculate_metrics(self) -> Dict[str, int]:
        """
        Calculate classification metrics.
        
        Returns:
            Dictionary with tp, fp, fn, tn counts
        """
        tp = 0  # Bot AND blocked
        fp = 0  # Human AND blocked
        fn = 0  # Bot AND NOT blocked
        tn = 0  # Human AND NOT blocked
        
        for user_id, user in self.users.items():
            is_blocked = user_id in self.blocked_users
            
            if user.is_bot:
                if is_blocked:
                    tp += 1
                else:
                    fn += 1
            else:
                if is_blocked:
                    fp += 1
                else:
                    tn += 1
        
        return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}

    def _get_observation(self) -> Observation:
        """
        Build the current observation (excludes is_bot).
        
        Returns:
            Observation object with user data visible to agent
        """
        users_obs = [
            user.to_observation_dict() 
            for user in self.users.values()
        ]
        
        return Observation(
            users=users_obs,
            blocked_users=list(self.blocked_users),
            system_health=self.system_health
        )

    def _is_done(self) -> bool:
        """
        Check if the episode should end.
        
        Returns:
            True if episode is done, False otherwise
        """
        # Episode ends when system_health <= 0 OR steps >= MAX_STEPS
        return self.system_health <= 0 or self.steps >= self.MAX_STEPS

    def get_action_space(self) -> Dict[str, Any]:
        """
        Return the action space specification.
        
        Returns:
            Dictionary describing valid actions
        """
        return {
            "type": "block",
            "user_id": "string (valid user ID from observation)"
        }

    def get_observation_space(self) -> Dict[str, Any]:
        """
        Return the observation space specification.
        
        Returns:
            Dictionary describing observation structure
        """
        return {
            "users": [
                {
                    "id": "str",
                    "rps": "int",
                    "is_suspicious_pattern": "bool",
                    "tier": "str ('normal' | 'premium')"
                }
            ],
            "blocked_users": ["list of user ids"],
            "system_health": "float (0 to 1)"
        }


# Convenience function for creating environment
def make_env() -> APIRateLimitDefenderEnv:
    """
    Factory function to create a new environment instance.
    
    Returns:
        A new APIRateLimitDefenderEnv instance
    """
    return APIRateLimitDefenderEnv()
