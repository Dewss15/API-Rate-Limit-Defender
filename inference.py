"""
inference.py - OpenEnv Inference Entry Point

CRITICAL: This file must produce EXACT JSON log format for grading.
Any deviation will cause validation failure.
"""

import os
import json
from typing import Dict, Any, List
from openai import OpenAI

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


def run_task(task_name: str, dataset_fn, agent, grader: Grader) -> Dict[str, Any]:
    """
    Run a single task and produce STRICT JSON logs.
    
    Args:
        task_name: Task identifier
        dataset_fn: Function to load dataset
        agent: Agent instance
        grader: Grader instance
        
    Returns:
        Final results dict
    """
    # Print START log (EXACT format required)
    print(json.dumps({"event": "START", "task": task_name}), flush=True)
    
    # Initialize environment
    env = make_env()
    data = dataset_fn()
    obs = env.reset(data)
    
    done = False
    step = 0
    total_reward = 0.0
    
    # Run episode
    while not done and step < 20:
        # Agent selects action
        action = agent.select_action(obs)
        
        # Environment step
        obs, reward, done, info = env.step(action)
        total_reward += reward
        step += 1
        
        # Print STEP log (EXACT format required)
        step_log = {
            "event": "STEP",
            "step": step,
            "action": action,
            "reward": float(reward),
            "done": done
        }
        print(json.dumps(step_log), flush=True)
    
    # Grade final result
    results = grader.grade(info["blocked_ids"], data)
    
    # Print END log (EXACT format required)
    end_log = {
        "event": "END",
        "task": task_name,
        "final_score": float(results["score"]),
        "tp": int(results["TP"]),
        "fp": int(results["FP"]),
        "fn": int(results["FN"]),
        "precision": float(results["precision"]),
        "recall": float(results["recall"]),
        "f1": float(results["f1"]),
        "system_health": float(results["system_health"]),
        "premium_penalty": int(results["premium_penalty"]),
        "total_reward": float(total_reward),
        "steps": step
    }
    print(json.dumps(end_log), flush=True)
    
    return results


def main():
    """
    Main inference entry point.
    
    Runs all three tasks in sequence:
    1. easy-triage
    2. behavioral-analysis
    3. adversarial-defense
    """
    print(json.dumps({"event": "INIT", "message": "Starting OpenEnv inference"}), flush=True)
    
    # Initialize grader
    grader = Grader()
    
    # Choose agent based on environment
    use_llm = os.environ.get("USE_LLM", "false").lower() == "true"
    
    if use_llm:
        print(json.dumps({"event": "INFO", "agent": "LLM", "model": os.environ.get("MODEL_NAME", "unknown")}), flush=True)
        agent = LLMAgent()
    else:
        print(json.dumps({"event": "INFO", "agent": "Heuristic"}), flush=True)
        agent = HeuristicAgent(rps_threshold=50)
    
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
            results = run_task(task_name, dataset_fn, agent, grader)
            all_results.append({
                "task": task_name,
                "score": results["score"],
                "f1": results["f1"]
            })
        except Exception as e:
            error_log = {
                "event": "ERROR",
                "task": task_name,
                "error": str(e)
            }
            print(json.dumps(error_log), flush=True)
            all_results.append({
                "task": task_name,
                "score": 0.0,
                "f1": 0.0,
                "error": str(e)
            })
    
    # Print final summary
    summary = {
        "event": "SUMMARY",
        "tasks": all_results,
        "average_score": sum(r["score"] for r in all_results) / len(all_results) if all_results else 0.0
    }
    print(json.dumps(summary), flush=True)
    
    print(json.dumps({"event": "COMPLETE"}), flush=True)


if __name__ == "__main__":
    main()
