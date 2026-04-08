"""
main.py - Production Agent Integration Bridge for Meta OpenEnv Submission

This script connects trained agents to the API Rate Limit Defender environment
with strict Meta-compliant logging and multi-task execution.
"""

import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Import environment and models
from environment import APIRateLimitDefenderEnv
from openenv_models import Action, Observation, UserObservation
from grader import Grader
from data import get_easy_data, get_medium_data, get_winning_data


# ============================================================================
# TASK CONFIGURATION
# ============================================================================

@dataclass
class TaskConfig:
    """Configuration for each evaluation task."""
    task_id: str
    task_name: str
    dataset_fn: callable
    seed: Optional[int] = None


TASKS = [
    TaskConfig(
        task_id="easy-triage",
        task_name="Easy Triage",
        dataset_fn=get_easy_data,
        seed=None
    ),
    TaskConfig(
        task_id="behavioral-analysis",
        task_name="Behavioral Analysis",
        dataset_fn=get_medium_data,
        seed=None
    ),
    TaskConfig(
        task_id="adversarial-defense",
        task_name="Adversarial Defense",
        dataset_fn=get_winning_data,
        seed=42  # Seed for generalization testing
    )
]


# ============================================================================
# AGENT INTERFACE
# ============================================================================

class BaseAgent:
    """Base interface for all agents."""
    
    def get_name(self) -> str:
        """Return agent name for logging."""
        raise NotImplementedError
    
    def select_action(self, observation: Dict[str, Any]) -> Action:
        """
        Select an action based on observation.
        
        Args:
            observation: Dict with keys 'users', 'blocked_users', 'system_health'
            
        Returns:
            Action: Pydantic Action model with type and user_id
        """
        raise NotImplementedError
    
    def reset(self):
        """Reset agent state between episodes (optional)."""
        pass


class HeuristicAgent(BaseAgent):
    """
    Baseline heuristic agent for testing and comparison.
    
    Strategy: Block users with high RPS + suspicious pattern, protect premium.
    """
    
    def __init__(self, rps_threshold: int = 50, name: str = "HeuristicAgent"):
        self.rps_threshold = rps_threshold
        self.name = name
    
    def get_name(self) -> str:
        return self.name
    
    def select_action(self, observation: Dict[str, Any]) -> Action:
        """Select action using heuristic rules."""
        users = observation.get("users", [])
        blocked_users = set(observation.get("blocked_users", []))
        
        for user in users:
            user_id = user["id"]
            
            # Skip already blocked users
            if user_id in blocked_users:
                continue
            
            # NEVER block premium (hard constraint)
            if user["tier"] == "premium":
                continue
            
            # Block if high RPS AND suspicious pattern
            if user["rps"] >= self.rps_threshold and user["is_suspicious_pattern"]:
                return Action(type="block", user_id=user_id)
        
        # No action needed
        return Action(type="noop", user_id=None)


