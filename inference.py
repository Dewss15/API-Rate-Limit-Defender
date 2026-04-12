"""
inference.py - OpenEnv Inference Entry Point

CRITICAL: This file must produce EXACT bracketed format for grading.
Output format:
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import os
import sys
from typing import Dict, Any, List, Optional
from openai import OpenAI

# Avoid UnicodeEncodeError on Windows consoles (cp1252) when printing emojis.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from environment import make_env
from data import get_easy_data, get_medium_data, get_winning_data
from grader import Grader
from openenv_models import Action, Observation, UserObservation


class LLMAgent:
    """
    LLM-powered agent using OpenAI-compatible API.
    
    Configured via environment variables:
    - API_BASE_URL: Base URL for API (e.g., Hugging Face Inference)
    - MODEL_NAME: Model identifier
    - HF_TOKEN: Authentication token
    """
    
    def __init__(self):
        """Initialize LLM client from environment variables."""
        self.api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
        self.model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
        self.hf_token = os.environ.get("HF_TOKEN", "")
        
        # Initialize OpenAI-compatible client
        self.client = OpenAI(
            base_url=self.api_base,
            api_key=self.hf_token or "dummy-key"
        )
        
        self.system_prompt = """You are an expert cybersecurity agent tasked with blocking malicious bots while protecting legitimate users.

You receive observations with:
- users: List of users with id, rps (requests/sec), is_suspicious_pattern (bool), tier ("normal" or "premium")
- blocked_users: Already blocked user IDs
- system_health: Current health (0.0 to 1.0)

