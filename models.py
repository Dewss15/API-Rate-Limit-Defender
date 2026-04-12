"""
models.py - Data models for API Rate Limit Defender

Defines the User class and observation structures for the RL environment.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class User:
    """
    Represents a user making API requests.
    
    Attributes:
        id: Unique identifier for the user
        rps: Requests per second from this user
        is_suspicious_pattern: Whether the user exhibits suspicious behavior patterns
        tier: User tier - either "normal" or "premium"
        is_bot: Whether the user is a bot (HIDDEN FROM AGENT - used only for evaluation)
    """
    id: str
    rps: int
    is_suspicious_pattern: bool
    tier: str  # "normal" | "premium"
    is_bot: bool  # HIDDEN FROM AGENT - ground truth for evaluation

    def __post_init__(self):
        """Validate user attributes after initialization."""
        if self.tier not in ("normal", "premium"):
            raise ValueError(f"tier must be 'normal' or 'premium', got '{self.tier}'")
        if self.rps < 0:
            raise ValueError(f"rps must be non-negative, got {self.rps}")

    def to_observation_dict(self) -> Dict[str, Any]:
        """
        Convert user to observation format (excludes is_bot).
        
        Returns:
            Dictionary with user attributes visible to the agent.
        """
        return {
            "id": self.id,
            "rps": self.rps,
            "is_suspicious_pattern": self.is_suspicious_pattern,
            "tier": self.tier
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """
        Create a User instance from a dictionary.
        
        Args:
            data: Dictionary containing user attributes
            
        Returns:
            User instance
        """
        return cls(
            id=str(data["id"]),
            rps=int(data["rps"]),
            is_suspicious_pattern=bool(data["is_suspicious_pattern"]),
            tier=str(data["tier"]),
            is_bot=bool(data["is_bot"])
        )


@dataclass
class Observation:
    """
    Observation structure returned to the agent.
    
    Attributes:
        users: List of user dictionaries (without is_bot)
        blocked_users: List of blocked user IDs
        system_health: Current system health (0 to 1)
    """
    users: List[Dict[str, Any]]
    blocked_users: List[str]
    system_health: float

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert observation to dictionary format.
        
        Returns:
            Dictionary representation of the observation.
        """
        return {
            "users": self.users,
            "blocked_users": self.blocked_users,
            "system_health": self.system_health
        }


@dataclass
class StepInfo:
    """
    Information dictionary returned with each step.
    
    Attributes:
        tp: True positives (bots correctly blocked)
        fp: False positives (humans incorrectly blocked)
        fn: False negatives (bots not blocked)
        tn: True negatives (humans not blocked)
        premium_penalty: Count of premium humans blocked
        blocked_ids: List of all blocked user IDs
    """
    tp: int
    fp: int
    fn: int
    tn: int
    premium_penalty: int
    blocked_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert step info to dictionary format.
        
        Returns:
            Dictionary representation matching evaluator expectations.
        """
        return {
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "tn": self.tn,
            "premium_penalty": self.premium_penalty,
            "blocked_ids": self.blocked_ids
        }