class LLMAgent(BaseAgent):
    """
    LLM-based agent using OpenAI-compatible API.
    
    Requires environment variables:
    - API_BASE_URL: LLM endpoint
    - MODEL_NAME: Model identifier
    - HF_TOKEN or OPENAI_API_KEY: Authentication token
    """
    
    def __init__(self, name: str = "LLM-Agent"):
        try:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN", "dummy-key")
            api_base = os.getenv("API_BASE_URL", "http://localhost:8000/v1")
            self.model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
            
            self.client = OpenAI(api_key=api_key, base_url=api_base)
            self.name = name
            
        except ImportError:
            raise RuntimeError("OpenAI package not installed. Run: pip install openai")
    
    def get_name(self) -> str:
        return f"{self.name}-{self.model_name}"
    
    def select_action(self, observation: Dict[str, Any]) -> Action:
        """Select action using LLM reasoning."""
        users = observation.get("users", [])
        blocked_users = set(observation.get("blocked_users", []))
        system_health = observation.get("system_health", 1.0)
        
        # Build prompt
        prompt = self._build_prompt(users, blocked_users, system_health)
        
        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert cybersecurity agent detecting bot traffic."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic
                max_tokens=50
            )
            
            # Parse response
            action_text = response.choices[0].message.content.strip()
            return self._parse_llm_response(action_text, users, blocked_users)
            
        except Exception as e:
            print(f"[WARNING] LLM error: {e}, defaulting to noop", file=sys.stderr)
            return Action(type="noop", user_id=None)
    
    def _build_prompt(self, users: List[Dict], blocked_users: set, system_health: float) -> str:
        """Build prompt for LLM."""
        prompt = f"System Health: {system_health:.2f}\n\n"
        prompt += "Users:\n"
        
        for user in users:
            if user["id"] in blocked_users:
                continue
            
            prompt += f"- {user['id']}: RPS={user['rps']}, "
            prompt += f"Suspicious={user['is_suspicious_pattern']}, "
            prompt += f"Tier={user['tier']}\n"
        
        prompt += "\nRules:\n"
        prompt += "1. NEVER block premium users\n"
        prompt += "2. Block bots (high RPS + suspicious pattern)\n"
        prompt += "3. Protect humans (low RPS or no suspicious pattern)\n\n"
        prompt += "Output format: 'block USER_ID' or 'noop'\n"
        prompt += "Your decision:"
        
        return prompt
    
    def _parse_llm_response(self, text: str, users: List[Dict], blocked_users: set) -> Action:
        """Parse LLM response into Action."""
        text_lower = text.lower()
        
        # Check for block action
        if "block" in text_lower:
            for user in users:
                user_id = user["id"]
                if user_id in text and user_id not in blocked_users:
                    # Validate: never block premium
                    if user["tier"] != "premium":
                        return Action(type="block", user_id=user_id)
        
        # Default to noop
        return Action(type="noop", user_id=None)


class TrainedModelAgent(BaseAgent):
    """
    Wrapper for Sakshi's trained PyTorch/TensorFlow model.
    
    Usage:
        agent = TrainedModelAgent(model_path="model.pt")
    """
    
    def __init__(self, model_path: str, name: str = "TrainedModel"):
        self.model_path = model_path
        self.name = name
        self.model = self._load_model(model_path)
    
    def _load_model(self, path: str):
        """Load trained model from file."""
        try:
            import torch
            model = torch.load(path, map_location="cpu")
            model.eval()
            return model
        except Exception as e:
            print(f"[WARNING] Failed to load model from {path}: {e}", file=sys.stderr)
            return None
    
    def get_name(self) -> str:
        return self.name
    
    def select_action(self, observation: Dict[str, Any]) -> Action:
        """Select action using trained model."""
        if self.model is None:
            return Action(type="noop", user_id=None)
        
        users = observation.get("users", [])
        blocked_users = set(observation.get("blocked_users", []))
        
        # Extract features for each user
        for user in users:
            if user["id"] in blocked_users:
                continue
            
            # Never block premium
            if user["tier"] == "premium":
                continue
            
            # Get model prediction
            features = self._extract_features(user, observation)
            block_prob = self._predict(features)
            
            # Threshold decision
            if block_prob > 0.7:
                return Action(type="block", user_id=user["id"])
        
        return Action(type="noop", user_id=None)
    
    def _extract_features(self, user: Dict, observation: Dict) -> Any:
        """Extract features for model input."""
        import torch
        
        # Example feature extraction (customize for your model)
        features = [
            user["rps"] / 100.0,  # Normalized RPS
            float(user["is_suspicious_pattern"]),
            float(user["tier"] == "premium"),
            observation["system_health"],
            len(observation["blocked_users"]) / max(len(observation["users"]), 1)
        ]
        
        return torch.tensor(features, dtype=torch.float32)
    
    def _predict(self, features) -> float:
        """Get prediction from model."""
        try:
            import torch
            with torch.no_grad():
                output = self.model(features)
                # Assume output is probability or logit
                prob = torch.sigmoid(output).item() if output.dim() == 0 else output[0].item()
                return prob
        except Exception as e:
            print(f"[WARNING] Model prediction error: {e}", file=sys.stderr)
            return 0.0