Your goal:
- Block bots (you'll get positive reward)
- Avoid blocking humans (negative reward)
- NEVER block premium users (massive penalty)
- Maintain system_health > 0.8

You must respond with ONLY a JSON action:
{"type": "block", "user_id": "U42"}
or
{"type": "noop", "user_id": null}

Rules:
- High RPS (>50) + suspicious pattern → likely bot
- Premium users should almost never be blocked
- Don't re-block already blocked users
- If unsure, use "noop" to avoid penalties

Respond with ONLY the JSON action, no explanation."""
    
    def select_action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select action using LLM.
        
        Args:
            observation: Current environment observation
            
        Returns:
            Action dict: {"type": "block"|"noop", "user_id": str|None}
        """
        # Format observation for LLM
        obs_text = json.dumps(observation, indent=2)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Current observation:\n{obs_text}\n\nWhat action should I take?"}
                ],
                temperature=0.0,  # Deterministic
                max_tokens=100
            )
            
            # Parse LLM response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "{" in content:
                json_start = content.index("{")
                json_end = content.rindex("}") + 1
                action_json = content[json_start:json_end]
                action = json.loads(action_json)
                
                # Validate action format
                if "type" not in action:
                    action = {"type": "noop", "user_id": None}
                if action["type"] == "block" and "user_id" not in action:
                    action = {"type": "noop", "user_id": None}
                
                return action
            else:
                # Fallback: no op
                return {"type": "noop", "user_id": None}
                
        except Exception as e:
            print(f"⚠️  LLM error: {e}, using heuristic fallback", flush=True)
            return self._heuristic_fallback(observation)
    
    def _heuristic_fallback(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback heuristic if LLM fails."""
        for user in observation["users"]:
            if user["id"] in observation["blocked_users"]:
                continue
            if user["tier"] == "premium":
                continue
            if user["rps"] > 50 and user["is_suspicious_pattern"]:
                return {"type": "block", "user_id": user["id"]}
        return {"type": "noop", "user_id": None}


class HeuristicAgent:
    """
    Baseline heuristic agent (used when LLM is not available).
    """
    
    def __init__(self, rps_threshold: int = 50):
        """
        Initialize heuristic agent.
        
        Args:
            rps_threshold: RPS threshold for blocking
        """
        self.rps_threshold = rps_threshold
    
    def select_action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select action using heuristic.
        
        Args:
            observation: Current environment observation
            
        Returns:
            Action dict
        """
        for user in observation["users"]:
            # Skip already blocked
            if user["id"] in observation["blocked_users"]:
                continue
            
            # Never block premium
            if user["tier"] == "premium":
                continue
            
            # Block if both conditions met
            if user["rps"] > self.rps_threshold and user["is_suspicious_pattern"]:
                return {"type": "block", "user_id": user["id"]}
        
        return {"type": "noop", "user_id": None}


def format_action(action: Dict[str, Any]) -> str:
    """Format action dict as simple string."""
    if action.get("type") == "block":
        user_id = action.get("user_id", "unknown")
        return f"block({user_id})"
    else:
        return "noop"


def log_start(task: str, env: str, model: str) -> None:
    """Print [START] line in official format."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action_str: str, reward: float, done: bool, error: Optional[str]) -> None:
    """Print [STEP] line in official format."""
    done_str = str(done).lower()
    error_str = error if error else "null"
    print(
        f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_str} error={error_str}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Print [END] line in official format."""
    success_str = str(success).lower()
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={success_str} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def run_task(task_name: str, dataset_fn, agent, grader: Grader, benchmark: str = "api-defender") -> Dict[str, Any]:
    """
    Run a single task and produce official bracketed logs.
    
    Args:
        task_name: Task identifier (easy-triage, behavioral-analysis, adversarial-defense)
        dataset_fn: Function to load dataset
        agent: Agent instance
        grader: Grader instance
        benchmark: Environment name
        
    Returns:
        Final results dict
    """
    # Get agent model name
    agent_model = agent.get_name()
    
    # Print START log (official format)
    log_start(task=task_name, env=benchmark, model=agent_model)
    
    # Initialize environment
    env = make_env()
    data = dataset_fn()
    obs = env.reset(data)
    
    done = False
    step = 0
    rewards = []
    error = None
    
    # Run episode (max 20 steps)
    while not done and step < 20:
        # Agent selects action
        try:
            action = agent.select_action(obs)
        except Exception as e:
            error = f"Agent error: {str(e)}"
            action = {"type": "noop", "user_id": None}
        
        # Environment step
        try:
            obs, reward, done, info = env.step(action)
            rewards.append(reward)
        except Exception as e:
            error = f"Environment error: {str(e)}"
            reward = 0.0
            rewards.append(reward)
            done = True
        
        step += 1
        
        # Format and log action
        action_str = format_action(action)
        log_step(step=step, action_str=action_str, reward=reward, done=done, error=error)
    
    # Grade final result
    try:
        results = grader.grade(info.get("blocked_ids", []), data)
        score = results["f1"]  # Use F1 as primary metric (normalized 0-1)
        success = score >= 0.70  # Judging threshold
    except Exception as e:
        error = f"Grading error: {str(e)}"
        score = 0.0
        success = False
        results = {}
    
    # Ensure score is in [0, 1] range
    score = max(0.0, min(1.0, score))
    
    # Print END log (official format)
    log_end(success=success, steps=step, score=score, rewards=rewards)
    
    return results


def main():
    """
    Main inference entry point.
    
    Runs all three tasks in sequence:
    1. easy-triage
    2. behavioral-analysis
    3. adversarial-defense
    """
    # Initialize grader
    grader = Grader()
    
    # Use HardDefenderAgent (F1=0.791 winning agent)
    from hard_defender_agent import HardDefenderAgent
    agent = HardDefenderAgent(block_threshold=2.5)
    
    # Define tasks
    tasks = [
        ("easy-triage", get_easy_data),
        ("behavioral-analysis", get_medium_data),
        ("adversarial-defense", get_winning_data)
    ]
    
    # Run all tasks
    all_results = []
    
    for task_name, dataset_fn in tasks:
        try:
            results = run_task(
                task_name=task_name,
                dataset_fn=dataset_fn,
                agent=agent,
                grader=grader,
                benchmark="api-defender"
            )
            all_results.append({
                "task": task_name,
                "f1": results.get("f1", 0.0),
                "score": results.get("score", 0.0)
            })
        except Exception as e:
            print(f"[ERROR] Task {task_name} failed: {str(e)}", file=sys.stderr, flush=True)
            all_results.append({
                "task": task_name,
                "f1": 0.0,
                "score": 0.0,
                "error": str(e)
            })


if __name__ == "__main__":
    main()
