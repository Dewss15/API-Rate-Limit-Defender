"""
models.py - Typed Data Contracts for OpenEnv Compliance

Using Pydantic v2 for strict type validation and serialization.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class UserObservation(BaseModel):
    """User data visible to the agent (excludes is_bot)."""
    id: str = Field(..., description="Unique user identifier")
    rps: int = Field(..., ge=0, description="Requests per second")
    is_suspicious_pattern: bool = Field(..., description="Behavioral anomaly flag")
    tier: Literal["normal", "premium"] = Field(..., description="User tier")


class Observation(BaseModel):
    """Complete observation returned to the agent."""
    users: List[UserObservation] = Field(..., description="List of users in the system")
    blocked_users: List[str] = Field(default_factory=list, description="Currently blocked user IDs")
    system_health: float = Field(..., ge=0.0, le=1.0, description="System health (0.0 to 1.0)")


class Action(BaseModel):
    """Action specification for the agent."""
    type: Literal["block", "noop"] = Field(..., description="Action type")
    user_id: Optional[str] = Field(None, description="User ID to block (required if type='block')")
    
    def to_env_action(self) -> dict:
        """Convert to environment-compatible action format."""
        return {
            "type": self.type,
            "user_id": self.user_id or "noop"
        }


class Reward(BaseModel):
    """Reward signal from environment."""
    reward: float = Field(..., description="Scalar reward value")


class StepResult(BaseModel):
    """Result of a single environment step."""
    observation: Observation
    reward: Reward
    done: bool
    info: dict


class TaskMetadata(BaseModel):
    """Metadata for a task."""
    name: str
    description: str
    difficulty: Literal["easy", "medium", "hard", "extreme"]
    dataset_fn: str = Field(..., description="Function name in data.py to load dataset")


class EpisodeLog(BaseModel):
    """Log entry for an episode step."""
    step: int
    action: dict
    reward: float
    done: bool


class FinalResult(BaseModel):
    """Final evaluation result."""
    final_score: float
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float
    system_health: float
    premium_penalty: int