# ============================================================================
# EXECUTION ENGINE
# ============================================================================

class ExecutionEngine:
    """Manages multi-task execution with strict logging."""
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.env = APIRateLimitDefenderEnv()
        self.grader = Grader()
    
    def run_task(self, task: TaskConfig) -> Dict[str, Any]:
        """
        Run a single task with the agent.
        
        Args:
            task: TaskConfig with dataset and metadata
            
        Returns:
            Dict with results and metrics
        """
        # Load dataset
        dataset = task.dataset_fn()
        
        # Log task start
        print(f"[START] task={task.task_id} env=api-defender model={self.agent.get_name()}")
        sys.stdout.flush()
        
        # Reset environment and agent
        obs_dict = self.env.reset(dataset)
        self.agent.reset()
        
        # Initialize tracking
        done = False
        step_num = 0
        rewards = []
        error_log = []
        
        # Execute episode (max 20 steps)
        while not done and step_num < APIRateLimitDefenderEnv.MAX_STEPS:
            step_num += 1
            
            try:
                # Agent selects action
                action = self.agent.select_action(obs_dict)
                
                # Validate action
                validated_action, error_msg = self._validate_action(action, obs_dict)
                
                # Execute in environment
                obs_dict, reward, done, info = self.env.step(validated_action.to_env_action())
                
                # Track results
                rewards.append(reward)
                if error_msg:
                    error_log.append(error_msg)
                
                # Log step
                action_str = f"{validated_action.type}"
                if validated_action.user_id:
                    action_str += f"({validated_action.user_id})"
                
                error_str = error_msg if error_msg else "null"
                print(f"[STEP] step={step_num} action={action_str} reward={reward:.2f} done={done} error={error_str}")
                sys.stdout.flush()
                
            except Exception as e:
                error_msg = f"Exception: {str(e)}"
                error_log.append(error_msg)
                print(f"[STEP] step={step_num} action=noop reward=0.00 done={done} error={error_msg}")
                sys.stdout.flush()
                rewards.append(0.0)
                continue
        
        # Grade final performance
        blocked_ids = list(info.get("blocked_ids", []))
        grade_results = self.grader.grade(blocked_ids, dataset)
        
        # Format rewards string
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])
        
        # Log task end
        success = grade_results["score"] > 0.0
        print(f"[END] success={str(success).lower()} steps={step_num} score={grade_results['score']:.3f} rewards={rewards_str}")
        sys.stdout.flush()
        
        return {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "success": success,
            "steps": step_num,
            "rewards": rewards,
            "total_reward": sum(rewards),
            "grade_results": grade_results,
            "error_log": error_log
        }
    
    def _validate_action(self, action: Action, observation: Dict[str, Any]) -> Tuple[Action, Optional[str]]:
        """
        Validate action and return corrected version with error message.
        
        Args:
            action: Agent's selected action
            observation: Current observation
            
        Returns:
            Tuple of (validated_action, error_message)
        """
        error_msg = None
        
        # If noop, always valid
        if action.type == "noop":
            return action, error_msg
        
        # If block, validate user_id
        if action.type == "block":
            if not action.user_id:
                error_msg = "Block action missing user_id"
                return Action(type="noop", user_id=None), error_msg
            
            # Check if user exists in current observation
            valid_user_ids = {user["id"] for user in observation.get("users", [])}
            if action.user_id not in valid_user_ids:
                error_msg = f"Invalid user_id: {action.user_id}"
                return Action(type="noop", user_id=None), error_msg
            
            # Check if already blocked
            if action.user_id in observation.get("blocked_users", []):
                error_msg = f"User {action.user_id} already blocked"
                return Action(type="noop", user_id=None), error_msg
        
        return action, error_msg
    
    def run_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Run all tasks and return results.
        
        Returns:
            List of result dicts for each task
        """
        results = []
        
        for task in TASKS:
            print()  # Blank line between tasks
            result = self.run_task(task)
            results.append(result)
        
        return results
    
    def print_final_summary(self, results: List[Dict[str, Any]]):
        """Print final summary across all tasks."""
        print("\n" + "="*70)
        print("FINAL_SUMMARY")
        print("="*70)
        
        for result in results:
            grade = result["grade_results"]
            print(f"\nTask: {result['task_name']} ({result['task_id']})")
            print(f"  Success:        {result['success']}")
            print(f"  Steps:          {result['steps']}")
            print(f"  Final Score:    {grade['score']:.3f}")
            print(f"  F1 Score:       {grade['f1']:.3f}")
            print(f"  Precision:      {grade['precision']:.3f}")
            print(f"  Recall:         {grade['recall']:.3f}")
            print(f"  System Health:  {grade['system_health']:.1%}")
            print(f"  TP/FP/FN/TN:    {grade['TP']}/{grade['FP']}/{grade['FN']}/{grade['TN']}")
            print(f"  Premium Blocked: {grade['premium_penalty']}")
            print(f"  Total Reward:   {result['total_reward']:.2f}")
            
            if result["error_log"]:
                print(f"  Errors:         {len(result['error_log'])}")
        
        # Aggregate metrics
        avg_score = sum(r["grade_results"]["score"] for r in results) / len(results)
        avg_precision = sum(r["grade_results"]["precision"] for r in results) / len(results)
        avg_system_health = sum(r["grade_results"]["system_health"] for r in results) / len(results)
        total_premium_blocked = sum(r["grade_results"]["premium_penalty"] for r in results)
        
        print(f"\n{'='*70}")
        print(f"AGGREGATE METRICS")
        print(f"{'='*70}")
        print(f"Average Score:         {avg_score:.3f}")
        print(f"Average Precision:     {avg_precision:.3f}")
        print(f"Average System Health: {avg_system_health:.1%}")
        print(f"Total Premium Blocked: {total_premium_blocked}")
        
        # Pass/Fail criteria
        print(f"\n{'='*70}")
        print(f"VALIDATION")
        print(f"{'='*70}")
        print(f"✅ No premium blocked:     {total_premium_blocked == 0}")
        print(f"✅ Avg F1 > 0.70:          {all(r['grade_results']['f1'] > 0.70 for r in results)}")
        print(f"✅ Avg health > 80%:       {avg_system_health > 0.80}")
        print(f"✅ All tasks completed:    {all(r['success'] for r in results)}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main execution entry point."""
    print("="*70)
    print("API Rate Limit Defender - Agent Integration Bridge")
    print("="*70)
    
    # ========================================================================
    # AGENT SELECTION
    # ========================================================================
    # Import and use HardDefenderAgent (Risk-based rule system - F1=0.791)
    from hard_defender_agent import HardDefenderAgent
    
    agent = HardDefenderAgent(block_threshold=2.5)
    
    # Other agent options (commented out):
    # agent = HeuristicAgent(rps_threshold=50, name="Heuristic-v1")
    # agent = LLMAgent(name="GPT-Defender")
    # agent = TrainedModelAgent(model_path="best_model.pt", name="DQN-v1")
    
    # ========================================================================
    
    print(f"Agent: {agent.get_name()}")
    print("="*70)
    
    # Create execution engine
    engine = ExecutionEngine(agent)
    
    # Run all tasks
    results = engine.run_all_tasks()
    
    # Print final summary
    engine.print_final_summary(results)
    
    print("\n" + "="*70)
    print("Execution complete!")
    print("="*70)


if __name__ == "__main__":
    main()
